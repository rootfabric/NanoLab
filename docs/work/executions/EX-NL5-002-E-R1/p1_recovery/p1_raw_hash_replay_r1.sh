#!/bin/bash
# P1 raw hash+size replay (EX-NL5-002-E-R1) — delegated step per
# docs/evidence/NL5-002-E/P1_RAW_REPLAY_COMMANDS_R1.md (authoritative; do not modify procedure).
# Read-only over raw run dirs: computes sha256+size of trajectory/energy/last_conf
# for the 20 final P1 attempts and compares against BOTH committed sources:
#   1) evidence/p1/run_output_digests_p1.json
#   2) P1_RAW_REPLAY_COMMANDS_R1.md table (mechanically extracted into
#      p1_recovery/p1_raw_replay_expectations_r1.json)
# No new physics runs, no retries, no recomputation of raw artifacts.
set -u
WS=~/nanolab-platform-sensitivity-r1/P1
PKG=$WS/package
REPO=${REPO:-/mnt/c/NanoLab/nl5-002-e-platform-r1}
EX=$REPO/docs/work/executions/EX-NL5-002-E-R1
[ -d "$PKG" ] || PKG=$WS/../package
cd "$WS"

echo "== P1_RAW_HASH_REPLAY_R1 =="
echo "host: $(hostname); utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "WS=$WS"
echo "PKG=$PKG"
echo "REPO=$REPO"

echo "== PIN CHECKS =="
echo "package VERSION: $(cat "$PKG/VERSION")"
PkgSha=$(sha256sum "$PKG/RELEASE_MANIFEST.json" | awk '{print $1}')
echo "RELEASE_MANIFEST.json sha256: $PkgSha"
if [ "$PkgSha" = "88c1f58061f15fde44225900f0577acbf2634d3f4a75fb96a2cedca24fd1bfef" ]; then
  echo "PIN package_manifest_sha256: OK"
else
  echo "PIN package_manifest_sha256: MISMATCH"
fi
EngSha=$(sha256sum "$WS/engine/build-oxdna-cpu/bin/oxDNA" | awk '{print $1}')
echo "engine binary sha256: $EngSha"
if [ "$EngSha" = "363356b9789fab8e0dab314bd66f92dc0e3a7e2cb3810e24b031614cebb45058" ]; then
  echo "PIN engine_binary_sha256: OK"
else
  echo "PIN engine_binary_sha256: MISMATCH"
fi

echo "== RAW HASH+SIZE REPLAY (disk vs digest JSON vs MD table) =="
DIGEST="$EX/evidence/p1/run_output_digests_p1.json" \
EXPECT="$EX/p1_recovery/p1_raw_replay_expectations_r1.json" \
python3 - <<'PYEOF'
import hashlib, json, os, sys

ws = os.path.expanduser("~/nanolab-platform-sensitivity-r1/P1")
digest = json.load(open(os.environ["DIGEST"]))
expect = json.load(open(os.environ["EXPECT"]))

runs = {r["final_attempt_id"]: r for r in digest["runs"]}
exp_by_final = {e["final_attempt"]: e for e in expect}

# 0) cross-check the two committed sources agree with each other
src_disagree = 0
for slot, e in sorted(exp_by_final.items()):
    r = runs.get(e["final_attempt"])
    if r is None:
        print(f"SOURCE_CHECK {slot}: MISSING_IN_DIGEST_JSON")
        src_disagree += 1
        continue
    for key, es, zs in (
        ("trajectory.dat", e["trajectory_sha256"], e["trajectory_size"]),
        ("hinge_energy.dat", e["hinge_energy_sha256"], e["hinge_energy_size"]),
        ("last_conf.dat", e["last_conf_sha256"], e["last_conf_size"]),
    ):
        a = r["artifacts"][key]
        if a["sha256"] != es or a["size_bytes"] != zs:
            print(f"SOURCE_CHECK {slot} {key}: digest_json_vs_md_table MISMATCH")
            src_disagree += 1
print(f"SOURCE_CHECK digest_json_vs_md_table: {'AGREE' if src_disagree == 0 else 'DISAGREE'} ({src_disagree} mismatches)")

disk_name = {"trajectory.dat": "trajectory.dat", "hinge_energy.dat": "hinge_energy.dat", "last_conf.dat": "last_conf.dat"}
alias = {"trajectory.dat": "traj.dat", "hinge_energy.dat": "energy.dat"}

hash_pass = size_pass = hash_fail = size_fail = 0
mismatch = False
for slot in sorted(exp_by_final):
    e = exp_by_final[slot]
    rid = e["final_attempt"]
    rd = os.path.join(ws, "runs", rid)
    print(f"-- {slot} final={rid}")
    if not os.path.isdir(rd):
        print(f"   RUN_DIR MISSING -> P1_RAW_EVIDENCE_MISMATCH")
        mismatch = True
        continue
    for key in ("trajectory.dat", "hinge_energy.dat", "last_conf.dat"):
        fn = os.path.join(rd, disk_name[key])
        if not os.path.exists(fn):
            print(f"   {disk_name[key]}: MISSING -> P1_RAW_EVIDENCE_MISMATCH")
            mismatch = True
            continue
        h = hashlib.sha256()
        size = 0
        with open(fn, "rb") as f:
            for chunk in iter(lambda: f.read(8 << 20), b""):
                h.update(chunk)
                size += len(chunk)
        got_sha, got_size = h.hexdigest(), size
        exp_sha = {"trajectory.dat": e["trajectory_sha256"], "hinge_energy.dat": e["hinge_energy_sha256"], "last_conf.dat": e["last_conf_sha256"]}[key]
        exp_size = {"trajectory.dat": e["trajectory_size"], "hinge_energy.dat": e["hinge_energy_size"], "last_conf.dat": e["last_conf_size"]}[key]
        art = runs[rid]["artifacts"][key]
        hs = "OK" if got_sha == art["sha256"] == exp_sha else "MISMATCH"
        ss = "OK" if got_size == art["size_bytes"] == exp_size else "MISMATCH"
        if hs == "OK": hash_pass += 1
        else: hash_fail += 1; mismatch = True
        if ss == "OK": size_pass += 1
        else: size_fail += 1; mismatch = True
        print(f"   {disk_name[key]}: sha256={got_sha} size={got_size} HASH={hs} SIZE={ss}")
        # dual-name alias check (instruction §2): if alias exists too, bytes must be identical
        al_name = alias.get(key)
        al = os.path.join(rd, al_name) if al_name else None
        if al and os.path.exists(al):
            ah = hashlib.sha256()
            asize = 0
            with open(al, "rb") as f:
                for chunk in iter(lambda: f.read(8 << 20), b""):
                    ah.update(chunk)
                    asize += len(chunk)
            same = (ah.hexdigest() == got_sha and asize == got_size)
            print(f"   [alias] {os.path.basename(al)}: sha256={ah.hexdigest()} size={asize} SAME_BYTES_AS_{disk_name[key]}={'YES' if same else 'NO'}")
            if not same:
                mismatch = True

print("== SUMMARY ==")
print(f"RAW_HASHES = {hash_pass}/60 PASS ({hash_fail} fail)")
print(f"RAW_SIZES  = {size_pass}/60 PASS ({size_fail} fail)")
if mismatch or src_disagree:
    print("P1_RAW_EVIDENCE_MISMATCH")
    sys.exit(1)
print("P1_RAW_EVIDENCE_REPLAY: ALL PASS")
PYEOF
rc=$?
echo "== DONE rc=$rc =="
exit $rc
