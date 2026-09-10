# hinge_family — digest-gated structural reproduction checks (NL3-001)

Frozen, deterministic, stdlib-only toolchain for the Shi–Castro–Arya hinge
family. The source (`gauravarya77/DNA-hinge-simulations` @ `23fd1ff…`) is
**REFERENCE_ONLY** (rights `UNKNOWN`): this toolchain never stores, generates
or vendors source bytes — it digest-verifies a user-side download against the
frozen pins registry and records machine-derived structural facts.

## Surfaces

- `source_pins.json` — frozen registry: upstream commit/tree, per-file
  `size_bytes` / `blob_sha1` / `sha256` with provenance classes, variant table
  (`0b` validated in R1; `11b/32b/53b/74b` registered, not validated),
  preregistered sim-input values (E2-SETUP-R1 §5).
- `pins.py` — fail-closed registry loader + digest verification
  (size + SHA-256 + git blob SHA-1).
- `oxdna_topology.py` / `oxdna_conf.py` / `cadnano_design.py` — strict parsers
  and structural checks (any deviation is an error, never a warning).
- `sim_input.py` — preregistered-value confirmation of the author CPU input.
- `validate.py` — orchestration + canonical byte-deterministic JSON report
  (sorted keys, fixed float rounding, no wall-clock data).

## Usage

```bash
# 1) obtain the pinned files user-side (exact commit), into a directory
#    OUTSIDE any NanoLab repository, under their plain basenames:
#    0b.top 0b.conf 0b.json pro_CPU.in
# 2) validate:
PYTHONPATH=scripts python -m hinge_family validate \
    --source-dir <user-dir> --report <report.json>
echo $?   # 0 = all checks pass, 3 = validation failure, 2 = usage/registry error
```

The report is byte-identical for identical inputs (verified in R1); it may be
committed as evidence because it contains only digests, sizes and structural
facts — never source bytes. Hard prohibitions (vendoring, durable caching,
generating the structure and calling it the original) are normative in
`docs/research/HINGE_FAMILY_R1.md` §6.

## Tests

```bash
python -m unittest tests.test_hinge_family
```

Coverage: byte-identical determinism (two CLI runs), digest-gate tampering,
structural negatives (topology/conf/design/sim-input), pins registry contract,
bundled-registry integrity (NL0-001 preregistered blob pins unchanged).
