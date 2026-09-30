#!/bin/bash
# P1 packaged-convention analysis of all 20 primary replicas (EX-NL5-002-E-R1 leg P1).
# Run ON THE P1 MACHINE from the repo checkout. Only nanolab-components 0.1.1
# convention/analyze_hinge.py is used - no substitute analyzer.
set -u
WS=~/nanolab-platform-sensitivity-r1/P1
PKG=$WS/package
REPO=$(cd "$(dirname "$0")/../../.." && pwd)/docs/work/executions/EX-NL5-002-E-R1
[ -d "$PKG" ] || PKG=$WS/../package   # fallback layout variant
cd "$WS"

declare -A WINDOWS=( [0b]=200000 [32b]=150000 )
declare -A RUNS=(
  [0b]="PLATSENS-P1-0B-S001 PLATSENS-P1-0B-S002 PLATSENS-P1-0B-S003 PLATSENS-P1-0B-S004 PLATSENS-P1-0B-S005 PLATSENS-P1-0B-S006 PLATSENS-P1-0B-S007 PLATSENS-P1-0B-S008 PLATSENS-P1-0B-S009 PLATSENS-P1-0B-S010"
  [32b]="PLATSENS-P1-32B-S001 PLATSENS-P1-32B-S002 PLATSENS-P1-32B-S003 PLATSENS-P1-32B-S004 PLATSENS-P1-32B-S005 PLATSENS-P1-32B-S006 PLATSENS-P1-32B-S007 PLATSENS-P1-32B-S008 PLATSENS-P1-32B-S009 PLATSENS-P1-32B-S010"
)

mkdir -p analysis
for v in 0b 32b; do
  W=${WINDOWS[$v]}
  for rid in ${RUNS[$v]}; do
    RD="$WS/runs/$rid"
    [ -d "$RD" ] || { echo "$rid MISSING_RUN_DIR" | tee -a analysis/completeness.txt; continue; }
    last_t=$(grep "^t =" "$RD/traj.dat" | tail -1 | awk '{print $3}')
    nframes=$(grep -c "^t =" "$RD/traj.dat")
    last_step=$(python3 -c "print(int(round(float('$last_t')/0.005)))")
    echo "$rid frames=$nframes last_step=$last_step" | tee -a analysis/completeness.txt
    # formatted exit-code copy for the analyzer if the run dir keeps a bare integer
    if [ -f "$RD/exit_code.txt" ] && ! grep -q "EXIT_CODE:" "$RD/exit_code.txt"; then
      printf 'EXIT_CODE: %s\n' "$(tr -dc '0-9-' < "$RD/exit_code.txt")" > "$RD/exit_code_formatted.txt"
      ECF="$RD/exit_code_formatted.txt"
    else
      ECF="$RD/exit_code.txt"
    fi
    python3 "$PKG/convention/analyze_hinge.py" run \
      --trajectory "$RD/traj.dat" --energy "$RD/energy.dat" \
      --topology "$RD/$v.top" --manifest "$PKG/convention/arm-manifest-$v.json" \
      --variant "$v" --run-id "$rid" --window "$W" \
      --exit-code-file "$ECF" \
      --report "analysis/${rid}_analysis.json" > "analysis/${rid}_analysis_stdout.json" 2> "analysis/${rid}_analysis_stderr.txt"
    echo "analyze $rid exit=$?" | tee -a analysis/completeness.txt
  done
done
grep -c "analyze.*exit=0" analysis/completeness.txt
echo DONE
