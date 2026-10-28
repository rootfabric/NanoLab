"""FLOW-R1 regression and negative controls; no scientific engine invocation."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from harness import operations, work_events, work_cli, batch_validate, review_impact, resource_plan
from harness.contracts import check_consistency


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


class GitCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.git('init', '-q')
        self.git('config', 'user.name', 'FLOW Test')
        self.git('config', 'user.email', 'flow-test@example.invalid')
        (self.root / 'marker.txt').write_text('base\n')
        self.base = self.commit()

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root, stderr=subprocess.PIPE).decode().strip()

    def commit(self):
        self.git('add', '.')
        self.git('commit', '-qm', 'test fixture')
        return self.git('rev-parse', 'HEAD')


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.plan = {'operational_task_directory': 'project/operations', 'tasks': [
            {'id': 'NL5-002', 'title': 'science', 'depends_on': ['NL5-001']}]}
        self.state = {'next_work_order': 'NL5-002', 'task_status': {'NL5-001': 'ACCEPTED', 'NL5-002': 'WAITING_HUMAN'}}
        self.card = {'schema_version': 1, 'id': 'PREP-R1', 'title': 'prep', 'track': 'NL7_PREP',
                     'status': 'READY', 'actor': 'IMPLEMENTER', 'priority': 10, 'depends_on': [],
                     'blockers': [], 'resume_condition': '', 'next_action': 'get real input',
                     'evidence_refs': [], 'updated_at_utc': '2026-10-28T03:20:00Z',
                     'claim_class': 'C0_SOFTWARE_ONLY', 'scientific_runs_allowed': False}
        self.path = self.root / 'project/operations/PREP-R1.json'
        write_json(self.path, self.card)

    def inspect(self):
        return operations.load_tasks(self.root, self.plan, self.state)

    def test_waiting_human_is_not_dispatchable_and_c0_is_available(self):
        data = self.inspect()
        self.assertTrue(data['ok'], data['errors'])
        route = operations.route(self.state, self.plan, data['tasks'])
        self.assertFalse(route['dispatchable'])
        self.assertFalse(route['execution_authorized'])
        self.assertEqual(route['next_actor'], 'HUMAN')
        self.assertTrue(route['human_decision_required'])
        self.assertEqual(route['parallel_ready_work'][0]['id'], 'PREP-R1')

    def test_planned_science_not_ready_even_with_accepted_dependencies(self):
        self.state['task_status']['NL5-002'] = 'PLANNED'
        self.assertFalse(operations.route(self.state, self.plan, [])['dispatchable'])

    def test_unmet_scientific_dependency_prevents_dispatch(self):
        self.state['task_status'].update({'NL5-002': 'READY', 'NL5-001': 'PLANNED'})
        route = operations.route(self.state, self.plan, [])
        self.assertFalse(route['dispatchable'])
        self.assertEqual(route['unmet_dependencies'], ['NL5-001'])

    def test_unknown_status_rejected(self):
        self.card['status'] = 'GREEN_ENOUGH'
        write_json(self.path, self.card)
        self.assertFalse(self.inspect()['ok'])

    def test_ready_with_blocker_rejected(self):
        self.card['blockers'] = ['no inputs']
        write_json(self.path, self.card)
        self.assertFalse(self.inspect()['ok'])

    def test_science_permission_cannot_be_set_in_card(self):
        for value in (True, 0, 'false'):
            with self.subTest(value=value):
                self.card['scientific_runs_allowed'] = value
                write_json(self.path, self.card)
                self.assertFalse(self.inspect()['ok'])

    def test_c1_card_rejected(self):
        self.card['claim_class'] = 'C1_COMPUTATIONAL_REPRODUCTION'
        write_json(self.path, self.card)
        self.assertFalse(self.inspect()['ok'])

    def test_blocker_requires_resume_condition(self):
        self.card['status'] = 'BLOCKED_SOURCE'
        write_json(self.path, self.card)
        self.assertFalse(self.inspect()['ok'])

    def test_unknown_dependency_rejected(self):
        self.card['depends_on'] = ['MISSING']
        write_json(self.path, self.card)
        self.assertFalse(self.inspect()['ok'])

    def test_cycle_rejected(self):
        self.card['depends_on'] = ['PREP-R1']
        write_json(self.path, self.card)
        self.assertFalse(self.inspect()['ok'])

    def test_ready_with_unfinished_dependency_rejected(self):
        self.card['depends_on'] = ['NL5-002']
        write_json(self.path, self.card)
        self.assertFalse(self.inspect()['ok'])

    def test_duplicate_json_keys_rejected(self):
        self.path.write_text('{"id":"X","id":"Y"}')
        self.assertFalse(self.inspect()['ok'])

    def test_empty_registry_rejected(self):
        self.path.unlink()
        self.assertFalse(self.inspect()['ok'])

    def test_filename_mismatch_rejected(self):
        self.card['id'] = 'OTHER'
        write_json(self.path, self.card)
        self.assertFalse(self.inspect()['ok'])

    def test_boolean_priority_rejected(self):
        self.card['priority'] = True
        write_json(self.path, self.card)
        self.assertFalse(self.inspect()['ok'])

    def test_current_repository_consistency_and_scientific_gate(self):
        result = check_consistency(ROOT)
        self.assertTrue(result['ok'], result['errors'])
        self.assertFalse(result['frontier_readiness']['dispatchable'])
        self.assertTrue(result['frontier_readiness']['human_decision_required'])

    def test_markdown_view_does_not_write_shared_queue(self):
        before = self.path.read_bytes()
        text = operations.render_markdown(self.inspect()['tasks'])
        self.assertIn('PREP-R1', text)
        self.assertEqual(self.path.read_bytes(), before)


class EventWriterTests(GitCase):
    def setUp(self):
        super().setUp()
        self.target = self.root / 'docs/work/executions/EX-FLOW-TEST-R1'

    def start(self):
        return work_events.start(self.root, self.target, work_order='WO-FLOW-TEST-R1', checkpoint='NL5',
                                 risk='MEDIUM', allowed_paths=['scripts/demo.py'], sha=self.base,
                                 summary='test start', next_action='test')

    def append(self, kind='CONTINUATION_CHECKPOINT', role='IMPLEMENTER', sha=None):
        return work_events.append(self.root, self.target, kind=kind, role=role, sha=sha or self.base,
                                  summary='test event')

    def test_start_record_finish_preserves_start_and_cannot_self_accept(self):
        self.assertTrue(self.start()['ok'])
        first = self.target / 'events/0001-work-order-started.json'
        before = first.read_bytes()
        self.append('VALIDATION_RECORDED')
        (self.target / 'summary.md').write_text('test handoff')
        result = self.append('HANDOFF_COMPLETED')
        self.assertTrue(result['ok'])
        self.assertEqual(result['effective_status'], 'HANDOFF_READY')
        self.assertNotEqual(result['status'], 'ACCEPTED')
        self.assertEqual(before, first.read_bytes())

    def test_equal_real_timestamps_are_valid_under_sequence_v1(self):
        with patch.object(work_events, 'utc_now', return_value='2026-10-28T03:20:00.000000Z'):
            self.start()
            self.append()
            self.assertTrue(self.append()['ok'])

    def test_real_midnight_is_valid_for_new_c0_profile(self):
        with patch.object(work_events, 'utc_now', return_value='2026-10-28T00:00:00.000000Z'):
            self.assertTrue(self.start()['ok'])

    def test_backwards_clock_rejected_without_partial_event(self):
        with patch.object(work_events, 'utc_now', return_value='2026-10-28T03:20:00Z'):
            self.start()
        with patch.object(work_events, 'utc_now', return_value='2026-10-28T03:19:59Z'):
            with self.assertRaises(ValueError):
                self.append()
        self.assertEqual(len(list((self.target / 'events').glob('*.json'))), 1)

    def test_duplicate_start_does_not_overwrite(self):
        self.start()
        before = (self.target / 'passport.json').read_bytes()
        with self.assertRaises(ValueError):
            self.start()
        self.assertEqual((self.target / 'passport.json').read_bytes(), before)

    def test_unknown_event_is_rejected(self):
        self.start()
        with self.assertRaises(ValueError):
            self.append('REVIEW_PASS')
        self.assertEqual(len(list((self.target / 'events').glob('*.json'))), 1)

    def test_fake_sha_is_rejected(self):
        self.start()
        with self.assertRaises(subprocess.CalledProcessError):
            self.append(sha='f' * 40)

    def test_finish_requires_summary(self):
        self.start()
        with self.assertRaises(ValueError):
            self.append('HANDOFF_COMPLETED')

    def test_implementer_cannot_author_review(self):
        self.start()
        with self.assertRaises(ValueError):
            self.append('REVIEW_RECORDED')

    def test_same_independent_verifier_can_append_review_correction(self):
        self.start()
        (self.target / 'summary.md').write_text('handoff')
        self.append('HANDOFF_COMPLETED')
        self.assertTrue(self.append('REVIEW_CORRECTIONS', 'VERIFIER')['ok'])
        self.assertTrue(self.append('REVIEW_CORRECTIONS', 'VERIFIER')['ok'])

    def test_non_correction_after_terminal_is_rejected(self):
        self.start()
        (self.target / 'summary.md').write_text('handoff')
        self.append('HANDOFF_COMPLETED')
        with self.assertRaises(ValueError):
            self.append('IMPLEMENTATION_COMMITTED')

    def test_invalid_sequence_is_rejected(self):
        self.start()
        event = self.target / 'events/0001-work-order-started.json'
        data = json.loads(event.read_text()); data['sequence'] = 2
        write_json(event, data)
        self.assertFalse(work_cli.inspect_execution(self.target)['ok'])

    def test_sequence_profile_cannot_relax_scientific_claim(self):
        self.start()
        path = self.target / 'passport.json'
        data = json.loads(path.read_text()); data['claim_class'] = 'C1_COMPUTATIONAL_REPRODUCTION'
        write_json(path, data)
        self.assertFalse(work_cli.inspect_execution(self.target)['ok'])

    def test_legacy_profile_not_silently_migrated(self):
        self.start()
        path = self.target / 'passport.json'
        data = json.loads(path.read_text()); del data['event_ordering']
        write_json(path, data)
        before = path.read_bytes()
        with self.assertRaises(ValueError):
            self.append()
        self.assertEqual(path.read_bytes(), before)

    def test_writer_lock_prevents_concurrent_publication(self):
        self.start()
        lock = self.target.parent / ('.' + self.target.name + '.writer.lock')
        lock.write_text('another writer')
        with self.assertRaises(FileExistsError):
            self.append()
        self.assertEqual(lock.read_text(), 'another writer')

    def test_path_escape_is_rejected(self):
        with self.assertRaises(ValueError):
            work_events.safe_target(self.root, self.root / 'other/EX-FLOW-TEST-R1')

    def test_symlink_target_rejected(self):
        self.start()
        link = self.target.parent / 'EX-LINK'
        link.symlink_to(self.target, target_is_directory=True)
        with self.assertRaises(ValueError):
            work_events.safe_target(self.root, link)


class BatchValidationTests(GitCase):
    def test_all_tracked_json_checked(self):
        write_json(self.root / 'a.json', {'a': 1})
        write_json(self.root / 'b.json', {'b': 2})
        self.git('add', '.')
        self.assertEqual(batch_validate.check_json(self.root)['checked'], 2)
        (self.root / 'b.json').write_text('{')
        result = batch_validate.check_json(self.root)
        self.assertFalse(result['ok'])
        self.assertTrue(any('b.json' in e for e in result['errors']))

    def test_pinned_negative_fixture_and_tamper(self):
        name = next(iter(batch_validate.PINNED_NON_JSON))
        path = self.root / name; path.parent.mkdir(parents=True)
        path.write_bytes(b'')
        self.git('add', '.')
        self.assertTrue(batch_validate.check_json(self.root)['ok'])
        path.write_bytes(b'{}')
        self.assertFalse(batch_validate.check_json(self.root)['ok'])

    def test_empty_sweeps_fail_closed(self):
        self.assertFalse(batch_validate.check_json(self.root)['ok'])
        self.assertFalse(batch_validate.check_executions(self.root)['ok'])

    def test_malformed_execution_is_reported_not_skipped(self):
        write_json(self.root / 'docs/work/executions/EX-BAD/passport.json', {})
        result = batch_validate.check_executions(self.root)
        self.assertFalse(result['ok'])
        self.assertEqual(result['checked'], 1)

    def test_batch_execution_result_matches_single_inspector(self):
        target = self.root / 'docs/work/executions/EX-BATCH'
        work_events.start(self.root, target, work_order='WO-BATCH', checkpoint='NL5', risk='LOW',
                          allowed_paths=['a.txt'], sha=self.base, summary='start', next_action='test')
        batch = batch_validate.check_executions(self.root)
        single = work_cli.inspect_execution(target)
        self.assertEqual(batch['ok'], single['ok'])
        self.assertEqual(batch['results'][0]['passport_sha256'], single['passport_sha256'])


class ReviewImpactTests(GitCase):
    report = 'docs/work/executions/EX-REPORT/summary.md'
    def add_report(self):
        path = self.root / self.report; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('report')
        return self.commit()

    def test_report_only_requires_delta_review_not_auto_pass(self):
        head = self.add_report()
        result = review_impact.compare(self.root, self.base, head, [self.report])
        self.assertEqual(result['classification'], 'PUBLICATION_ONLY_CANDIDATE')
        self.assertTrue(result['subject_equivalent'])
        self.assertFalse(result['previous_verdict_reusable_without_review'])
        self.assertFalse(result['merge_authorized'])

    def test_report_change_without_explicit_exclusion_is_full_review(self):
        self.assertEqual(review_impact.compare(self.root, self.base, self.add_report())['classification'], 'FULL_REVIEW')

    def test_code_change_invalidates_equivalence(self):
        self.add_report()
        (self.root / 'marker.txt').write_text('changed code')
        result = review_impact.compare(self.root, self.base, self.commit(), [self.report])
        self.assertEqual(result['classification'], 'FULL_REVIEW')

    def test_protocol_or_wildcard_cannot_be_excluded(self):
        for path in ('docs/research/protocol.md', 'scripts/harness/cli.py', 'docs/**', 'docs/work/executions/EX-X/../../summary.md'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                review_impact.compare(self.root, self.base, self.base, [path])

    def test_modifying_existing_event_is_not_publication_only(self):
        name = 'docs/work/executions/EX-REPORT/events/0001-work-order-started.json'
        write_json(self.root / name, {'value': 1})
        old = self.commit()
        write_json(self.root / name, {'value': 2})
        result = review_impact.compare(self.root, old, self.commit(), [name])
        self.assertEqual(result['classification'], 'FULL_REVIEW')

    def test_symlink_report_is_not_publication_only(self):
        path = self.root / self.report; path.parent.mkdir(parents=True)
        path.symlink_to(self.root / 'marker.txt')
        result = review_impact.compare(self.root, self.base, self.commit(), [self.report])
        self.assertEqual(result['classification'], 'FULL_REVIEW')

    def test_unchanged_subject_is_not_new_approval(self):
        result = review_impact.compare(self.root, self.base, self.base)
        self.assertEqual(result['classification'], 'UNCHANGED')
        self.assertFalse(result['merge_authorized'])


class ResourceArithmeticTests(unittest.TestCase):
    def test_df_reserved_blocks_are_excluded_and_result_minimal(self):
        for used, available, expected in [(446395604992, 19686797312, 73529683149),
                                          (902998384640, 52755177472, 138395534951)]:
            with self.subTest(used=used):
                freed = resource_plan.bytes_to_free(used, available)
                self.assertEqual(freed, expected)
                self.assertLessEqual(100 * (used - freed), 80 * (used + available))
                self.assertGreater(100 * (used - freed + 1), 80 * (used + available))

    def test_df_invalid_inputs_rejected(self):
        for args in [(True, 100), (-1, 10), (0, 0), (10, 10, 100), (10, 10, 0)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                resource_plan.bytes_to_free(*args)

    def test_already_under_disk_target_needs_no_cleanup(self):
        self.assertEqual(resource_plan.bytes_to_free(10, 90), 0)

    def test_published_p2_timings_replayed_without_engine(self):
        p = ROOT / 'docs/work/executions/EX-NL5-002-E-R1/evidence/p2/run_output_digests_p2.json'
        result = resource_plan.p2_estimate(json.loads(p.read_text()))
        self.assertEqual(result['historical_runs'], 20)
        self.assertAlmostEqual(result['primary_job_wall_hours'], 1512.3075555555556)
        self.assertGreater(result['ideal_primary_elapsed_lower_bound_hours'], 560)
        self.assertFalse(result['dispatch_authorized'])
        self.assertTrue(result['excludes_controls_and_replacements'])

    def test_p2_missing_data_is_not_assumed_fast(self):
        with self.assertRaises(ValueError):
            resource_plan.p2_estimate({'runs': []})

    def test_systemctl_running_and_unit_active_are_distinct(self):
        self.assertTrue(resource_plan.service_readiness('running', {'executor': 'active'}, [], [])['ok'])
        self.assertFalse(resource_plan.service_readiness('active', {'executor': 'active'}, [], [])['ok'])

    def test_degraded_requires_explicit_classification(self):
        args = ('degraded', {'executor': 'active'}, ['desktop-portal'])
        self.assertFalse(resource_plan.service_readiness(*args, [])['ok'])
        self.assertTrue(resource_plan.service_readiness(*args, ['desktop-portal'])['ok'])

    def test_failed_critical_unit_cannot_be_exempted(self):
        result = resource_plan.service_readiness('degraded', {'executor': 'failed'}, ['executor'], ['executor'])
        self.assertFalse(result['ok'])
        self.assertFalse(result['scientific_dispatch_authorized'])


if __name__ == '__main__':
    unittest.main()
