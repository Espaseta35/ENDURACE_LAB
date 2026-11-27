/* ENDURACE LAB · "Tu temporada": historias tipo Wrapped generadas con el CSV.
   Usa los datos que deja el informe (lastS, lastEF, lastInt). Todo ocurre en el navegador. */
(() => {
  const MES = ["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"];
  const ES = (v, d = 0) => v.toLocaleString("es-ES", {minimumFractionDigits: d, maximumFractionDigits: d});
  const esc = s => String(s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const hm = h => { const H = Math.floor(h), M = Math.round((h - H) * 60); return H + " h" + (M ? " " + M + " min" : ""); };
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const SLIDE_MS = 5200;

  /* ---------- 1. Cálculos ---------- */
  function stats(S0) {
    const S = S0.filter(s => s.t !== "Caminar").length >= 5 ? S0.filter(s => s.t !== "Caminar") : S0;
    const first = S[0].d, last = S[S.length - 1].d;
    const hours = S.reduce((a, s) => a + s.h, 0);
    const km = {}; S.forEach(s => { if (s.km > 0) km[s.t] = (km[s.t] || 0) + s.km; });
    const kmTot = ["Natación", "Ciclismo", "Carrera", "Remo", "Esquí de fondo"].reduce((a, k) => a + (km[k] || 0), 0);
    const months = {}; S.forEach(s => { const k = s.d.getFullYear() * 12 + s.d.getMonth(); months[k] = (months[k] || 0) + s.h; });
    const mk = Object.keys(months).map(Number).sort((a, b) => a - b).slice(-12);
    const best = mk.reduce((a, k) => months[k] > months[a] ? k : a, mk[0]);
    const LS = S.filter(s => !["Otros", "Raqueta", "Fuerza"].includes(s.t)), longest = (LS.length ? LS : S).reduce((a, s) => s.h > a.h ? s : a, (LS.length ? LS : S)[0]);
    const days = [...new Set(S.map(s => Math.round(new Date(s.d.getFullYear(), s.d.getMonth(), s.d.getDate()) / 864e5)))].sort((a, b) => a - b);
    let streak = 1, run = 1; for (let i = 1; i < days.length; i++) { run = days[i] - days[i - 1] === 1 ? run + 1 : 1; streak = Math.max(streak, run); }
    const ef = ((typeof lastEF !== "undefined" && lastEF) || []).slice().sort((a, b) => b.chg - a.chg)[0] || null;
    const I = typeof lastInt !== "undefined" ? lastInt : null;
    const weeks = Math.max(1, Math.round((last - first) / 6048e5));
    let type;
    if (I && I.lo >= 75) type = ["MOTOR DIÉSEL", "Muchas horas suaves y la intensidad en su sitio. Construyes base como los profesionales."];
    else if (I && I.mo >= I.hi) type = ["ESPÍRITU TEMPO", "Te encanta ese ritmo «cómodamente duro». Si suavizas los rodajes, las series te saldrán aún mejor."];
    else if (I) type = ["MODO SERIES", "Lo tuyo es apretar. Con algo más de volumen suave para asimilarlo, tu techo sube."];
    else if (streak >= 7) type = ["MÁQUINA DE CONSTANCIA", "Pocos fallan menos que tú. La constancia es lo que más rinde en resistencia."];
    else type = ["ESPÍRITU LIBRE", "Entrenas cuando puedes y como puedes. Con un poco de estructura, cada hora contará más."];
    return {first, last, hours, n: S.length, km, kmTot, months, mk, best, longest, streak, ef, type, weeks};
  }

  /* ---------- 2. Pantallas ---------- */
  const range = st => `${MES[st.first.getMonth()].slice(0, 3)} ${st.first.getFullYear()} — ${MES[st.last.getMonth()].slice(0, 3)} ${st.last.getFullYear()}`.toUpperCase();
  function slides(st) {
    const L = [];
    L.push(`<div class="sl sl-intro"><p class="sk">ENDURACE<span>_LAB</span> PRESENTA</p><h2>TU<br><span class="outline">TEMPORADA</span></h2><p class="sr">${range(st)}</p><p class="tap">Toca para avanzar →</p></div>`);
    L.push(`<div class="sl"><p class="sk">HAS ENTRENADO</p><p class="big"><b data-count="${Math.round(st.hours)}">${ES(Math.round(st.hours))}</b></p><p class="unit">HORAS</p><p class="sub">Son <b>${ES(st.hours / 24, 1)} días</b> seguidos sin parar, repartidos en <b>${ES(st.n)} entrenos</b>. Sin contar paseos.</p></div>`);
    if (st.kmTot >= 10) {
      const rows = ["Natación", "Ciclismo", "Carrera", "Remo", "Esquí de fondo"].filter(k => st.km[k] >= 1)
        .map(k => `<li><span>${k}</span><b>${ES(st.km[k], st.km[k] < 100 ? 1 : 0)} km</b></li>`).join("");
      const cam = st.kmTot / 780;
      const cmp = cam >= 1 ? `Es como hacer <b>${ES(cam, 1)} veces</b> el Camino de Santiago francés.` : `Es el <b>${Math.round(cam * 100)} %</b> del Camino de Santiago francés.`;
      L.push(`<div class="sl"><p class="sk">HAS RECORRIDO</p><p class="big"><b data-count="${Math.round(st.kmTot)}">${ES(Math.round(st.kmTot))}</b></p><p class="unit">KILÓMETROS</p><ul class="kml">${rows}</ul><p class="sub">${cmp}</p></div>`);
    }
    if (st.mk.length >= 2) {
      const mx = Math.max(...st.mk.map(k => st.months[k]));
      const bars = st.mk.map(k => `<span class="mb${k === st.best ? " on" : ""}" style="--h:${Math.max(4, st.months[k] / mx * 100)}%"><i></i><em>${MES[k % 12].slice(0, 1).toUpperCase()}</em></span>`).join("");
      L.push(`<div class="sl"><p class="sk">TU MES MÁS FUERTE</p><h2 class="word">${MES[st.best % 12].toUpperCase()}</h2><p class="sub"><b>${hm(st.months[st.best])}</b> de entrenamiento en un solo mes.</p><div class="months">${bars}</div></div>`);
    }
    const lg = st.longest;
    L.push(`<div class="sl"><p class="sk">TU SESIÓN MÁS LARGA</p><p class="big"><b>${hm(lg.h).replace(" min", "'")}</b></p><p class="sub">${lg.t}${lg.n ? ` · «${esc(lg.n.slice(0, 40))}»` : ""}<br>${lg.d.getDate()} de ${MES[lg.d.getMonth()]}${lg.km > 1 ? ` · ${ES(lg.km, 1)} km` : ""}</p></div>`);
    if (st.streak >= 3) L.push(`<div class="sl"><p class="sk">TU MEJOR RACHA</p><p class="big"><b data-count="${st.streak}">${st.streak}</b></p><p class="unit">DÍAS SEGUIDOS</p><p class="sub">entrenando sin un solo día libre. Eso es compromiso.</p></div>`);
    if (st.ef && Math.abs(st.ef.chg) >= 2) {
      const up = st.ef.chg > 0;
      L.push(`<div class="sl"><p class="sk">TU MOTOR · ${st.ef.t.toUpperCase()}</p><p class="big"><b>${up ? "+" : "−"}${ES(Math.abs(st.ef.chg), 1)}</b><small>%</small></p><p class="unit">DE EFICIENCIA</p><p class="sub">${up ? (st.ef.t === "Carrera" ? "Corres más rápido con el mismo pulso." : "Mueves más vatios con el mismo pulso.") + " Tu base aeróbica ha crecido." : "Tu eficiencia ha bajado: calor, fatiga o poco trabajo suave. Hay margen para la próxima."}</p></div>`);
    }
    L.push(`<div class="sl sl-type"><p class="sk">TU TIPO DE ATLETA</p><h2 class="word">${st.type[0]}</h2><p class="sub">${st.type[1]}</p></div>`);
    L.push(`<div class="sl sl-share"><p class="sk">TU TEMPORADA, EN UNA IMAGEN</p><div class="share-img"><img id="tp-img" alt="Resumen de tu temporada"></div><div class="share-actions"><button type="button" class="button button-orange" id="tp-share">Compartir <span>↗</span></button><button type="button" class="button button-outline" id="tp-dl">Descargar</button></div><a class="share-next" href="inscripcion">¿Quieres que la próxima sea aún mejor? Hablemos ↗</a></div>`);
    return L;
  }

  /* ---------- 3. Imagen para compartir (1080×1920) ---------- */
  async function image(st) {
    try { await Promise.all([document.fonts.load('800 100px "Barlow Condensed"'), document.fonts.load('600 30px "IBM Plex Sans"')]); } catch (e) {}
    const W = 1080, H = 1920, c = document.createElement("canvas"); c.width = W; c.height = H;
    const g = c.getContext("2d"), O = "#ff6b2c", WH = "#f4f4f1", MU = "#a8adb2", HEAD = '"Barlow Condensed", Impact, sans-serif', BODY = '"IBM Plex Sans", Arial, sans-serif';
    g.fillStyle = "#090b0e"; g.fillRect(0, 0, W, H);
    const glow = g.createRadialGradient(W * .85, H * .12, 0, W * .85, H * .12, 900); glow.addColorStop(0, "rgba(255,107,44,.42)"); glow.addColorStop(1, "rgba(255,107,44,0)");
    g.fillStyle = glow; g.fillRect(0, 0, W, H);
    g.strokeStyle = "rgba(255,255,255,.05)"; g.lineWidth = 2; for (let x = 90; x < W; x += 90) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, H); g.stroke(); }
    const P = 90; g.textBaseline = "alphabetic";
    g.font = `800 46px ${HEAD}`; g.fillStyle = WH; g.fillText("ENDURACE", P, 150); const w1 = g.measureText("ENDURACE").width; g.fillStyle = O; g.fillText("_LAB", P + w1, 150);
    g.font = `600 30px ${BODY}`; g.fillStyle = O; g.fillText(range(st), P, 260);
    g.font = `800 190px ${HEAD}`; g.fillStyle = WH; g.fillText("MI", P, 460); g.fillStyle = O; g.fillText("TEMPORADA", P, 640);
    const box = (x, y, v, l) => { g.fillStyle = "rgba(255,255,255,.04)"; g.fillRect(x, y, 430, 250); g.strokeStyle = "#30363c"; g.lineWidth = 2; g.strokeRect(x, y, 430, 250);
      g.font = `800 120px ${HEAD}`; g.fillStyle = WH; g.fillText(v, x + 36, y + 150); g.font = `700 26px ${BODY}`; g.fillStyle = O; g.fillText(l, x + 38, y + 205); };
    box(P, 740, ES(Math.round(st.hours)), "HORAS");
    box(P + 470, 740, st.kmTot >= 10 ? ES(Math.round(st.kmTot)) : ES(st.n), st.kmTot >= 10 ? "KILÓMETROS" : "ENTRENOS");
    box(P, 1030, ES(st.n), "ENTRENOS");
    box(P + 470, 1030, st.ef && Math.abs(st.ef.chg) >= 2 ? (st.ef.chg > 0 ? "+" : "−") + ES(Math.abs(st.ef.chg), 0) + "%" : String(st.streak), st.ef && Math.abs(st.ef.chg) >= 2 ? "EFICIENCIA" : "DÍAS DE RACHA");
    g.font = `700 30px ${BODY}`; g.fillStyle = MU; g.fillText("TIPO DE ATLETA", P, 1420);
    let fs = 150; g.font = `800 ${fs}px ${HEAD}`; while (g.measureText(st.type[0]).width > W - 2 * P && fs > 60) { fs -= 6; g.font = `800 ${fs}px ${HEAD}`; }
    g.fillStyle = O; g.fillText(st.type[0], P, 1420 + fs * .95);
    g.fillStyle = O; g.fillRect(P, H - 230, W - 2 * P, 4);
    g.font = `600 34px ${BODY}`; g.fillStyle = WH; g.fillText("Analiza tu temporada gratis en", P, H - 150);
    g.font = `800 52px ${HEAD}`; g.fillStyle = O; g.fillText("ENDURACE-LAB.COM", P, H - 88);
    return c;
  }

  /* ---------- 4. Reproductor ---------- */
  let downAt = 0, dlg, cur = 0, L = [], timer = null, t0 = 0, left = SLIDE_MS, paused = false, st = null, canvas = null, opener = null;
  function build() {
    dlg = document.createElement("div");
    dlg.className = "tp"; dlg.setAttribute("role", "dialog"); dlg.setAttribute("aria-modal", "true"); dlg.setAttribute("aria-label", "Tu temporada"); dlg.hidden = true;
    dlg.innerHTML = `<div class="tp-story"><div class="tp-bars"></div><button class="tp-x" type="button" aria-label="Cerrar">✕</button><div class="tp-stage" aria-live="polite"></div><button class="tp-prev" type="button" aria-label="Anterior"></button><button class="tp-next" type="button" aria-label="Siguiente"></button></div>`;
    document.body.appendChild(dlg);
    dlg.querySelector(".tp-x").addEventListener("click", close);
    const held = () => downAt && performance.now() - downAt > 300;
    dlg.querySelector(".tp-prev").addEventListener("click", () => { if (!held()) go(cur - 1); downAt = 0; });
    dlg.querySelector(".tp-next").addEventListener("click", () => { if (!held()) go(cur + 1); downAt = 0; });
    const stage = dlg.querySelector(".tp-story");
    stage.addEventListener("pointerdown", e => { if (e.target.closest(".tp-x,.share-actions,.share-next")) return; downAt = performance.now(); pause(true); });
    ["pointerup", "pointerleave", "pointercancel"].forEach(ev => stage.addEventListener(ev, () => pause(false)));
    dlg.addEventListener("click", e => { if (e.target === dlg) close(); });
    document.addEventListener("keydown", e => {
      if (dlg.hidden) return;
      if (e.key === "Escape") close(); else if (e.key === "ArrowRight") go(cur + 1); else if (e.key === "ArrowLeft") go(cur - 1);
      else if (e.key === "Tab") { const f = [...dlg.querySelectorAll("button,a")].filter(x => !x.hidden && x.offsetParent); if (!f.length) return;
        if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus(); } else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus(); } }
    });
  }
  function count(el) {
    const end = +el.dataset.count; if (reduce || !end) return;
    const t = performance.now(), d = 1100;
    const step = n => { const p = Math.min(1, (n - t) / d), e = 1 - Math.pow(1 - p, 3); el.textContent = ES(Math.round(end * e)); if (p < 1) requestAnimationFrame(step); };
    requestAnimationFrame(step);
  }
  function go(i) {
    if (i < 0) i = 0;
    if (i >= L.length) return close();
    cur = i;
    const stage = dlg.querySelector(".tp-stage");
    stage.innerHTML = L[cur];
    stage.querySelectorAll("[data-count]").forEach(count);
    dlg.querySelectorAll(".tp-bars i").forEach((b, k) => { b.className = k < cur ? "done" : ""; b.style.animation = "none"; });
    dlg.querySelector(".tp-prev").hidden = cur === 0;
    if (stage.querySelector(".sl-share")) share();
    clearTimeout(timer); left = SLIDE_MS;
    if (!reduce && cur < L.length - 1) run(); else dlg.querySelectorAll(".tp-bars i")[cur].className = "done";
  }
  function run() {
    const bar = dlg.querySelectorAll(".tp-bars i")[cur];
    bar.style.animation = "none"; void bar.offsetWidth;
    bar.style.animation = `tpfill ${SLIDE_MS}ms linear forwards`; bar.style.animationPlayState = "running";
    t0 = performance.now(); timer = setTimeout(() => go(cur + 1), left);
  }
  function pause(on) {
    if (reduce || dlg.hidden || cur >= L.length - 1 || paused === on) return;
    paused = on;
    const bar = dlg.querySelectorAll(".tp-bars i")[cur];
    if (on) { clearTimeout(timer); left -= performance.now() - t0; bar.style.animationPlayState = "paused"; }
    else { bar.style.animationPlayState = "running"; t0 = performance.now(); timer = setTimeout(() => go(cur + 1), Math.max(0, left)); }
  }
  async function share() {
    canvas = canvas || await image(st);
    const img = document.getElementById("tp-img"); if (img) img.src = canvas.toDataURL("image/png");
    const file = () => new Promise(r => canvas.toBlob(b => r(new File([b], "mi-temporada-endurace-lab.png", {type: "image/png"})), "image/png"));
    const dl = async () => { const f = await file(), u = URL.createObjectURL(f), a = document.createElement("a"); a.href = u; a.download = f.name; document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(u), 4000); };
    document.getElementById("tp-dl").onclick = dl;
    const sb = document.getElementById("tp-share");
    sb.onclick = async () => {
      const f = await file();
      if (navigator.canShare && navigator.canShare({files: [f]})) {
        try { await navigator.share({files: [f], title: "Mi temporada", text: "Mi temporada en ENDURACE LAB. Analiza la tuya gratis: https://www.endurace-lab.com/laboratorio"}); } catch (e) {}
      } else dl();
    };
  }
  function open() {
    if (typeof lastS === "undefined" || !lastS) return;
    if (!dlg) build();
    opener = document.activeElement;
    st = stats(lastS); canvas = null; L = slides(st);
    dlg.querySelector(".tp-bars").innerHTML = L.map(() => "<span><i></i></span>").join("");
    dlg.hidden = false; document.documentElement.classList.add("tp-open"); paused = false;
    go(0); dlg.querySelector(".tp-x").focus();
  }
  function close() {
    clearTimeout(timer); dlg.hidden = true; document.documentElement.classList.remove("tp-open");
    if (opener) opener.focus();
  }
  document.getElementById("wrapped-open").addEventListener("click", open);
})();
