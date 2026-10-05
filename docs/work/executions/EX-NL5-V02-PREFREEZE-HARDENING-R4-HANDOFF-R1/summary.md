# EX-NL5-V02-PREFREEZE-HARDENING-R4-HANDOFF-R1 — summary

## Result

```text
VERDICT = HANDOFF_READY
CLAIM_CLASS = C0_SOFTWARE_ONLY
SCIENTIFIC_RUNS = 0
CANDIDATE = PRE-DATA / NOT FROZEN
NL5 = IN_PROGRESS
external_reproductions = 0
NL6-001 = LOCKED
```

This execution only publishes durable instructions/evidence for the next real R4 implementation and Ubuntu host-validation work. It does not repair F1–F4 itself and does not activate R2.

## Base and product subject

```text
BASE_MAIN = 87298b36431045474d3784adf5cee8c9a64d0fc9
BASE_TREE = db19f9dd265873f99c995aa279ae5e0c5b21c330

AUDITED_PR48_HEAD = ce13f0e9cb9536aaffddfff0a05c9a73f0870a21

HANDOFF_PRODUCT_HEAD = 36ce836d8858381bc0d27c741ccd11508d262575
HANDOFF_PRODUCT_TREE = 8bfd676b891aef57837ed6ea25d267901f2ef1f4
COMPARE_AT_PRODUCT = ahead 11 / behind 0
```

## Published artifacts

- `docs/work/WO-NL5-V02-PREFREEZE-HARDENING-R4.md` — full R4 mission.
- `docs/evidence/NL5-V02-PREFREEZE-HARDENING-R4/audit_results_2026-10-03.json` — machine-readable observations.
- `docs/evidence/NL5-V02-PREFREEZE-HARDENING-R4/audit/README_AUDIT_R4.md` — provenance, limits and reproduction instructions.
- `docs/evidence/NL5-V02-PREFREEZE-HARDENING-R4/audit/reproduce_findings.py` — pre-repair focused reproducer.
- `docs/evidence/NL5-V02-PREFREEZE-HARDENING-R4/audit/source/*` — exact audited PR #48 modules.
- `docs/evidence/NL5-V02-PREFREEZE-HARDENING-R4/audit/reconstructed_committed_seed_record_R3.json` — exact R3 record used by the audit.
- `docs/evidence/NL5-V02-PREFREEZE-HARDENING-R4/PACKAGE_MANIFEST_R1.json` — hashes/provenance.
- `docs/work/prompts/UBUNTU_AGENT_NL5_R4_R1.md` — ready-to-paste continuation prompt.

## Findings transferred

```text
F1 = freeze/dispatch contract incomplete / fail-open classes
F2 = collision scan error handling + mutable worktree defect
F3 = replacement N+1 reuses confirmatory identities after skips
F4 = integer rounding / scientific wording must be resolved pre-freeze
```

Historical R3 review/verify records are preserved; this new audit is append-only and requires a fresh repair/review/verify cycle.

## Reproduction check

The pre-repair reproducer was executed in an equivalent local layout after publication preparation and returned exit code 0. That result proves only that the documented old weaknesses reproduce; it is not a repaired-product acceptance test.

## Ubuntu state ceiling

```text
AUTHOR_U1 = NOT_ASSIGNED (canonical baseline)
R2_STATUS = WAITING_HOST / NOT_ACTIVE
outenemy = EXTERNAL_U2_ONLY
```

The Ubuntu prompt lets the next agent collect real host evidence if it is running on an eligible owner-provided U1 candidate, but R2 activation still requires all real gates, fresh review, fresh verification and owner Human Gate.

## Next action

Ubuntu IMPLEMENTER fetches this branch, reads the prompt/WO, creates or continues the actual R4 implementation execution from fresh main, and keeps R4 protocol repair separate from INFRA host-validation evidence.
