"use strict";
const $ = id => document.getElementById(id);
let token = "", trajectory = null, frames = [], current = 0, playing = false, loadedRun = null;
let yaw = .55, pitch = -.35, zoom = 1, dragging = null;
let polling = false;
const value = id => Number($(id).value);
function config() {
  return {schema_version:"atomistic-config-v1",material:"Cu",model:"ASE_EMT_Cu",structure:{kind:"fcc_cuboid",size:[value("nx"),value("ny"),value("nz")],lattice_constant_angstrom:value("lattice")},relaxation:{max_steps:value("relax"),fmax_ev_per_angstrom:value("fmax")},md:{steps:value("steps"),timestep_fs:value("timestep"),temperature_k:value("temperature"),sample_interval:value("interval"),friction_per_fs:value("friction"),seed:value("seed")}};
}
function error(message) { $("error").textContent=message; $("error").hidden=!message; }
async function api(path, payload) {
  const options = payload === undefined ? {} : {method:"POST",headers:{"Content-Type":"application/json","X-NanoLab-Token":token},body:JSON.stringify(payload)};
  const response = await fetch(path,options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Ошибка локального сервера");
  return data;
}
function download(name, data) {
  const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:"application/json"}));
  const link=document.createElement("a"); link.href=url; link.download=name; link.click(); setTimeout(()=>URL.revokeObjectURL(url),1000);
}
$("config-form").addEventListener("input",()=>{$("atom-count").textContent=4*value("nx")*value("ny")*value("nz");});
$("config-form").addEventListener("submit",async event=>{
  event.preventDefault(); error(""); $("run").disabled=true;
  try { await api("/api/run",config()); loadedRun=null; clearTrajectory(); await poll(); }
  catch (e) { error(e.message); $("run").disabled=false; }
});
$("stop").addEventListener("click",async()=>{try{await api("/api/stop",{});await poll();}catch(e){error(e.message);}});
$("save-config").addEventListener("click",()=>{if($("config-form").reportValidity())download("nanolab-config.json",config());});
$("export").addEventListener("click",event=>{if($("export").getAttribute("aria-disabled")==="true")event.preventDefault();});
function clearTrajectory(){
  playing=false;trajectory=null;frames=[];current=0;$("play").textContent="▶";$("play").disabled=true;$("frame").disabled=true;$("frame").value=0;$("frame-info").textContent="Нет кадров";$("empty").hidden=false;$("metadata").textContent="Результат ещё не готов.";
  for(const id of ["atoms-metric","time-metric","energy-metric","temp-metric"])$(id).textContent="—";
  $("export").classList.add("disabled");$("export").setAttribute("aria-disabled","true");draw();drawEnergy();
}
async function poll(){
  if(polling)return; polling=true;
  try{
    const state=await api("/api/state");token=state.token;
    const job=state.job, active=job&&["running","stopping"].includes(job.status);
    if(job&&loadedRun&&loadedRun!==job.run_id){clearTrajectory();loadedRun=null;}
    $("run").disabled=Boolean(active)||state.runs_started>=state.max_runs||state.compute_seconds>=1200;$("stop").disabled=!active||job.status==="stopping";
    const labels={running:"Выполняется расчёт",stopping:"Остановка расчёта…",completed:"Расчёт завершён",failed:"Расчёт завершился ошибкой",cancelled:"Расчёт остановлен",aborted:"Расчёт прерван"};
    $("status").textContent=job?(labels[job.status]||job.status):"Готов к расчёту";$("status-dot").className="status-dot "+(job?job.status:"");
    $("status-detail").textContent=job?`${job.run_id} · ${job.elapsed_seconds||0} с · запуск ${state.runs_started}/${state.max_runs}${active?" · backend: релаксация / MD (процент недоступен)":""}`:"Результаты появятся после запуска backend.";
    if(job&&job.error)error(job.error);
    if(job&&job.status==="completed"&&loadedRun!==job.run_id){
      const [data,metrics,manifest]=await Promise.all([api("/api/trajectory"),api("/api/metrics"),api("/api/manifest")]);
      if(!Array.isArray(data.frames)||!data.frames.length)throw new Error("Backend вернул пустую траекторию.");
      trajectory=data;frames=data.frames;current=0;loadedRun=job.run_id;$("empty").hidden=true;$("frame").max=frames.length-1;$("frame").disabled=false;$("play").disabled=frames.length<2;
      $("metadata").textContent=JSON.stringify({metrics,manifest},null,2);$("export").classList.remove("disabled");$("export").setAttribute("aria-disabled","false");showFrame(0);
    }
  }catch(e){error(e.message);}finally{polling=false;}
}
function canvasSize(canvas){
 const box=canvas.getBoundingClientRect(),ratio=window.devicePixelRatio||1;
 if(canvas.width!==Math.round(box.width*ratio)||canvas.height!==Math.round(box.height*ratio)){canvas.width=Math.round(box.width*ratio);canvas.height=Math.round(box.height*ratio);}
 const ctx=canvas.getContext("2d");ctx.setTransform(ratio,0,0,ratio,0,0);return {ctx,w:box.width,h:box.height};
}
function draw(){
 const {ctx,w,h}=canvasSize($("viewer"));ctx.clearRect(0,0,w,h);
 if(!frames.length)return;
 const positions=frames[current].positions_angstrom;
 // Keep the origin/scale fixed to frame 0, so the camera does not hide motion.
 const initial=frames[0].positions_angstrom;
 const center=[0,1,2].map(k=>initial.reduce((s,p)=>s+p[k],0)/initial.length);
 const radius=Math.max(2,...initial.map(p=>Math.hypot(...p.map((x,k)=>x-center[k]))));
 const scale=Math.min(w,h)*.34/radius*zoom;
 const rotate=p=>{const x=p[0]-center[0],y=p[1]-center[1],z=p[2]-center[2];const a=x*Math.cos(yaw)+z*Math.sin(yaw),b=-x*Math.sin(yaw)+z*Math.cos(yaw);return [a,y*Math.cos(pitch)-b*Math.sin(pitch),y*Math.sin(pitch)+b*Math.cos(pitch)];};
 const projected=positions.map((p,i)=>({p:rotate(p),i})).sort((a,b)=>a.p[2]-b.p[2]);
 for(const {p} of projected){const x=w/2+p[0]*scale,y=h/2-p[1]*scale,r=Math.max(2.3,Math.min(12,scale*.32));const gradient=ctx.createRadialGradient(x-r*.3,y-r*.4,r*.1,x,y,r);gradient.addColorStop(0,"#ffe0b5");gradient.addColorStop(.4,"#d9905d");gradient.addColorStop(1,"#794530");ctx.fillStyle=gradient;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();}
 // Small orientation triad (no bonds are inferred).
 const origin=[38,h-52];for(const [vec,label,color] of [[[1,0,0],"X","#df8e79"],[[0,1,0],"Y","#8cbaa2"],[[0,0,1],"Z","#7ca6cc"]]){const v=rotate(vec.map((x,k)=>x+center[k]));ctx.strokeStyle=color;ctx.fillStyle=color;ctx.lineWidth=1.5;ctx.beginPath();ctx.moveTo(...origin);ctx.lineTo(origin[0]+v[0]*23,origin[1]-v[1]*23);ctx.stroke();ctx.font="9px system-ui";ctx.fillText(label,origin[0]+v[0]*30-3,origin[1]-v[1]*30+3);}
}
function drawEnergy(){
 const {ctx,w,h}=canvasSize($("energy"));ctx.clearRect(0,0,w,h);const left=61,right=w-19,top=17,bottom=h-32;
 ctx.strokeStyle="#e7eef1";ctx.fillStyle="#81939e";ctx.font="9px system-ui";
 if(!frames.length){ctx.fillText("График появится после расчёта",left,h/2);return;}
 const series=[frames.map(f=>f.potential_energy_ev),frames.map(f=>f.potential_energy_ev+f.kinetic_energy_ev)];
 let min=Math.min(...series.flat()),max=Math.max(...series.flat());const padding=Math.max((max-min)*.12,.01);min-=padding;max+=padding;const end=Math.max(1,...frames.map(f=>f.time_fs));
 const x=f=>left+f.time_fs/end*(right-left),y=e=>bottom-(e-min)/(max-min)*(bottom-top);
 for(let i=0;i<4;i++){const val=min+(max-min)*i/3,py=y(val);ctx.beginPath();ctx.moveTo(left,py);ctx.lineTo(right,py);ctx.stroke();ctx.fillText(val.toFixed(2),5,py+3);}
 for(let i=0;i<4;i++){const t=end*i/3;ctx.fillText(t.toFixed(1),left+t/end*(right-left)-8,bottom+16);}ctx.fillText("фс",right-9,bottom+29);ctx.fillText("эВ",9,12);
 series.forEach((values,j)=>{ctx.strokeStyle=j?"#ba8756":"#087e87";ctx.lineWidth=1.8;ctx.beginPath();values.forEach((v,i)=>i?ctx.lineTo(x(frames[i]),y(v)):ctx.moveTo(x(frames[i]),y(v)));ctx.stroke();if(values.length===1){ctx.beginPath();ctx.arc(x(frames[0]),y(values[0]),3,0,Math.PI*2);ctx.fillStyle=ctx.strokeStyle;ctx.fill();}});
 ctx.strokeStyle="#8da6b3";ctx.setLineDash([3,3]);ctx.beginPath();ctx.moveTo(x(frames[current]),top);ctx.lineTo(x(frames[current]),bottom);ctx.stroke();ctx.setLineDash([]);
}
function showFrame(index){
 current=Math.max(0,Math.min(frames.length-1,index));if(!frames.length)return;
 const f=frames[current];$("frame").value=current;$("frame-info").textContent=`${current+1}/${frames.length} · ${f.time_fs.toFixed(1)} фс`;
 $("atoms-metric").textContent=trajectory.atom_count;$("time-metric").textContent=f.time_fs.toFixed(1);$("energy-metric").textContent=f.potential_energy_ev.toFixed(3);$("temp-metric").textContent=f.temperature_k.toFixed(1);draw();drawEnergy();
}
$("frame").addEventListener("input",()=>showFrame(value("frame")));
$("play").addEventListener("click",()=>{playing=!playing;$("play").textContent=playing?"Ⅱ":"▶";});
setInterval(()=>{if(playing&&frames.length)showFrame((current+1)%frames.length);},140);
$("reset-view").addEventListener("click",()=>{yaw=.55;pitch=-.35;zoom=1;draw();});
$("viewer").addEventListener("pointerdown",e=>{dragging=[e.clientX,e.clientY];$("viewer").setPointerCapture(e.pointerId);});
$("viewer").addEventListener("pointermove",e=>{if(!dragging)return;yaw+=(e.clientX-dragging[0])*.009;pitch+=(e.clientY-dragging[1])*.009;dragging=[e.clientX,e.clientY];draw();});
for(const event of ["pointerup","pointercancel"])$("viewer").addEventListener(event,()=>{dragging=null;});
$("viewer").addEventListener("wheel",e=>{e.preventDefault();zoom=Math.max(.2,Math.min(5,zoom*Math.exp(-e.deltaY*.001)));draw();},{passive:false});
window.addEventListener("resize",()=>{draw();drawEnergy();});
poll();drawEnergy();setInterval(poll,1000);
