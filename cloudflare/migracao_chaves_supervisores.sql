-- Credentials for individual supervisor logins.
-- Store only PBKDF2-SHA256 hashes and random salts; never store plaintext keys.
-- Initial production credentials are provisioned separately in the production database.
CREATE TABLE IF NOT EXISTS public.aproar_supervisor_access (
  supervisor text PRIMARY KEY CHECK (supervisor IN ('EDUARDO','FELIPE','GABRIEL','JOEL','NETO','SOARES','VICTOR')),
  password_salt text NOT NULL CHECK (password_salt ~ '^[0-9a-f]{32}$'),
  password_hash text NOT NULL CHECK (password_hash ~ '^[0-9a-f]{64}$'),
  iterations integer NOT NULL DEFAULT 210000 CHECK (iterations BETWEEN 100000 AND 500000),
  active boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
