#!/bin/bash
# P1 raw->median replay (EX-NL5-002-E-R1) — delegated step per
# docs/evidence/NL5-002-E/P1_RAW_REPLAY_COMMANDS_R1.md.
# Re-runs ONLY the packaged analyzer nanolab-components 0.1.1
# convention/analyze_hinge.py on the EXISTING raw trajectories of the 20 final
# P1 attempts and compares replica_median_deg bit-exact against:
#   1) regenerated report (this run, written to a SEPARATE dir analysis_replay_r1)
#   2) committed evidence/p1/analysis/<final>_analysis.json
#   3) expected value from P1_RAW_REPLAY_COMMANDS_R1.md table (expectations JSON)
# Difference vs committed wrapper analyze_all_p1.sh: this replay reads the raw
# files under their on-disk canonical names (trajectory.dat / hinge_energy.dat —
# the same run files the manifest keys refer to; no traj.dat/energy.dat copies
# exist in the run dirs) and writes reports OUTSIDE the original analysis dir so
# no committed or raw artifact is overwritten. Analyzer invocation is otherwise
# identical. No new physics runs; raw trajectories untouched.
set -u
WS=~/nanolab-platform-sensitivity-r1/P1
PKG=$WS/package
REPO=${REPO:-/mnt/c/NanoLab/nl5-002-e-platform-r1}
EX=$REPO/docs/work/executions/EX-NL5-002-E-R1
RP=$WS/analysis_replay_r1
[ -d "$PKG" ] || PKG=$WS/../package
cd "$WS"
mkdir -p "$RP/exit_code_formatted"

echo "== P1_RAW_MEDIAN_REPLAY_R1 =="
echo "host: $(hostname); utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "PKG=$PKG"
echo "analyzer: $PKG/convention/analyze_hinge.py"
sha256sum "$PKG/convention/analyze_hinge.py"
echo "RP=$RP (separate dir; original analysis/ untouched)"

declare -A WINDOWS=( [0b]=200000 [32b]=150000 )
declare -A RUNS=(
  [0b]="PLATSENS-P1-0B-S001 PLATSENS-P1-0B-S002 PLATSENS-P1-0B-S003 PLATSENS-P1-0B-S004 PLATSENS-P1-0B-S005 PLATSENS-P1-0B-S006 PLATSENS-P1-0B-S007 PLATSENS-P1-0B-S008 PLATSENS-P1-0B-S009-R21 PLATSENS-P1-0B-S010-R14"
  [32b]="PLATSENS-P1-32B-S001-R14 PLATSENS-P1-32B-S002-R13 PLATSENS-P1-32B-S003-R13 PLATSENS-P1-32B-S004-R13 PLATSENS-P1-32B-S005-R13 PLATSENS-P1-32B-S006-R13 PLATSENS-P1-32B-S007 PLATSENS-P1-32B-S008 PLATSENS-P1-32B-S009 PLATSENS-P1-32B-S010"
)

for v in 0b 32b; do
  W=${WINDOWS[$v]}
  for rid in ${RUNS[$v]}; do
    RD="$WS/runs/$rid"
    if [ ! -d "$RD" ]; then echo "$rid MISSING_RUN_DIR" | tee -a "$RP/completeness.txt"; continue; fi
    last_t=$(grep "^t =" "$RD/trajectory.dat" | tail -1 | awk '{print $3}')
    nframes=$(grep -c "^t =" "$RD/trajectory.dat")
    last_step=$(python3 -c "print(int(round(float('$last_t')/0.005)))")
    echo "$rid frames=$nframes last_step=$last_step" | tee -a "$RP/completeness.txt"
    if [ -f "$RD/exit_code.txt" ] && ! grep -q "EXIT_CODE:" "$RD/exit_code.txt"; then
      printf 'EXIT_CODE: %s\n' "$(tr -dc '0-9-' < "$RD/exit_code.txt")" > "$RP/exit_code_formatted/$rid.txt"
      ECF="$RP/exit_code_formatted/$rid.txt"
    else
      ECF="$RD/exit_code.txt"
    fi
    python3 "$PKG/convention/analyze_hinge.py" run \
      --trajectory "$RD/trajectory.dat" --energy "$RD/hinge_energy.dat" \
      --topology "$RD/$v.top" --manifest "$PKG/convention/arm-manifest-$v.json" \
      --variant "$v" --run-id "$rid" --window "$W" \
      --exit-code-file "$ECF" \
      --report "$RP/${rid}_analysis.json" > "$RP/${rid}_analysis_stdout.json" 2> "$RP/${rid}_analysis_stderr.txt"
    echo "analyze $rid exit=$?" | tee -a "$RP/completeness.txt"
  done
done

echo "== MEDIAN COMPARISON (bit-exact string compare of replica_median_deg) =="
REPLAY_DIR="$RP" \
EXPECT="$EX/p1_recovery/p1_raw_replay_expectations_r1.json" \
COMMITTED="$EX/evidence/p1/analysis" \
python3 - <<'PYEOF'
import json, os, re, sys

rp = os.environ["REPLAY_DIR"]
committed = os.environ["COMMITTED"]
expect = json.load(open(os.environ["EXPECT"]))

pat = re.compile(r'"replica_median_deg"\s*:\s*([0-9.eE+-]+)')
npass = nfail = 0
from decimal import Decimal

def deep_diff(a, b, path=""):
    # returns list of differing leaf paths between two parsed JSON docs
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append(path + "/" + k)
            else:
                out += deep_diff(a[k], b[k], path + "/" + k)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(path + "[]")
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                out += deep_diff(x, y, f"{path}[{i}]")
    else:
        if a != b:
            out.append(path)
    return out

for e in sorted(expect, key=lambda x: x["final_attempt"]):
    rid = e["final_attempt"]
    regen = os.path.join(rp, rid + "_analysis.json")
    com = os.path.join(committed, rid + "_analysis.json")
    try:
        regen_txt = open(regen).read()
        com_txt = open(com).read()
    except OSError as ex:
        print(f"{rid}: FILE_MISSING {ex} -> MISMATCH")
        nfail += 1
        continue
    m1 = pat.search(regen_txt)
    m2 = pat.search(com_txt)
    regen_v = m1.group(1) if m1 else None
    com_v = m2.group(1) if m2 else None
    exp_v = e["expected_replica_median_deg"]
    # Criterion (instruction §5.2): regenerated replica_median_deg must match
    # committed analysis AND the MD table value. The MD table pads values to 9
    # decimal places while JSON serialization drops trailing zeros, so equality
    # vs the table accepts string level OR exact decimal level; the notation
    # case is explicitly reported. Nothing else is softened. Structural diff of
    # the full report vs committed is printed (expected documented difference:
    # seed field, injected into committed copies by the campaign evidence
    # driver; packaged analyzer emits seed:null per event 0004 precedent).
    vs_committed = "OK" if (regen_v is not None and regen_v == com_v) else "MISMATCH"
    if regen_v is None:
        vs_table, note = "MISMATCH", ""
    elif regen_v == exp_v:
        vs_table, note = "OK", ""
    elif Decimal(regen_v) == Decimal(exp_v):
        vs_table, note = "OK", f" [NOTATION_EQ: table={exp_v} vs json={regen_v}]"
    else:
        vs_table, note = "MISMATCH", f" [table={exp_v} vs json={regen_v}]"
    diff_paths = deep_diff(json.loads(regen_txt), json.loads(com_txt))
    diff_note = ",".join(diff_paths) if diff_paths else "IDENTICAL"
    ok = (vs_committed == "OK") and (vs_table == "OK")
    print(f"{rid}: regen={regen_v} committed={com_v} expected={exp_v} VS_COMMITTED_BIT_EXACT={vs_committed} VS_TABLE={vs_table}{note} JSON_DIFF={diff_note}")
    if ok: npass += 1
    else: nfail += 1

print("== SUMMARY ==")
print(f"P1_RAW_ANALYSIS_REPLAY = {npass}/20 PASS")
print(f"MEDIAN_MISMATCHES = {nfail}")
if nfail == 0 and npass == 20:
    print("P1_RAW_MEDIAN_REPLAY: ALL PASS")
else:
    print("P1_RAW_MEDIAN_REPLAY: FAILED")
    sys.exit(1)
PYEOF
rc=$?
echo "== DONE rc=$rc =="
exit $rc
