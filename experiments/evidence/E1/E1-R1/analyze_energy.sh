#!/usr/bin/env bash
# E1-PROTO-R1 §5.1 mechanical analysis: arithmetic mean of column 2 of energy.dat
# over ALL rows of the run (including initial row). No thresholds applied here;
# the upstream oracle comparison is reported as a fact.
# Usage: analyze_energy.sh <path-to-energy.dat>
set -euo pipefail
f="$1"
rows=$(wc -l < "$f")
# integrity: NaN/Inf must not exist (E1-PROTO-R1 §5.2)
if grep -qiE '(^|[^a-z])(nan|inf)([^a-z]|$)' "$f"; then echo "NAN_INF_FOUND"; exit 3; fi
awk -v rows="$rows" '{ s += $2; n++ } END {
  avg = s / n
  printf "rows=%d\navg_col2=%.11f\n", n, avg
  # upstream oracle (verbatim from pinned quick_compare, SHA-256 in protocol.json):
  oracle = -1.37970256144; band = 0.15
  d = avg - oracle; if (d < 0) d = -d
  if (d <= band) print "T1_band=IN_BAND" ; else print "T1_band=OUT_OF_BAND"
  printf "delta_from_oracle=%.11f\n", avg - oracle
}' "$f"
