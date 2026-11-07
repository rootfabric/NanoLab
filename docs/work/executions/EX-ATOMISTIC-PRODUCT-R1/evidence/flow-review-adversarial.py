"""Independent FLOW-R1 reviewer falsifiers; temporary repos only, no science."""
import concurrent.futures
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SUBJECT_ROOT = Path('/workspace/scratch/48cb7a65c9c0/NanoLab-flow-review')
sys.path.insert(0, str(SUBJECT_ROOT / 'scripts'))
from harness import operations, work_events, work_cli, batch_validate, review_impact, resource_plan

class IndependentFalsifiers(unittest.TestCase):
    def test_resource_integer_minimum_exhaustive(self):
        count = 0
        for used in range(0, 100):
            for available in range(0, 100):
                if not used + available:
                    continue
                for target in (1, 20, 50, 80, 99):
                    freed = resource_plan.bytes_to_free(used, available, target)
                    self.assertLessEqual(Fraction(used - freed, used + available), Fraction(target, 100))
                    if freed:
                        self.assertGreater(Fraction(used - freed + 1, used + available), Fraction(target, 100))
                    count += 1
        print('resource exact-rational cases:', count)

    def test_resource_published_arithmetic_and_source_digest(self):
        correction = json.loads((SUBJECT_ROOT / 'docs/control/RESOURCE_PLAN_CORRECTIONS_R1.json').read_text())
        raw = (SUBJECT_ROOT / correction['p2_source']['path']).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), correction['p2_source']['sha256'])
        self.assertEqual(resource_plan.p2_estimate(json.loads(raw)), correction['p2_primary_projection'])
        for row in correction['filesystem_corrections']:
            used, avail = row['used_bytes'], row['available_unpriv_bytes']
            self.assertEqual(resource_plan.bytes_to_free(used, avail), row['correct_min_free_bytes_for_df_80'])
            self.assertAlmostEqual(float(Fraction(used-row['old_proposed_free_bytes'], used+avail)), row['ratio_after_old_free'])

    def test_operations_mutation_matrix(self):
        plan = json.loads((SUBJECT_ROOT / 'project/plan.json').read_text())
        state = json.loads((SUBJECT_ROOT / 'project/state.json').read_text())
        card = json.loads((SUBJECT_ROOT / 'project/operations/RESOURCE-R1.json').read_text())
        mutations = [('status', []), ('actor', {}), ('priority', False), ('schema_version', True),
                     ('scientific_runs_allowed', 0), ('depends_on', ['NL5-002']),
                     ('blockers', ['NO']), ('claim_class', 'C1_COMPUTATIONAL_REPRODUCTION'),
                     ('updated_at_utc', 'tomorrow')]
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); path=root/'project/operations/RESOURCE-R1.json';path.parent.mkdir(parents=True)
            for field, value in mutations:
                mutated=copy.deepcopy(card);mutated[field]=value;path.write_text(json.dumps(mutated))
                self.assertFalse(operations.load_tasks(root,plan,state)['ok'], (field, value))
        print('malformed operations rejected:', len(mutations))

    def git_repo(self):
        temp = tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);root=Path(temp.name)
        def git(*args):
            return subprocess.check_output(['git', *args], cwd=root, stderr=subprocess.PIPE).decode().strip()
        git('init','-q');git('config','user.name','Independent reviewer');git('config','user.email','reviewer@example.invalid')
        (root/'product.txt').write_text('immutable product\n')
        def commit():
            git('add','.');git('commit','-qm','fixture');return git('rev-parse','HEAD')
        return root, git, commit, commit()

    def test_real_concurrent_writers_and_no_rewrite(self):
        root,git,commit,base=self.git_repo();target=root/'docs/work/executions/EX-REVIEW-RACE'
        work_events.start(root,target,work_order='WO-REVIEW-RACE',checkpoint='NL5',risk='MEDIUM',allowed_paths=['product.txt'],sha=base,summary='start',next_action='test')
        first=(target/'events/0001-work-order-started.json').read_bytes()
        def writer(n):
            try:
                work_events.append(root,target,kind='VALIDATION_RECORDED',role='IMPLEMENTER',sha=base,summary=f'writer {n}')
                return 'published'
            except FileExistsError:
                return 'locked'
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            outcomes=list(pool.map(writer, range(8)))
        inspection=work_cli.inspect_execution(target)
        self.assertTrue(inspection['ok'], inspection)
        self.assertEqual((target/'events/0001-work-order-started.json').read_bytes(),first)
        self.assertEqual(len(list((target/'events').glob('*.json'))),1+outcomes.count('published'))
        self.assertGreaterEqual(outcomes.count('published'),1)
        self.assertFalse(list(target.parent.glob('*.lock')))
        print('concurrent writers:', outcomes)

    def test_batch_continues_after_bad_execution(self):
        root,git,commit,base=self.git_repo()
        for label in ('A','C'):
            path=root/f'docs/work/executions/EX-{label}';path.mkdir(parents=True);(path/'passport.json').write_text('{')
        target=root/'docs/work/executions/EX-B'
        work_events.start(root,target,work_order='WO-B',checkpoint='NL5',risk='LOW',allowed_paths=['product.txt'],sha=base,summary='start',next_action='test')
        result=batch_validate.check_executions(root)
        self.assertFalse(result['ok']);self.assertEqual(result['checked'],3)
        self.assertEqual([row['ok'] for row in result['results']],[False,True,False])

    def test_review_mode_deletion_and_nonpublication_product(self):
        root,git,commit,base=self.git_repo();name='docs/work/executions/EX-MODE/summary.md';path=root/name;path.parent.mkdir(parents=True);path.write_text('report')
        added=commit();self.assertEqual(review_impact.compare(root,base,added,[name])['classification'],'PUBLICATION_ONLY_CANDIDATE')
        path.chmod(0o755);executable=commit();self.assertEqual(review_impact.compare(root,added,executable,[name])['classification'],'FULL_REVIEW')
        path.chmod(0o644);regular=commit()
        (root/'product.txt').write_text('changed');changed=commit();self.assertEqual(review_impact.compare(root,executable,changed,[name])['classification'],'FULL_REVIEW')
        path.unlink();deleted=commit();self.assertEqual(review_impact.compare(root,changed,deleted,[name])['classification'],'FULL_REVIEW')

    def test_review_executable_base_must_not_be_report_only(self):
        root,git,commit,base=self.git_repo();name='docs/work/executions/EX-MODE/summary.md';path=root/name;path.parent.mkdir(parents=True);path.write_text('#!/bin/sh\necho executable report\n');path.chmod(0o755)
        executable=commit();path.chmod(0o644);head=commit()
        result=review_impact.compare(root,executable,head,[name])
        print('base executable -> head regular:', result['classification'], result['subject_equivalent'])
        self.assertEqual(result['classification'],'FULL_REVIEW')

if __name__ == '__main__':
    unittest.main(verbosity=2)
