# Branch Passport — EX-NL0-002-R1-REPAIR1

- Branch: `work/nl0-002-license-rights-audit-r1` (продолжение существующей ветки PR #17; новая ветка не создавалась)
- Work Order: `NL0-002` (docs/work/WO-NL0-002.md; repair по FRESH_VERIFIER_R1)
- Checkpoint: `NL0`
- Base SHA: `495b03391e7eff72bbfbb5c5912e35ef9035b868` (original verified candidate HEAD; base ветки — `95b1319600bcc64572d84c0456acb927802ab806`)
- Repair of: `EX-NL0-002-R1` (verdict FAIL / FIX_REQUIRED; fresh verifier evidence `48d6d0c0089d985118e629ac459c7aa9d85e85eb`, `docs/evidence/NL0-002/FRESH_VERIFIER_R1.md` на `origin/control/nl0-002-fresh-verifier-r1`)
- Risk class: `LOW` (documentation / metadata / license evidence pinning)
- Claim class: `C0_SOFTWARE_ONLY`
- Allowed paths: see `passport.json`
- Status: `IN_PROGRESS`
- Scope: только три verifier fix (FIX 1 immutable license evidence; FIX 2 GPL boundary wording; FIX 3 GPL obligations wording) + два non-blocking уточнения. E1/E2 audit заново не повторяется.
- Frozen by verifier: E1 = GPL-3.0 / DOWNLOAD_ON_SETUP; E2 = UNKNOWN / REFERENCE_ONLY; NANOBASE = UNKNOWN per-record; S08 = RESTRICTED / reference-only — не меняются.
- Active experiment campaigns: none
- Next action: fresh exact-head VERIFIER после repair
- Blocking issue: none

Правила прав: `UNKNOWN` не превращается в разрешение; юридически неоднозначные вопросы помечаются `REQUIRES_OWNER_DECISION` / `REQUIRES_LEGAL_REVIEW`, а не решаются агентом. Документы не являются юридическим заключением.
