const MAX_BODY = 20000;
const CONSENT_VERSION = "2026-11-27";

const clean = (v, max) =>
  String(v ?? "").replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, "").trim().slice(0, max);

const json = (obj, status = 200, extra = {}) =>
  new Response(JSON.stringify(obj), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store", ...extra },
  });

async function sha256(text) {
  const b = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(b)].map((x) => x.toString(16).padStart(2, "0")).join("");
}

function cors(req, env) {
  const origin = req.headers.get("Origin") || "";
  const ok = env.ALLOWED_ORIGINS.split(",").map((s) => s.trim()).includes(origin);
  return {
    ok,
    headers: ok
      ? {
          "Access-Control-Allow-Origin": origin,
          "Access-Control-Allow-Methods": "POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type",
          Vary: "Origin",
        }
      : {},
  };
}

async function contact(req, env, c) {
  if (!c.ok) return json({ error: "origin" }, 403);
  let b;
  try {
    const t = await req.text();
    if (t.length > MAX_BODY) return json({ error: "too_large" }, 413, c.headers);
    b = JSON.parse(t);
  } catch {
    return json({ error: "invalid" }, 400, c.headers);
  }
  if (clean(b.empresa, 50)) return json({ ok: true }, 200, c.headers); // honeypot: los bots lo rellenan

  const d = {
    nombre: clean(b.nombre, 120),
    email: clean(b.email, 254).toLowerCase(),
    telefono: clean(b.telefono, 40),
    plan: clean(b.plan, 40),
    periodo: clean(b.periodo, 20),
    trainingpeaks: clean(b.trainingpeaks, 80),
    nivel: clean(b.nivel, 120),
    disciplinas: clean(b.disciplinas, 200),
    prueba: clean(b.prueba, 200),
    horas: clean(b.horas, 100),
    dispositivo: clean(b.dispositivo, 120),
    mensaje: clean(b.mensaje, 3000),
  };
  if (
    d.nombre.length < 2 ||
    !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(d.email) ||
    !/^[a-z0-9-]{1,40}$/.test(d.plan) ||
    b.privacidad !== true
  ) {
    return json({ error: "validation" }, 400, c.headers);
  }

  const ipHash = await sha256((req.headers.get("CF-Connecting-IP") || "") + (env.IP_SALT || ""));
  const since = new Date(Date.now() - 3600e3).toISOString();
  const r = await env.DB.prepare("SELECT COUNT(*) AS n FROM leads WHERE ip_hash = ?1 AND created_at > ?2")
    .bind(ipHash, since)
    .first();
  if (r.n >= 5) return json({ error: "rate_limit" }, 429, c.headers);

  const id = crypto.randomUUID();
  const now = new Date().toISOString();
  await env.DB.prepare(
    `INSERT INTO leads (id, created_at, ip_hash, nombre, email, telefono, plan, periodo, trainingpeaks, nivel,
       disciplinas, prueba, horas, dispositivo, mensaje, consent_version, consent_at)
     VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11,?12,?13,?14,?15,?16,?17)`
  )
    .bind(id, now, ipHash, d.nombre, d.email, d.telefono, d.plan, d.periodo, d.trainingpeaks, d.nivel,
      d.disciplinas, d.prueba, d.horas, d.dispositivo, d.mensaje, CONSENT_VERSION, now)
    .run();

  // El aviso por correo es secundario: la solicitud ya está guardada aunque falle.
  try {
    await env.EMAIL.send({
      to: [{ email: env.NOTIFY_TO }],
      from: { email: env.MAIL_FROM, name: "Endurace Lab" },
      subject: `Nueva solicitud: plan ${d.plan}`,
      text: [
        `Nombre: ${d.nombre}`,
        `Email: ${d.email}`,
        `Teléfono: ${d.telefono || "-"}`,
        `Plan: ${d.plan} (${d.periodo || "-"})`,
        `TrainingPeaks: ${d.trainingpeaks || "-"}`,
        `Experiencia: ${d.nivel || "-"}`,
        `Disciplinas: ${d.disciplinas || "-"}`,
        `Prueba objetivo: ${d.prueba || "-"}`,
        `Horas por semana: ${d.horas || "-"}`,
        `Dispositivo: ${d.dispositivo || "-"}`,
        "",
        d.mensaje || "(sin mensaje)",
        "",
        `Referencia: ${id}`,
      ].join("\n"),
    });
  } catch (e) {
    console.error("email_failed", (e && (e.code || e.message)) || "unknown");
  }
  return json({ ok: true }, 200, c.headers);
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const c = cors(req, env);
    if (req.method === "OPTIONS") return new Response(null, { status: c.ok ? 204 : 403, headers: c.headers });
    if (url.pathname === "/health") return json({ ok: true });
    if (url.pathname === "/contact" && req.method === "POST") return contact(req, env, c);
    return json({ error: "not_found" }, 404, c.headers);
  },
  async scheduled(_event, env) {
    const days = Number(env.RETENTION_DAYS) || 365;
    const limit = new Date(Date.now() - days * 864e5).toISOString();
    await env.DB.prepare("DELETE FROM leads WHERE created_at < ?1").bind(limit).run();
  },
};
