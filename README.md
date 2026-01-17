# Khaznati DZ - خزنتي

Your Algerian-Friendly Cloud Drive 🇩🇿

## Overview

Khaznati DZ is a modern, privacy-respecting cloud storage web application designed specifically for Algerian users. It provides a polished alternative to Google Drive/Dropbox with a lightweight, cost-efficient backend.

## Features (V1)

- 🔐 **Secure Authentication** - Email/password with session-based auth
- 📁 **File Management** - Upload, download, organize into folders
- 🔗 **Smart Sharing** - Generate secure share links with optional protection
- 🌍 **Bilingual UI** - Full Arabic (RTL) and French (LTR) support
- 🌙 **Dark Mode** - Mobile-first design with dark theme
- 📱 **Low-Bandwidth Optimized** - Chunked uploads for unstable connections

## Tech Stack

- **Backend**: Python 3.11+ with FastAPI
- **Database**: PostgreSQL (Supabase)
- **Storage**: S3-compatible object storage
- **Frontend**: HTML5 + CSS3 + Vanilla JS (Alpine.js)
- **Auth**: Session-based with secure cookies

## Project Structure

```
khaznati-dz/
├── backend/
│   ├── app/
│   │   ├── api/           # API route handlers
│   │   ├── core/          # Config, security, dependencies
│   │   ├── models/        # Database models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   └── main.py        # FastAPI app entry
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── templates/
│   └── locales/           # i18n translations
├── .env.example
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL or Supabase account
- S3-compatible storage (Supabase Storage, Backblaze B2, etc.)

### Installation

1. Clone the repository
```bash
git clone https://github.com/your-username/khaznati-dz.git
cd khaznati-dz
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r backend/requirements.txt
```

4. Configure environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run development server
```bash
cd backend
uvicorn app.main:app --reload
```

## Environment Variables

See `.env.example` for required configuration.

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## License

MIT License - See [LICENSE](LICENSE) for details.

---

Made with ❤️ for Algeria 🇩🇿
