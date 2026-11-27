/* ENDURACE LAB · calculadoras compartidas (laboratorio y páginas de cada calculadora).
   Cada herramienta se activa solo si su marcado está en la página. Todo ocurre en el navegador. */
(() => {
const $=s=>document.querySelector(s);
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
/* ===== Utilidades de las calculadoras ===== */
const ps=s=>{s=String(s).trim();const p=s.split(":").map(Number);return s&&p.every(x=>!isNaN(x))?p.reduce((a,v)=>a*60+v,0):0};
const ft=s=>{s=Math.round(s);const h=Math.floor(s/3600),m=Math.floor(s%3600/60),x=s%60;return(h?h+":"+String(m).padStart(2,"0"):m)+":"+String(x).padStart(2,"0")};
const fill=el=>el.style.setProperty("--p",((el.value-el.min)/(el.max-el.min)*100)+"%");
function chips(id,cb){const box=$(id);box.querySelectorAll("button").forEach(b=>b.addEventListener("click",()=>{box.querySelectorAll("button").forEach(x=>x.setAttribute("aria-checked",String(x===b)));cb(b)}))}
const chosen=id=>$(id).querySelector('[aria-checked="true"]');


if($("#ptr")){
/* ===== Predictor de tiempos (Riegel) ===== */
const DIST=[[5,"5K"],[10,"10K"],[21.0975,"Media maratón"],[42.195,"Maratón"]];
const PRANGE={5:[840,3000],10:[1800,6300],21.0975:[3900,12600],42.195:[8100,25200]};
let pdist=10;
function setPredRange(t){const r=PRANGE[pdist],s=$("#ptr");s.min=r[0];s.max=r[1];s.value=Math.min(r[1],Math.max(r[0],t));fill(s)}
function pred(){const t=ps($("#pt").value);
if(!t){$("#pr").innerHTML='<p class="ctl-help">Escribe un tiempo válido, por ejemplo 45:00 o 1:39:30.</p>';$("#pt-pace").textContent="";return}
$("#pt-pace").textContent=ft(t/pdist)+" /km";
$("#pr").innerHTML=DIST.map(([k,n])=>{const T=t*Math.pow(k/pdist,1.06),me=k==pdist;
return`<div class="rcard${me?" me":""}"><span class="rk">${me?"TU MARCA":n.toUpperCase()}</span><b>${ft(T)}</b><span class="rs">${me?n+" · ":""}${ft(T/k)} /km</span></div>`}).join("")}
chips("#pd",b=>{const old=pdist,t=ps($("#pt").value);pdist=+b.dataset.d;
const nt=t?Math.round(t*Math.pow(pdist/old,1.06)/5)*5:PRANGE[pdist][0]*1.5;$("#pt").value=ft(nt);setPredRange(nt);pred()});
$("#ptr").addEventListener("input",e=>{fill(e.target);$("#pt").value=ft(+e.target.value);pred()});
$("#pt").addEventListener("input",()=>{const t=ps($("#pt").value);if(t)setPredRange(t);pred()});

setPredRange(2700);pred();
}
if($("#zl")){
/* ===== Zonas ===== */
let zk="hr";
const zrow=(name,range,w,i)=>`<div class="zrow z${i}"><span class="zn">${name}</span><span class="zbar"><i style="width:${w}%"></i></span><span class="zv">${range}</span></div>`;
function zones(){["fm","fr","rt","ftp"].forEach(id=>fill($("#"+id)));
const fm=+$("#fm").value,fr=+$("#fr").value,rt=+$("#rt").value,f=+$("#ftp").value;
$("#fm-o").textContent=fm;$("#fr-o").textContent=fr;$("#rt-o").textContent=ft(rt);$("#ftp-o").textContent=f;
let h="";
if(zk=="hr"){h=[[50,60,"Z1 · Recuperación"],[60,70,"Z2 · Aeróbica"],[70,80,"Z3 · Tempo"],[80,90,"Z4 · Umbral"],[90,100,"Z5 · Máxima"]].map((z,i)=>zrow(z[2],Math.round(fr+z[0]/100*(fm-fr))+"–"+Math.round(fr+z[1]/100*(fm-fr))+" ppm",z[1],i)).join("")}
else if(zk=="pace"){h=[["Z1 · Recuperación","más lento de "+ft(rt*1.29),40],["Z2 · Aeróbica",ft(rt*1.29)+" – "+ft(rt*1.14),55],["Z3 · Tempo",ft(rt*1.13)+" – "+ft(rt*1.06),70],["Z4 · Umbral",ft(rt*1.05)+" – "+ft(rt),85],["Z5 · Intensa","más rápido de "+ft(rt),100]].map((z,i)=>zrow(z[0],z[1]+" /km",z[2],i)).join("")}
else{h=[[0,55,"Z1 · Recuperación"],[56,75,"Z2 · Resistencia"],[76,90,"Z3 · Tempo"],[91,105,"Z4 · Umbral"],[106,120,"Z5 · VO2máx"],[121,150,"Z6 · Anaeróbica"]].map((z,i)=>zrow(z[2],(z[0]?Math.round(f*z[0]/100)+"–":"hasta ")+Math.round(f*z[1]/100)+" W",z[1]/1.5,Math.min(i,4))).join("")}
$("#zl").innerHTML=h}
chips("#zk",b=>{zk=b.dataset.k;document.querySelectorAll("#p-zonas .tool-controls>[data-k]").forEach(d=>d.hidden=d.dataset.k!=zk);zones()});
["fm","fr","rt","ftp"].forEach(id=>$("#"+id).addEventListener("input",()=>{if(+$("#fr").value>=+$("#fm").value-40)$("#fr").value=+$("#fm").value-40;zones()}));

zones();
}
if($("#nt")){
/* ===== Nutrición en carrera ===== */
const dur=d=>{const h=Math.floor(d),m=Math.round((d-h)*60);return(h?h+" h":"")+(m?(h?" ":"")+m+" min":"")};
function nutri(){const s=$("#nd");fill(s);const d=+s.value,c=+chosen("#nc").dataset.c;$("#nd-o").textContent=dur(d);
const H=d<1?[0,30]:d<=2.5?[30,60]:[60,90],L=[[400,500],[500,700],[600,800]][c],N=[300,600];
const tot=(r,u)=>Math.round(r[0]*d).toLocaleString("es-ES")+"–"+Math.round(r[1]*d).toLocaleString("es-ES")+" "+u;
const card=(k,r,u)=>`<div class="rcard"><span class="rk">${k}</span><b>${r[0]}–${r[1]}<small> ${u}/h</small></b><span class="rs">Total: ${tot(r,u)}</span></div>`;
$("#nt").innerHTML=card("HIDRATOS",H,"g")+card("LÍQUIDO",L,"ml")+card("SODIO",N,"mg");
$("#ne").innerHTML=H[1]?`<b>Cada 20 minutos:</b> ${Math.round(H[0]/3)}–${Math.round(H[1]/3)} g de hidratos y ${Math.round(L[0]/3)}–${Math.round(L[1]/3)} ml de líquido. Empieza pronto, antes de tener hambre o sed.`:"<b>En menos de una hora</b> no suele hacer falta comer: basta con llegar bien desayunado e hidratado."}
$("#nd").addEventListener("input",nutri);chips("#nc",nutri);

nutri();
}
if($("#co")){
/* ===== Cuenta atrás ===== */
const CDK={corta:{n:"5K–10K",t:1,s:4,b:6},media:{n:"media maratón",t:2,s:5,b:7},maraton:{n:"maratón",t:3,s:6,b:8},h70:{n:"medio Ironman",t:2,s:6,b:8},im:{n:"Ironman",t:3,s:8,b:10}};
const PH=[["BASE","Volumen suave y constancia: construye el motor aeróbico y la fuerza. La intensidad, con moderación."],["DESARROLLO","Sube la carga poco a poco, sin saltos de más del 10 % por semana, e introduce trabajo de umbral."],["ESPECÍFICO","Entrena a ritmo de carrera y prueba tu nutrición y tu material en las sesiones largas."],["PUESTA A PUNTO","Baja el volumen entre un 30 y un 50 % y mantén algo de intensidad corta. Duerme mucho."],["SEMANA DE CARRERA","Nada nuevo: sesiones cortas, buena hidratación y tu plan de carrera claro."]];
const store={get(k){try{return JSON.parse(localStorage.getItem(k))}catch(e){return null}},set(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}};
function cdInit(){const sv=store.get("endurace-carrera");const d=new Date();d.setDate(d.getDate()+84);
$("#cn").value=sv&&sv.n||"";$("#cd").value=sv&&sv.d||d.toISOString().slice(0,10);
const k=sv&&CDK[sv.k]?sv.k:"maraton";$("#ck").querySelectorAll("button").forEach(b=>b.setAttribute("aria-checked",String(b.dataset.k==k)));cdRender(false)}
function cdRender(save=true){const k=chosen("#ck").dataset.k,c=CDK[k],name=$("#cn").value.trim(),ds=$("#cd").value;
if(save)store.set("endurace-carrera",{n:name,d:ds,k});
if(!ds){$("#co").innerHTML='<p class="ctl-help">Elige la fecha de tu carrera.</p>';return}
const today=new Date();today.setHours(0,0,0,0);const race=new Date(ds+"T00:00:00"),days=Math.round((race-today)/864e5),wk=days/7;
const title=esc(name||("Tu "+c.n));
if(days<0){$("#co").innerHTML=`<div class="cd-big"><span class="rk">${title.toUpperCase()}</span><b>¡HECHO!</b><span class="rs">Fue hace ${-days} días.</span></div><p class="every"><b>¿Qué tal fue?</b> Si quieres preparar la siguiente, <a href="inscripcion.html">hablemos</a>.</p>`;return}
const ph=days<=7?4:wk<=c.t?3:wk<=c.t+c.s?2:wk<=c.t+c.s+c.b?1:0;
const tot=Math.max(wk,c.t+c.s+c.b+4),seg=[tot-(c.t+c.s+c.b),c.b,c.s,c.t],pos=Math.max(0,Math.min(100,(1-wk/tot)*100));
const W=Math.floor(days/7),D=days%7;
$("#co").innerHTML=`<div class="cd-big"><span class="rk">${title.toUpperCase()} · ${race.toLocaleDateString("es-ES",{day:"numeric",month:"long",year:"numeric"})}</span>
<b>${days===0?"¡HOY!":W?`${W}<small> sem</small>${D?` ${D}<small> d</small>`:""}`:`${D}<small> días</small>`}</b><span class="rs">${days===0?"Disfruta de tu carrera.":`Faltan ${days} días para la salida.`}</span></div>
<div class="cd-line" aria-hidden="true">${seg.map((w,i)=>`<span class="ph${i}${i===Math.min(ph,3)?" on":""}" style="flex:${Math.max(w,.4)}"><em>${PH[i][0]}</em></span>`).join("")}<i style="left:${pos}%"></i></div>
<p class="every"><b>Ahora toca: ${PH[ph][0].toLowerCase()}.</b> ${PH[ph][1]}</p>`}
$("#cn").addEventListener("input",()=>cdRender());$("#cd").addEventListener("input",()=>cdRender());chips("#ck",()=>cdRender());
cdInit();
}
})();
