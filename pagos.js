/*
  Configuración de pagos de ENDURACE LAB (Stripe).
  Mientras "activo" sea false, la web no muestra ningún pago ni el enlace al portal.
  Para activarlo: pega aquí los enlaces de pago (Payment Links) y el portal de cliente
  de Stripe, cambia "activo" a true y publica. Instrucciones en _build/LEEME.txt.
*/
window.ENDURACE_PAGOS = {
  activo: false,
  portal: "", // Enlace del portal de cliente de Stripe (Ajustes > Billing > Customer portal)
  enlaces: {
    "esencial-mensual": "", "esencial-trimestral": "", "esencial-semestral": "",
    "pro-mensual": "", "pro-trimestral": "", "pro-semestral": "",
    "premium-mensual": "", "premium-trimestral": "", "premium-semestral": "",
    "carrera": "", "sesion": ""
  }
};

/* Muestra el enlace "Gestionar mi suscripción" solo cuando los pagos están activos */
document.addEventListener("DOMContentLoaded", () => {
  const P = window.ENDURACE_PAGOS;
  if (!P.activo || !P.portal) return;
  document.querySelectorAll("[data-portal]").forEach(el => {
    const a = el.querySelector("a") || el;
    a.href = P.portal;
    el.hidden = false;
  });
});
