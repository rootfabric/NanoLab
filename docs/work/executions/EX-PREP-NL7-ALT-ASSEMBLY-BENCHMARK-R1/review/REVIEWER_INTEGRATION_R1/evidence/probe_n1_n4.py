import json, subprocess, sys, tempfile, os
from pathlib import Path
ROOT = Path('/home/rdpuser/NanoLab-review76')
def run(manifest_text, candidate="S23_NARCISSUS_ECHO"):
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
        f.write(manifest_text); p = f.name
    r = subprocess.run([sys.executable, '-m', 'knowledge_pack.alt_pair_source_gate', p,
                        '--candidate', candidate, '--root', str(ROOT)],
                       capture_output=True, text=True, env={**os.environ, 'PYTHONPATH': str(ROOT/'scripts')})
    os.unlink(p)
    return r
# N1: non-dict roots
for name, m in [("empty_list","[]"), ("string",'"str"'), ("null","null")]:
    r = run(m)
    tb = "AttributeError" in r.stderr
    print(f"N1 {name}: exit={r.returncode} attributeerror_in_traceback={tb} fail_open={'NO' if r.returncode!=0 else 'YES!'}")
# N4: CONTENT_VERIFIED path './x' traversal nuance (path normalization)
pack = json.loads((ROOT/'docs/research/ALT_DNA_TWO_PART_SOURCE_PACK_R1.json').read_text())
cand = next(c for c in pack['candidates'] if c['candidate_id']=='S23_NARCISSUS_ECHO')
top_rec = cand['parts'][0]['topology']
orig_path = top_rec['path']
top_rec.update(status='CONTENT_VERIFIED', path='./'+str(orig_path), sha256='0'*64, size_bytes=1, source_url='https://example.org/x', rights='ALLOWED')
r = run(json.dumps(pack))
out = json.loads(r.stdout or '{}')
reasons = ' | '.join(out.get('reasons', []))
print(f"N4 dot-slash path: exit={r.returncode} outcome={out.get('outcome')}")
print(f"   reasons mentioning path/bytes: {[x for x in out.get('reasons',[]) if 'topology' in x][:3]}")
