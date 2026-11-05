"""One explicitly authorized UI calculation, invoked in a frozen clean source worktree."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import threading
import zipfile

from atomistic.web import LocalApp, make_server, DEFAULT_CONFIG
from atomistic.api import verify_run, validate_config

root = Path('/workspace/scratch/48cb7a65c9c0/ui-real-runs')
evidence = Path('/workspace/scratch/48cb7a65c9c0/ui-real-evidence')
evidence.mkdir(exist_ok=True)
head = subprocess.check_output(['git','rev-parse','HEAD'], text=True).strip()
tree = subprocess.check_output(['git','rev-parse','HEAD^{tree}'], text=True).strip()
if subprocess.check_output(['git','status','--porcelain'],text=True).strip():
    raise RuntimeError('UI smoke requires a clean exact worktree')
requested = json.loads(json.dumps(DEFAULT_CONFIG))
requested['md'].update(steps=10,sample_interval=2)
(evidence/'requested-config.json').write_text(json.dumps(validate_config(requested),indent=2)+'\n')
app = LocalApp(root)
server = make_server(app, 8765)
threading.Thread(target=server.serve_forever, daemon=True).start()
script = r'''
const fs=require('fs');
const {chromium}=require(process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES+'/playwright');
(async()=>{
 const b=await chromium.launch({executablePath:'/workspace/scratch/48cb7a65c9c0/sparticuz/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--disable-gpu']});
 try{
 const p=await b.newPage({viewport:{width:1440,height:1100}}), errors=[];
 p.on('pageerror',e=>errors.push(e.message));
 await p.goto('http://127.0.0.1:8765');
 await p.locator('#steps').fill('10'); await p.locator('#interval').fill('2');
 const formValid=await p.locator('form').evaluate(e=>e.checkValidity());
 if(!formValid)throw Error('Invalid form defaults');
 const request=p.waitForResponse(r=>r.url().endsWith('/api/run')&&r.request().method()==='POST');
 await p.getByRole('button',{name:'Запустить расчёт'}).click();
 const response=await request;
 const launch={status:response.status(),url:response.url(),body:await response.json()};
 if(launch.status!==202)throw Error(JSON.stringify(launch));
 await p.getByText('Расчёт завершён',{exact:true}).waitFor({timeout:130000});
 await p.locator('#export:not(.disabled)').waitFor({timeout:5000});
 const first=await p.locator('#frame-info').textContent();
 await p.getByRole('button',{name:'Воспроизвести траекторию'}).click();
 await p.waitForFunction(initial=>document.getElementById('frame-info').textContent!==initial,first);
 await p.getByRole('button',{name:'Воспроизвести траекторию'}).click();
 const after=await p.locator('#frame-info').textContent();
 await p.locator('#frame').press('End');
 const box=await p.locator('#viewer').boundingBox();
 await p.mouse.move(box.x+box.width/2,box.y+box.height/2);await p.mouse.down();
 await p.mouse.move(box.x+box.width/2+50,box.y+box.height/2+20,{steps:4});await p.mouse.up();
 await p.mouse.wheel(0,-120);
 await p.screenshot({path:'/workspace/scratch/48cb7a65c9c0/ui-real-evidence/ui-real.png',fullPage:true});
 const download=p.waitForEvent('download');
 await p.getByRole('link',{name:'Скачать результат'}).click();
 await (await download).saveAs('/workspace/scratch/48cb7a65c9c0/ui-real-evidence/result.zip');
 const stateResponse=await p.request.get('http://127.0.0.1:8765/api/state');
 const state=await stateResponse.json(); delete state.token;
 const summary={launch,state,formValid,firstFrame:first,afterPlayback:after,selectedFrame:await p.locator('#frame-info').textContent(),pageErrors:errors};
 fs.writeFileSync('/workspace/scratch/48cb7a65c9c0/ui-real-evidence/http-ui.json',JSON.stringify(summary,null,2)+'\n');
 if(errors.length)throw Error(JSON.stringify(errors));
 console.log(JSON.stringify(summary));
 }finally{await b.close();}
})().catch(e=>{console.error(e);process.exit(1)});
'''
try:
    run = subprocess.run(['node','-e',script],text=True,capture_output=True,timeout=150)
    (evidence/'browser.log').write_text(run.stdout+run.stderr)
    print(run.stdout,run.stderr)
    if run.returncode:
        raise RuntimeError('Browser smoke failed; no automatic rerun')
    job=app.snapshot()['job']
    manifest=verify_run(root/job['run_id'])
    with zipfile.ZipFile(evidence/'result.zip') as archive:
        extracted=evidence/'exported'
        extracted.mkdir(exist_ok=False)
        archive.extractall(extracted)
        recovered=verify_run(extracted)
    files={p.name:{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size_bytes':p.stat().st_size} for p in evidence.iterdir() if p.is_file()}
    summary={'source_head':head,'source_tree':tree,'run_id':job['run_id'],'run_dir':str(root/job['run_id']), 'manifest_status':manifest['status'],'wall_seconds':manifest['wall_seconds'],'export_verified_run_id':recovered['run_id'],'claim_ceiling':manifest['claim_ceiling'],'files':files}
    (evidence/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
finally:
    app.stop()
    if app.worker: app.worker.join(8)
    server.shutdown();server.server_close()
