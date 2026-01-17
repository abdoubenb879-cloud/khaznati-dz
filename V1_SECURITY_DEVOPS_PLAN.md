# Khaznati DZ - V1 Security & Deployment Plan
**Role:** Security, Auth Hardening, DevOps Lead
**Target:** Algerian Market (Low bandwidth, High Trust requirement)
**Stack:** Python (Flask), Supabase/Postgres, Docker, Nginx, Linux VPS

## 1. Executive Summary
*   **Zero-Trust Edge**: Use **Cloudflare (Free Tier)** as the entry point for aggressive caching, DDR protection, and managed SSL. This significantly boosts performance for Algerian users with poor connections.
*   **Containerized Simplicity**: Fully dockerized stack (App + Nginx) via `docker-compose`. This ensures the "works on my machine" guarantee for a solo dev.
*   **Hardened Authentication**: Implement session-based auth with `Secure`, `HttpOnly`, `SameSite` cookies. Use `Argon2` for password hashing to prevent rainbow table attacks.
*   **Privacy-First Logging**: Configure Nginx and App logging to anonymize IPs where possible, aligning with the "Trust" value proposition.
*   **Automated CI/CD**: A single GitHub Actions workflow: `Lint -> Test -> Deploy`. Deployment uses SSH to pull changes and restart containers (Zero-downtime not critical for V1, simplicity is key).
*   **Secret Safety**: Strict `.env` usage. No secrets in Git. A template `.env.example` will be maintained.

---

## 2. Authentication & Security Hardening
### A. Authentication Strategy
*   **Library**: `Flask-Login` for session management.
*   **Password Hashing**: `Argon2-cffi`. It is memory-hard and strictly superior to Bcrypt/SHA for modern hardware.
*   **Session Security**:
    *   Cookie Name: `__Secure-KhaznatiSession`
    *   `HttpOnly`: True (Prevents XSS theft)
    *   `Secure`: True (HTTPS only)
    *   `SameSite`: Lax (CSRF protection)
    *   Lifetime: 14 Days (rolling)

### B. Application Security (AppSec)
*   **CSRF Protection**: `Flask-WTF` with `CSRFProtect` global middleware.
*   **Headers (Security Middleware)**:
    *   `Content-Security-Policy`: Strict, allow scripts only from self and specific trusted CDNs (if any).
    *   `X-Frame-Options`: DENY (Prevent clickjacking).
    *   `X-Content-Type-Options`: nosniff.
*   **Rate Limiting**: `Flask-Limiter` usage on login/register endpoints (e.g., "5 per minute").

### C. Trust Features (Frontend Visible)
*   "Secured by Khaznati Shield" badge in footer (Psychological trust).
*   Clear "End-to-End Encryption" (V1.1 feature) or "Bank-Grade Encryption" (At rest/Transit) explanation on the landing page.

---

## 3. Infrastructure & Environment
### A. Architecture Diagram
```
User (DZ) 
  --> [ Cloudflare CDN ] (Edge Cache + WAF + SSL)
      --> [ Host VPS (Linux) ]
          --> [ Nginx Reverse Proxy Container ] 
              --> [ Flask App Container ] (Gunicorn workers)
                  --> [ Supabase / Postgres DB ] (External)
                  --> [ Object Storage ] (S3 Compatible)
```

### B. Directory Structure (Proposed)
```text
khaznati-dz/
├── .github/workflows/   # CI/CD
├── app/                 # Application Code
│   ├── auth/            # Auth Blueprints
│   ├── static/          # Assets
│   └── templates/       # Jinja Templates
├── infrastructure/
│   ├── nginx/           # Nginx Configs
│   └── docker-compose.yml
├── .env                 # SECRETS (GitIgnored)
└── requirements.txt     # Python Dependencies
```

### C. Environment Configuration (.env)
We distinguish between `FLASK_ENV=development` and `production`.
Required variables:
```bash
SECRET_KEY=...          # Strong random string for sessions
DATABASE_URL=...        # Supabase connection string
S3_ACCESS_KEY=...
S3_SECRET_KEY=...
SECURITY_PASSWORD_SALT=...
```

---

## 4. Deployment & CI/CD
### A. Docker Strategy
*   **Dockerfile**: Multi-stage build.
    *   *Builder*: Installs compilers, python dependencies.
    *   *Runner*: `python:3.11-slim`, copies dependencies. Runs `gunicorn`.
*   **Docker Compose**: Orchestrates the Flask container and the Nginx container side-by-side.

### B. Nginx Configuration
Crucial optimizations for Algerian networks:
*   `gzip on;` with aggressive compression levels (5-6) for text/css/js.
*   `client_max_body_size 1G;` (Allow large uploads).
*   `proxy_read_timeout 300s;` (Handle slow mobile uploads).

### C. GitHub Actions Workflow
File: `.github/workflows/deploy.yml`
1.  **Trigger**: Push to `main`.
2.  **Job 1 (Test)**: Ubuntu-latest -> Checkout -> Install Python -> Run `pytest`.
3.  **Job 2 (Deploy)**:
    *   SSH into VPS.
    *   `cd /opt/khaznati-dz`
    *   `git pull origin main`
    *   `docker compose up -d --build`
    *   `docker system prune` (Cleanup)

---

## 5. Roadmap
*   **Phase 1 (Setup)**: Initialize Git, set up Docker structure, basic Flask "Hello World" with hardened config.
*   **Phase 2 (Auth)**: Implement Register/Login with Argon2 and Flask-Login.
*   **Phase 3 (Deploy)**: Provision VPS, set up Cloudflare, first successful deploy of the skeleton.
