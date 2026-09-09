"""Workflow negative-control lint tests (INFRA1-002).

Required negative control: a workflow with `runs-on: nanolab-cpu` MUST FAIL
(NC-1: an untrusted PR route cannot select a trusted self-hosted label).
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


if __name__ == "__main__":
    unittest.main()
