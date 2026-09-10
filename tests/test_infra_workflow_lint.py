"""Workflow negative-control lint tests (INFRA1-002, control WO EX-CTRL-LINTSCHEMA-R1).

Required negative control: a workflow with `runs-on: nanolab-cpu` MUST FAIL
(NC-1: an untrusted PR route cannot select a trusted self-hosted label).
Control WO EX-CTRL-LINTSCHEMA-R1 adds the MINOR-4 tab-indentation negatives
(TAB in leading whitespace of any line -> WORKFLOW_UNPARSEABLE) and the NOTE-5
jobs-form negatives (missing/non-mapping `jobs:` -> fail closed), plus the
full negative matrix across rule families.
Run: python -m unittest discover -s tests -t .
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from harness.workflow_lint import lint_paths, load_policy  # noqa: E402

POLICY_PATH = REPO_ROOT / "config" / "infra" / "validation-gates.v1.json"

COMPLIANT_WORKFLOW = """\
name: compliant-fixture

on:
  pull_request:
    branches: [main]
    types: [opened, synchronize, reopened, ready_for_review]
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  validate:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout
        uses: actions/checkout@93cb6efe18208431cddfb8368fd83d5badbf9bfd # v5.0.1
        with:
          persist-credentials: false
      - name: Check
        run: |
          echo "ok"
"""


def policy() -> dict:
    return load_policy(POLICY_PATH)


def lint_yaml(text: str) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "fixture.yml"
        path.write_text(text, encoding="utf-8")
        return lint_paths([path], policy())


def rule_ids(report: dict) -> set:
    return {v["rule_id"] for w in report["workflows"] for v in w["violations"]}


class PositiveLintTests(unittest.TestCase):
    @unittest.skipUnless(POLICY_PATH.is_file(), "validation gates config required")
    def test_compliant_workflow_passes(self) -> None:
        report = lint_yaml(COMPLIANT_WORKFLOW)
        self.assertTrue(report["ok"], json.dumps(report, indent=2))
        self.assertEqual(rule_ids(report), set())

    @unittest.skipUnless((REPO_ROOT / ".github/workflows/hosted-ci.yml").is_file(), "repository checkout required")
    def test_real_hosted_ci_workflow_passes(self) -> None:
        report = lint_paths([REPO_ROOT / ".github" / "workflows" / "hosted-ci.yml"], policy())
        self.assertTrue(report["ok"], json.dumps(report, indent=2))


class NC1RunnerLabelTests(unittest.TestCase):
    @unittest.skipUnless(POLICY_PATH.is_file(), "validation gates config required")
    def test_runs_on_nanolab_cpu_must_fail(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("runs-on: ubuntu-latest", "runs-on: nanolab-cpu")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC1_SELF_HOSTED_LABEL", rule_ids(report))

    @unittest.skipUnless(POLICY_PATH.is_file(), "validation gates config required")
    def test_reserved_hpc_label_prefix_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("runs-on: ubuntu-latest", "runs-on: nanolab-hpc-cpu")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC1_SELF_HOSTED_LABEL", rule_ids(report))

    @unittest.skipUnless(POLICY_PATH.is_file(), "validation gates config required")
    def test_self_hosted_label_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("runs-on: ubuntu-latest", "runs-on: self-hosted")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC1_SELF_HOSTED_LABEL", rule_ids(report))

    @unittest.skipUnless(POLICY_PATH.is_file(), "validation gates config required")
    def test_dynamic_runs_on_expression_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("runs-on: ubuntu-latest", "runs-on: ${{ github.event.inputs.runner }}")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC1_DYNAMIC_RUNS_ON", rule_ids(report))

    @unittest.skipUnless(POLICY_PATH.is_file(), "validation gates config required")
    def test_missing_runs_on_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("    runs-on: ubuntu-latest\n", "")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC1_RUNS_ON_MISSING", rule_ids(report))


class NC2TrustBoundaryTests(unittest.TestCase):
    @unittest.skipUnless(POLICY_PATH.is_file(), "validation gates config required")
    def test_pull_request_target_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("pull_request:", "pull_request_target:")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC2_FORBIDDEN_TRIGGER", rule_ids(report))

    @unittest.skipUnless(POLICY_PATH.is_file(), "validation gates config required")
    def test_workflow_run_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("  push:", "  workflow_run:")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC2_FORBIDDEN_TRIGGER", rule_ids(report))

    @unittest.skipUnless(POLICY_PATH.is_file(), "validation gates config required")
    def test_reserved_schedule_trigger_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("  push:", "  schedule:")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC2_TRIGGER_NEEDS_BASELINE_REVISION", rule_ids(report))

    @unittest.skipUnless(POLICY_PATH.is_file(), "validation gates config required")
    def test_external_reusable_workflow_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("  validate:\n", "  validate:\n    uses: other/repo/.github/workflows/x.yml@main\n")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC2_EXTERNAL_REUSABLE_WORKFLOW", rule_ids(report))


class NC4NC6NC7Tests(unittest.TestCase):
    @unittest.skipUnless(POLICY_PATH.is_file(), "validation gates config required")
    def test_missing_permissions_block_fails(self) -> None:
        text = "\n".join(line for line in COMPLIANT_WORKFLOW.splitlines() if not line.startswith("permissions:") and not line.startswith("  contents: read"))
        report = lint_yaml(text + "\n")
        self.assertFalse(report["ok"])
        self.assertIn("NC4_PERMISSIONS_BLOCK_MISSING", rule_ids(report))

    @unittest.skipUnless(POLICY_PATH.is_file(), "validation gates config required")
    def test_write_permission_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("  contents: read", "  contents: write")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC4_WRITE_PERMISSION", rule_ids(report))

    @unittest.skipUnless(POLICY_PATH.is_file(), "validation gates config required")
    def test_secrets_reference_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace('echo "ok"', 'echo "$DEPLOY_TOKEN" # via ${{ secrets.DEPLOY_TOKEN }}')
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC7_SECRETS_REFERENCE", rule_ids(report))

    @unittest.skipUnless(POLICY_PATH.is_file(), "validation gates config required")
    def test_missing_timeout_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("    timeout-minutes: 15\n", "")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("BUDGET_TIMEOUT_REQUIRED", rule_ids(report))

    @unittest.skipUnless(POLICY_PATH.is_file(), "validation gates config required")
    def test_out_of_bounds_timeout_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("timeout-minutes: 15", "timeout-minutes: 120")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("BUDGET_TIMEOUT_BOUNDS", rule_ids(report))


class PinningAndNote3Tests(unittest.TestCase):
    @unittest.skipUnless(POLICY_PATH.is_file(), "validation gates config required")
    def test_tag_pinned_action_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("@93cb6efe18208431cddfb8368fd83d5badbf9bfd # v5.0.1", "@v5")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("PIN_ACTION_FULL_SHA", rule_ids(report))

    @unittest.skipUnless(POLICY_PATH.is_file(), "validation gates config required")
    def test_pull_request_without_ready_for_review_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("types: [opened, synchronize, reopened, ready_for_review]", "types: [opened, synchronize]")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NOTE3_PR_TYPES_READY_FOR_REVIEW", rule_ids(report))

    @unittest.skipUnless(POLICY_PATH.is_file(), "validation gates config required")
    def test_pull_request_without_types_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("    types: [opened, synchronize, reopened, ready_for_review]\n", "")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NOTE3_PR_TYPES_READY_FOR_REVIEW", rule_ids(report))


class FailClosedTests(unittest.TestCase):
    @unittest.skipUnless(POLICY_PATH.is_file(), "validation gates config required")
    def test_unparseable_workflow_fails(self) -> None:
        report = lint_yaml("jobs:\n  broken:\n    - just a list where a mapping belongs\n      nonsense: [unclosed\n")
        self.assertFalse(report["ok"])
        self.assertIn("WORKFLOW_UNPARSEABLE", rule_ids(report))


class MAJOR1TriggerFormTests(unittest.TestCase):
    """Repair R1 MAJOR-1: non-dict or missing `on:` must fail closed."""

    def test_on_flow_form_with_forbidden_trigger_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace(
            "on:\n  pull_request:\n    branches: [main]\n    types: [opened, synchronize, reopened, ready_for_review]\n  push:\n    branches: [main]",
            "on: [push, pull_request_target]",
        )
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC2_TRIGGERS_UNSUPPORTED_FORM", rule_ids(report))

    def test_on_scalar_form_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace(
            "on:\n  pull_request:\n    branches: [main]\n    types: [opened, synchronize, reopened, ready_for_review]\n  push:\n    branches: [main]",
            "on: push",
        )
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC2_TRIGGERS_UNSUPPORTED_FORM", rule_ids(report))

    def test_missing_on_block_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace(
            "on:\n  pull_request:\n    branches: [main]\n    types: [opened, synchronize, reopened, ready_for_review]\n  push:\n    branches: [main]\n\n",
            "",
        )
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC2_TRIGGERS_BLOCK_MISSING", rule_ids(report))

    def test_null_on_block_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace(
            "on:\n  pull_request:\n    branches: [main]\n    types: [opened, synchronize, reopened, ready_for_review]\n  push:\n    branches: [main]",
            "on:",
        )
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC2_TRIGGERS_BLOCK_MISSING", rule_ids(report))


class MAJOR2AnchorAliasTests(unittest.TestCase):
    """Repair R1 MAJOR-2: YAML anchors/aliases must fail closed."""

    def test_anchor_and_alias_in_runs_on_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("runs-on: ubuntu-latest", "runs-on: &cpu nanolab-cpu")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("WORKFLOW_UNPARSEABLE", rule_ids(report))
        message = report["workflows"][0]["violations"][0]["message"]
        self.assertIn("anchor/alias", message)

    def test_alias_dereference_in_runs_on_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("runs-on: ubuntu-latest", "runs-on: *cpu")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("WORKFLOW_UNPARSEABLE", rule_ids(report))

    def test_anchor_in_non_runner_field_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("timeout-minutes: 15", "timeout-minutes: &t 15")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("WORKFLOW_UNPARSEABLE", rule_ids(report))

    def test_merge_key_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("jobs:\n", "jobs:\n  <<: *defaults\n")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("WORKFLOW_UNPARSEABLE", rule_ids(report))

    def test_ampersand_inside_run_script_is_not_an_anchor(self) -> None:
        text = COMPLIANT_WORKFLOW.replace('echo "ok"', 'echo "a" && echo "b"')
        report = lint_yaml(text)
        self.assertTrue(report["ok"], json.dumps(report, indent=2))


class MINOR1SecretsBracketTests(unittest.TestCase):
    """Repair R1 MINOR-1: bracket-form secret expressions must be caught."""

    def test_bracket_single_quote_form_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace('echo "ok"', 'echo "${{ secrets[\'DEPLOY_TOKEN\'] }}"')
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC7_SECRETS_REFERENCE", rule_ids(report))

    def test_bracket_double_quote_form_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace('echo "ok"', 'echo "${{ secrets[\\"DEPLOY_TOKEN\\"] }}"')
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC7_SECRETS_REFERENCE", rule_ids(report))

    def test_dot_form_still_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace('echo "ok"', 'echo "$DEPLOY_TOKEN" # via ${{ secrets.DEPLOY_TOKEN }}')
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC7_SECRETS_REFERENCE", rule_ids(report))


class NOTE1TriggerGuardTests(unittest.TestCase):
    """Repair R1 NOTE-1: the ready_for_review rule applies only to pull_request workflows."""

    def test_push_only_workflow_does_not_trigger_note3(self) -> None:
        text = COMPLIANT_WORKFLOW.replace(
            "on:\n  pull_request:\n    branches: [main]\n    types: [opened, synchronize, reopened, ready_for_review]\n  push:\n    branches: [main]",
            "on:\n  push:\n    branches: [main]",
        )
        report = lint_yaml(text)
        self.assertTrue(report["ok"], json.dumps(report, indent=2))
        self.assertNotIn("NOTE3_PR_TYPES_READY_FOR_REVIEW", rule_ids(report))

    def test_bare_pull_request_trigger_still_fails_note3(self) -> None:
        text = COMPLIANT_WORKFLOW.replace(
            "on:\n  pull_request:\n    branches: [main]\n    types: [opened, synchronize, reopened, ready_for_review]",
            "on:\n  pull_request:",
        )
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NOTE3_PR_TYPES_READY_FOR_REVIEW", rule_ids(report))


class MultiDocumentTests(unittest.TestCase):
    """Repair R1 NOTE-3: multi-document files are rejected instead of merged."""

    def test_multi_document_workflow_fails(self) -> None:
        second_doc = (
            "---\nname: second\non:\n  pull_request_target:\n    branches: [main]\n"
            "permissions:\n  contents: write\njobs:\n  evil:\n    runs-on: nanolab-cpu\n    timeout-minutes: 15\n    steps:\n      - run: echo\n"
        )
        report = lint_yaml(COMPLIANT_WORKFLOW + second_doc)
        self.assertFalse(report["ok"])
        rules = rule_ids(report)
        self.assertIn("WORKFLOW_UNPARSEABLE", rules)
        self.assertNotIn("NC2_FORBIDDEN_TRIGGER", rules)


class MINOR4TabIndentationTests(unittest.TestCase):
    """Control WO EX-CTRL-LINTSCHEMA-R1, MINOR-4: the parser must reject a TAB
    in the leading whitespace of ANY raw line (YAML forbids tab indentation).
    The old check compared a spaces-only prefix slice and could never fire, so
    TAB-led keys silently rebuilt the document instead of failing closed."""

    def test_tab_indented_key_under_on_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("  push:", "\tpush:")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("WORKFLOW_UNPARSEABLE", rule_ids(report))
        self.assertIn("tab character in leading whitespace", report["workflows"][0]["violations"][0]["message"])

    def test_tab_indented_key_under_job_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("    runs-on: ubuntu-latest", "\truns-on: ubuntu-latest")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("WORKFLOW_UNPARSEABLE", rule_ids(report))
        self.assertIn("tab character in leading whitespace", report["workflows"][0]["violations"][0]["message"])

    def test_tab_indented_top_level_key_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("permissions:", "\tpermissions:")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("WORKFLOW_UNPARSEABLE", rule_ids(report))

    def test_tab_indented_step_inside_job_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace('          echo "ok"', '\t\techo "ok"')
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("WORKFLOW_UNPARSEABLE", rule_ids(report))

    def test_tab_before_comment_line_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("name: compliant-fixture\n", "name: compliant-fixture\n\t# tab-indented comment\n")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("WORKFLOW_UNPARSEABLE", rule_ids(report))

    def test_tab_only_blank_line_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("permissions:\n", "permissions:\n\t\n")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("WORKFLOW_UNPARSEABLE", rule_ids(report))

    def test_mixed_space_tab_leading_whitespace_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("  push:", " \tpush:")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("WORKFLOW_UNPARSEABLE", rule_ids(report))

    def test_tab_inside_scalar_value_is_allowed(self) -> None:
        text = COMPLIANT_WORKFLOW.replace('echo "ok"', 'echo "a\tb"')
        report = lint_yaml(text)
        self.assertTrue(report["ok"], json.dumps(report, indent=2))
        self.assertNotIn("WORKFLOW_UNPARSEABLE", rule_ids(report))


class NOTE5JobsMappingTests(unittest.TestCase):
    """Control WO EX-CTRL-LINTSCHEMA-R1, NOTE-5: a missing or non-mapping
    `jobs:` block must fail closed instead of silently skipping the job-level
    rules (NC-1 labels, NC-6 timeouts, action pinning)."""

    def jobs_only(self, block: str) -> str:
        return COMPLIANT_WORKFLOW.split("jobs:", 1)[0] + block

    def test_jobs_sequence_with_nanolab_cpu_fails(self) -> None:
        report = lint_yaml(self.jobs_only("jobs:\n  - nanolab-cpu\n"))
        self.assertFalse(report["ok"])
        self.assertIn("WORKFLOW_JOBS_UNSUPPORTED_FORM", rule_ids(report))

    def test_jobs_sequence_benign_content_still_fails(self) -> None:
        report = lint_yaml(self.jobs_only("jobs:\n  - ubuntu-latest\n"))
        self.assertFalse(report["ok"])
        self.assertIn("WORKFLOW_JOBS_UNSUPPORTED_FORM", rule_ids(report))

    def test_jobs_sequence_of_mappings_still_fails(self) -> None:
        report = lint_yaml(self.jobs_only("jobs:\n  - validate:\n      runs-on: ubuntu-latest\n      timeout-minutes: 15\n"))
        self.assertFalse(report["ok"])
        self.assertIn("WORKFLOW_JOBS_UNSUPPORTED_FORM", rule_ids(report))

    def test_jobs_scalar_form_fails(self) -> None:
        report = lint_yaml(self.jobs_only("jobs: validate\n"))
        self.assertFalse(report["ok"])
        self.assertIn("WORKFLOW_JOBS_UNSUPPORTED_FORM", rule_ids(report))

    def test_jobs_null_form_fails(self) -> None:
        report = lint_yaml(self.jobs_only("jobs:\n"))
        self.assertFalse(report["ok"])
        self.assertIn("WORKFLOW_JOBS_BLOCK_MISSING", rule_ids(report))

    def test_jobs_missing_fails(self) -> None:
        report = lint_yaml(COMPLIANT_WORKFLOW.split("jobs:", 1)[0])
        self.assertFalse(report["ok"])
        self.assertIn("WORKFLOW_JOBS_BLOCK_MISSING", rule_ids(report))

    def test_jobs_flow_mapping_is_still_linted(self) -> None:
        text = self.jobs_only("jobs: {validate: {runs-on: nanolab-cpu, timeout-minutes: 15, steps: [{run: echo ok}]}}\n")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC1_SELF_HOSTED_LABEL", rule_ids(report))
        self.assertNotIn("WORKFLOW_JOBS_UNSUPPORTED_FORM", rule_ids(report))

    def test_jobs_flow_mapping_compliant_passes(self) -> None:
        text = self.jobs_only("jobs: {validate: {runs-on: ubuntu-latest, timeout-minutes: 15, steps: [{run: 'echo ok'}]}}\n")
        report = lint_yaml(text)
        self.assertTrue(report["ok"], json.dumps(report, indent=2))


class RunsOnEmptyListTests(unittest.TestCase):
    """Control WO EX-CTRL-LINTSCHEMA-R1 (NOTE-5 family): an empty runs-on list
    selects no runner and must not bypass NC-1."""

    def test_empty_runs_on_list_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("runs-on: ubuntu-latest", "runs-on: []")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC1_RUNS_ON_MISSING", rule_ids(report))

    def test_runs_on_list_form_passes(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("runs-on: ubuntu-latest", "runs-on: [ubuntu-latest]")
        report = lint_yaml(text)
        self.assertTrue(report["ok"], json.dumps(report, indent=2))


class NegativeMatrixExpansionTests(unittest.TestCase):
    """Control WO EX-CTRL-LINTSCHEMA-R1: full negative matrix across rule
    families (case/prefix label variants, reserved triggers, permission and
    timeout edges, pinning forms, NOTE-3 type forms, parser rejects)."""

    def test_nanolab_gpu_label_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("runs-on: ubuntu-latest", "runs-on: nanolab-gpu")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC1_SELF_HOSTED_LABEL", rule_ids(report))

    def test_mixed_case_nanolab_cpu_label_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("runs-on: ubuntu-latest", "runs-on: Nanolab-CPU")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC1_SELF_HOSTED_LABEL", rule_ids(report))

    def test_uppercase_self_hosted_label_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("runs-on: ubuntu-latest", "runs-on: SELF-HOSTED")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC1_SELF_HOSTED_LABEL", rule_ids(report))

    def test_forbidden_label_inside_list_form_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("runs-on: ubuntu-latest", "runs-on: [ubuntu-latest, nanolab-cpu]")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC1_SELF_HOSTED_LABEL", rule_ids(report))

    def test_workflow_run_with_filters_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace(
            "  push:\n    branches: [main]",
            "  workflow_run:\n    workflows: [hosted-ci]\n    types: [completed]",
        )
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC2_FORBIDDEN_TRIGGER", rule_ids(report))

    def test_workflow_dispatch_reserved_trigger_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("  push:\n    branches: [main]", "  workflow_dispatch:\n    branches: [main]")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC2_TRIGGER_NEEDS_BASELINE_REVISION", rule_ids(report))

    def test_release_reserved_trigger_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("  push:\n    branches: [main]", "  release:\n    types: [published]")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC2_TRIGGER_NEEDS_BASELINE_REVISION", rule_ids(report))

    def test_workflow_level_write_all_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("permissions:\n  contents: read", "permissions: write-all")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC4_WRITE_PERMISSION", rule_ids(report))

    def test_job_level_write_permission_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace(
            "    timeout-minutes: 15\n",
            "    timeout-minutes: 15\n    permissions:\n      contents: write\n",
        )
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC4_WRITE_PERMISSION", rule_ids(report))

    def test_pull_requests_write_scope_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("  contents: read", "  contents: read\n  pull-requests: write")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC4_WRITE_PERMISSION", rule_ids(report))

    def test_non_scalar_permission_level_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("  contents: read", "  contents: [read]")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC4_WRITE_PERMISSION", rule_ids(report))

    def test_unknown_permission_level_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("  contents: read", "  contents: admin")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC4_WRITE_PERMISSION", rule_ids(report))

    def test_zero_timeout_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("timeout-minutes: 15", "timeout-minutes: 0")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("BUDGET_TIMEOUT_BOUNDS", rule_ids(report))

    def test_timeout_above_max_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("timeout-minutes: 15", "timeout-minutes: 61")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("BUDGET_TIMEOUT_BOUNDS", rule_ids(report))

    def test_string_timeout_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("timeout-minutes: 15", "timeout-minutes: '15'")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("BUDGET_TIMEOUT_BOUNDS", rule_ids(report))

    def test_boolean_timeout_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("timeout-minutes: 15", "timeout-minutes: true")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("BUDGET_TIMEOUT_BOUNDS", rule_ids(report))

    def test_docker_action_without_digest_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace(
            "      - name: Check\n",
            "      - name: Pull\n        uses: docker://alpine:3.19\n      - name: Check\n",
        )
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("PIN_ACTION_FULL_SHA", rule_ids(report))

    def test_docker_action_digest_pinned_passes(self) -> None:
        text = COMPLIANT_WORKFLOW.replace(
            "      - name: Check\n",
            "      - name: Pull\n        uses: docker://alpine@sha256:6457d53fb065d6f250e1504b9bc42d5b6c65941d57532c072d929dd0628977d0\n      - name: Check\n",
        )
        report = lint_yaml(text)
        self.assertTrue(report["ok"], json.dumps(report, indent=2))

    def test_short_sha_pinned_action_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("@93cb6efe18208431cddfb8368fd83d5badbf9bfd # v5.0.1", "@93cb6ef")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("PIN_ACTION_FULL_SHA", rule_ids(report))

    def test_pr_types_scalar_form_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("    types: [opened, synchronize, reopened, ready_for_review]", "    types: opened")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NOTE3_PR_TYPES_READY_FOR_REVIEW", rule_ids(report))

    def test_pr_types_empty_list_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("    types: [opened, synchronize, reopened, ready_for_review]", "    types: []")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NOTE3_PR_TYPES_READY_FOR_REVIEW", rule_ids(report))

    def test_secrets_reference_in_job_env_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace(
            "    timeout-minutes: 15\n",
            "    timeout-minutes: 15\n    env:\n      TOKEN: ${{ secrets.TOKEN }}\n",
        )
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("NC7_SECRETS_REFERENCE", rule_ids(report))

    def test_document_end_marker_followed_by_content_fails(self) -> None:
        report = lint_yaml(COMPLIANT_WORKFLOW + "...\nname: second\n")
        self.assertFalse(report["ok"])
        self.assertIn("WORKFLOW_UNPARSEABLE", rule_ids(report))

    def test_unexpected_indent_fails(self) -> None:
        text = COMPLIANT_WORKFLOW.replace("    runs-on: ubuntu-latest", "      runs-on: ubuntu-latest")
        report = lint_yaml(text)
        self.assertFalse(report["ok"])
        self.assertIn("WORKFLOW_UNPARSEABLE", rule_ids(report))

    def test_crlf_line_endings_pass(self) -> None:
        report = lint_yaml(COMPLIANT_WORKFLOW.replace("\n", "\r\n"))
        self.assertTrue(report["ok"], json.dumps(report, indent=2))


if __name__ == "__main__":
    unittest.main()
