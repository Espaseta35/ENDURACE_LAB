/* ENDURACE LAB · efectos compartidos: aparición al hacer scroll, cinta en movimiento,
   instalación como app (PWA). Sin librerías. Respeta "reducir movimiento". */
(() => {
  /* Analítica sin cookies (Cloudflare Web Analytics). Pega aquí tu token para activarla.
     Instrucciones en LEEME.txt. Mientras esté vacío, no se carga nada. */
  const ANALYTICS_TOKEN = "";
  if (ANALYTICS_TOKEN && location.protocol === "https:") {
    const s = document.createElement("script");
    s.defer = true; s.src = "https://static.cloudflareinsights.com/beacon.min.js";
    s.setAttribute("data-cf-beacon", JSON.stringify({token: ANALYTICS_TOKEN}));
    document.head.appendChild(s);
  }

  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* Aparición suave de bloques al entrar en pantalla */
  if (!reduce && "IntersectionObserver" in window) {
    const sel = ".section-heading,.method-card,.sport-link,.price-card,.service-card,.about-photo,.about-copy,.faq-list details,.mini-pred,.extras>div,.run-tools article,.final-cta-inner,.lab-report .block,.process article";
    const els = [...document.querySelectorAll(sel)].filter(el => el.getBoundingClientRect().top > innerHeight * .9);
    if (els.length) {
      document.documentElement.classList.add("fx");
      const io = new IntersectionObserver(es => es.forEach(e => {
        if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
      }), {rootMargin: "0px 0px -8% 0px", threshold: .08});
      els.forEach(el => {
        const sib = [...el.parentElement.children].filter(x => x.tagName === el.tagName);
        el.style.setProperty("--d", Math.min(sib.indexOf(el), 5) * 80 + "ms");
        el.classList.add("rv");
        io.observe(el);
      });
    }
  }

  /* Cinta de disciplinas en movimiento infinito */
  if (!reduce) document.querySelectorAll(".ticker").forEach(t => {
    const inner = t.querySelector(".ticker-inner");
    if (!inner || inner.dataset.mq) return;
    const copy = inner.innerHTML;
    inner.insertAdjacentHTML("beforeend", copy.replace(/<(span|i)>/g, '<$1 aria-hidden="true">'));
    inner.dataset.mq = "1";
    t.classList.add("mq");
  });

  /* Instalar como app */
  let promptEvt = null;
  addEventListener("beforeinstallprompt", e => {
    e.preventDefault(); promptEvt = e;
    document.querySelectorAll("[data-install]").forEach(b => b.hidden = false);
  });
  document.querySelectorAll("[data-install]").forEach(b => b.addEventListener("click", async () => {
    if (!promptEvt) return;
    promptEvt.prompt(); await promptEvt.userChoice; promptEvt = null;
    document.querySelectorAll("[data-install]").forEach(x => x.hidden = true);
  }));
  if ("serviceWorker" in navigator && location.protocol === "https:") {
    addEventListener("load", () => navigator.serviceWorker.register("sw.js").catch(() => {}));
  }
})();
