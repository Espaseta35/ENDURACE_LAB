CREATE TABLE leads (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  ip_hash TEXT NOT NULL,
  nombre TEXT NOT NULL,
  email TEXT NOT NULL,
  telefono TEXT,
  plan TEXT NOT NULL,
  periodo TEXT,
  trainingpeaks TEXT,
  nivel TEXT,
  disciplinas TEXT,
  prueba TEXT,
  horas TEXT,
  dispositivo TEXT,
  mensaje TEXT,
  consent_version TEXT NOT NULL,
  consent_at TEXT NOT NULL
);
CREATE INDEX idx_leads_ip ON leads (ip_hash, created_at);
CREATE INDEX idx_leads_created ON leads (created_at);
