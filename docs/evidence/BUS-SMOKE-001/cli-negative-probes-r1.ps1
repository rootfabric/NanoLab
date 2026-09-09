# BUS-001 P1.2 fresh-reviewer CLI negative probes on a scratch remote.
$ErrorActionPreference = "Continue"
$log = "C:\NanoLab\review-bus-001\docs\evidence\BUS-SMOKE-001\cli-negative-probes-r1.log"
Remove-Item $log -ErrorAction SilentlyContinue
$root = Join-Path $env:TEMP ("bus-review-" + [guid]::NewGuid().ToString("N").Substring(0, 8))
New-Item -ItemType Directory $root | Out-Null
$tool = "C:\NanoLab\review-bus-001\tools\task_bus.py"

function Say($s) { $s | Tee-Object -FilePath $log -Append }
function Code { $LASTEXITCODE }

Say "=== BUS-001 fresh reviewer CLI probes $(Get-Date -Format o) ==="
Say "host: $(git --version) / $(python --version 2>&1) / Windows"
Say "scratch root: $root"

# --- env attribution: safe.bareRepository ---
$emptyCfg = Join-Path $root "empty-gitconfig"
"" | Out-File -NoNewline $emptyCfg
$bare = Join-Path $root "envtest.git"
git init --bare --initial-branch=main $bare *> $null
$withUser = git -C $bare rev-parse HEAD 2>&1 | Out-String
$c1 = Code
$env:GIT_CONFIG_GLOBAL = $emptyCfg
$withDefault = git -C $bare rev-parse HEAD 2>&1 | Out-String
$c2 = Code
Remove-Item Env:GIT_CONFIG_GLOBAL
Say "bare-repo access via -C with user gitconfig: exit=$c1 out=$($withUser.Trim())"
Say "bare-repo access via -C with empty global config: exit=$c2 out=$($withDefault.Trim())"
Say "user safe.bareRepository: $(git config --global --get safe.bareRepository)"

# --- fixtures ---
$remote = Join-Path $root "remote.git"
$seed = Join-Path $root "seed"
git init --bare --initial-branch=main $remote *> $null
git clone $remote $seed *> $null
git -C $seed config user.name probe
git -C $seed config user.email probe@invalid
Set-Content (Join-Path $seed "README.md") "probe seed"
git -C $seed add . *> $null
git -C $seed commit -m "seed" *> $null
git -C $seed push origin main *> $null
$base = git -C $seed rev-parse HEAD
Say "seed base: $base"

foreach ($a in @("dir", "ia", "ib", "ra")) {
  git clone -q $remote (Join-Path $root $a) 2>$null
  git -C (Join-Path $root $a) config user.name probe
  git -C (Join-Path $root $a) config user.email probe@invalid
}

$policy = Join-Path $root "policy.json"
@'
{"mode": "SANDBOX", "lease_seconds": 60, "max_claims": 8, "max_repairs": 2,
 "actors": {"director-pilot": {"role": "DIRECTOR", "capabilities": ["control"]},
            "implementer-a": {"role": "IMPLEMENTER", "capabilities": ["json"]},
            "implementer-b": {"role": "IMPLEMENTER", "capabilities": ["json"]},
            "reviewer-a": {"role": "REVIEWER", "capabilities": ["review"]},
            "verifier-a": {"role": "VERIFIER", "capabilities": ["python"]}}}
'@ | Set-Content $policy

$spec1 = Join-Path $root "spec1.json"
@'
{"id": "BUS-PROBE-1", "kind": "PILOT", "claim_class": "C0_SOFTWARE_ONLY",
 "base_sha": "SEEDBASE", "goal": "reviewer negative probes", "depends_on": [],
 "allowed_paths": ["docs/work/pilots/BUS-PROBE-1/receipt.json"],
 "capabilities": {"IMPLEMENTER": ["json"], "REVIEWER": ["review"],
                  "VERIFIER": ["python"], "DIRECTOR": ["control"]}}
'@ -replace "SEEDBASE", $base | Set-Content $spec1

function Bus($repo, $actor, $argz) {
  python $tool --repo (Join-Path $root $repo) --actor $actor @argz 2>&1 | Out-String
}
function Probe($name, $expected, $actualOut) {
  $c = Code
  $ok = if ($expected -is [string]) { ($actualOut -match $expected) -and ($c -eq 2) } else { $c -eq 0 }
  Say ("PROBE {0}: exit={1} expected={2} -> {3}" -f $name, $c, $expected, $(if ($ok) { "OK" } else { "UNEXPECTED: " + ($actualOut.Trim() -replace "`n", " | ") }))
  return $ok
}

$r = Bus "dir" "director-pilot" @("init", "--policy", $policy, "--base", $base); Say "init: exit=$(Code) $($r.Trim())"
$r = Bus "dir" "director-pilot" @("open", "--spec", $spec1); Say "open: exit=$(Code) $($r.Trim())"

# probe-dup-init
$r = Bus "dir" "director-pilot" @("init", "--policy", $policy, "--base", $base); Probe "dup-init" "BUS_ALREADY_EXISTS" $r | Out-Null
# probe-open-by-implementer
$r = Bus "ia" "implementer-a" @("open", "--spec", $spec1); Probe "open-by-implementer" "OPEN_DENIED" $r | Out-Null
# probe-unknown-actor
$r = Bus "ib" "ghost-x" @("claim", "BUS-PROBE-1"); Probe "unknown-actor" "ACTOR_NOT_ALLOWED" $r | Out-Null
# probe-wrong-role-claim
$r = Bus "ra" "reviewer-a" @("claim", "BUS-PROBE-1"); Probe "wrong-role-claim" "TASK_NOT_CLAIMABLE" $r | Out-Null

# valid claim by implementer-a
$r = Bus "ia" "implementer-a" @("claim", "BUS-PROBE-1"); Say "claim-a: exit=$(Code)"
$receipt = Get-Content (Join-Path $root "ia/.git/task-bus-receipts/implementer-a/BUS-PROBE-1.json") | ConvertFrom-Json
$token = $receipt.token
Say "token: $token"

# probe-competing-claim
$r = Bus "ib" "implementer-b" @("claim", "BUS-PROBE-1"); Probe "competing-claim" "TASK_NOT_CLAIMABLE" $r | Out-Null
# probe-foreign-token (stolen token, wrong actor)
$r = Bus "ib" "implementer-b" @("finish", "BUS-PROBE-1", "--token", $token, "--report", (Join-Path $root "r.json")); Probe "foreign-actor-with-stolen-token" "STALE_OR_FOREIGN_LEASE" $r | Out-Null
# probe-wrong-token heartbeat
$r = Bus "ia" "implementer-a" @("heartbeat", "BUS-PROBE-1", "--token", ("f" * 32)); Probe "wrong-token-heartbeat" "STALE_OR_FOREIGN_LEASE" $r | Out-Null
# probe-heartbeat-without-receipt-and-token
$r = Bus "ib" "implementer-b" @("heartbeat", "BUS-PROBE-1"); Probe "heartbeat-no-receipt" "BusError|error" $r | Out-Null
# probe-early-reclaim
$r = Bus "dir" "director-pilot" @("reclaim", "BUS-PROBE-1", "--reason", "too early"); Probe "early-reclaim" "LEASE_NOT_EXPIRED" $r | Out-Null
# probe-pass-with-failed-check
$badReport = Join-Path $root "bad-report.json"
@'
{"subject_head": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", "subject_tree": "cccccccccccccccccccccccccccccccccccccccc",
 "verdict": "PASS", "summary": "probe", "checks": [{"command": "probe", "exit_code": 1}]}
'@ | Set-Content $badReport
$r = Bus "ia" "implementer-a" @("finish", "BUS-PROBE-1", "--candidate-ref", "work/nope", "--report", $badReport); Probe "pass-with-failed-check" "PASS_WITH_FAILED_CHECK" $r | Out-Null

# positive control: real candidate
git -C $seed checkout -q -b work/probe-1-r1
New-Item -ItemType Directory -Force (Join-Path $seed "docs/work/pilots/BUS-PROBE-1") | Out-Null
Set-Content (Join-Path $seed "docs/work/pilots/BUS-PROBE-1/receipt.json") '{"schema_version": 1, "probe": true}'
git -C $seed add . *> $null
git -C $seed commit -q -m "probe candidate"
git -C $seed push -q origin work/probe-1-r1 2>$null
$cHead = git -C $seed rev-parse HEAD
$cTree = git -C $seed rev-parse 'HEAD^{tree}'
$goodReport = Join-Path $root "good-report.json"
@'
{"subject_head": "HEADX", "subject_tree": "TREEX", "verdict": "PASS", "summary": "positive control",
 "checks": [{"command": "probe assertion", "exit_code": 0}]}
'@ -replace "HEADX", $cHead -replace "TREEX", $cTree | Set-Content $goodReport
$r = Bus "ia" "implementer-a" @("finish", "BUS-PROBE-1", "--candidate-ref", "work/probe-1-r1", "--report", $goodReport); Say "finish-a-positive: exit=$(Code)"

# probe-reviewer-claim ok
$r = Bus "ra" "reviewer-a" @("claim", "BUS-PROBE-1"); Say "claim-reviewer: exit=$(Code)"
# probe-reviewer-subject-drift
$driftReport = Join-Path $root "drift-report.json"
@'
{"subject_head": "dddddddddddddddddddddddddddddddddddddddd", "subject_tree": "TREEX", "verdict": "PASS",
 "summary": "drift probe", "checks": [{"command": "probe assertion", "exit_code": 0}]}
'@ -replace "TREEX", $cTree | Set-Content $driftReport
$r = Bus "ra" "reviewer-a" @("finish", "BUS-PROBE-1", "--report", $driftReport); Probe "reviewer-subject-drift" "SUBJECT_MISMATCH" $r | Out-Null
# probe-reviewer-pass ok
$r = Bus "ra" "reviewer-a" @("finish", "BUS-PROBE-1", "--report", $goodReport); Say "finish-reviewer-positive: exit=$(Code)"

# probe-candidate-ref-drift at verifier stage
$ver = Join-Path $root "ver"
git clone -q $remote $ver 2>$null
git -C $ver config user.name probe; git -C $ver config user.email probe@invalid
$r = Bus "ver" "verifier-a" @("claim", "BUS-PROBE-1"); Say "claim-verifier: exit=$(Code)"
git -C $seed commit -q --allow-empty --amend --no-edit 2>$null
git -C $seed push -q -f origin work/probe-1-r1 2>$null
$r = Bus "ver" "verifier-a" @("finish", "BUS-PROBE-1", "--report", $goodReport); Probe "candidate-ref-drift" "CANDIDATE_REF_DRIFT" $r | Out-Null

# probe-claim-race: two simultaneous CLI claims on a second task
$spec2 = Join-Path $root "spec2.json"
(@'
{"id": "BUS-PROBE-2", "kind": "PILOT", "claim_class": "C0_SOFTWARE_ONLY",
 "base_sha": "SEEDBASE", "goal": "race probe", "depends_on": [],
 "allowed_paths": ["docs/work/pilots/BUS-PROBE-2/receipt.json"],
 "capabilities": {"IMPLEMENTER": ["json"], "REVIEWER": ["review"],
                  "VERIFIER": ["python"], "DIRECTOR": ["control"]}}
'@ -replace "SEEDBASE", $base) | Set-Content $spec2
$r = Bus "dir" "director-pilot" @("open", "--spec", $spec2); Say "open-2: exit=$(Code)"
$o1 = Join-Path $root "o1.txt"; $e1 = Join-Path $root "e1.txt"
$o2 = Join-Path $root "o2.txt"; $e2 = Join-Path $root "e2.txt"
$p1 = Start-Process -FilePath python -ArgumentList @($tool, "--repo", (Join-Path $root "ia"), "--actor", "implementer-a", "claim", "BUS-PROBE-2") -PassThru -NoNewWindow -RedirectStandardOutput $o1 -RedirectStandardError $e1
$p2 = Start-Process -FilePath python -ArgumentList @($tool, "--repo", (Join-Path $root "ib"), "--actor", "implementer-b", "claim", "BUS-PROBE-2") -PassThru -NoNewWindow -RedirectStandardOutput $o2 -RedirectStandardError $e2
$p1.WaitForExit(); $p2.WaitForExit()
$winners = @($p1.ExitCode, $p2.ExitCode) | Where-Object { $_ -eq 0 }
$losers = @()
foreach ($f in @($e1, $e2)) { if ((Get-Item $f).Length -gt 0) { $losers += (Get-Content $f -Raw).Trim() } }
Say ("PROBE cli-claim-race: winner exits: a={0} b={1} winners={2} -> {3}" -f $p1.ExitCode, $p2.ExitCode, $winners.Count, $(if ($winners.Count -eq 1) { "OK (single winner)" } else { "UNEXPECTED" }))
Say ("  loser stderr: " + ($losers -join " || "))

# journal integrity: fresh replay via status
$r = Bus "dir" "director-pilot" @("status"); Say "final-status: exit=$(Code)"
$queue = git --git-dir=$remote show refs/heads/control/task-bus-pilot-r1:task-bus/queue.json | Out-String
$tmpq = Join-Path $root "queue.json"
Set-Content $tmpq $queue
$events = python -c "import json,sys; print(len(json.load(open(sys.argv[1], encoding='utf-8'))['events']))" $tmpq
Say "journal events after all probes: $($events.Trim())"
Say "scratch root kept for inspection: $root"
Say "=== end of probes ==="
