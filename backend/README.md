# Khaznati DZ Backend

A modern cloud storage API for Algerian users, built with FastAPI and PostgreSQL.

## Tech Stack

- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL via SQLAlchemy 2.0
- **Migrations**: Alembic
- **File Storage**: S3-compatible (Supabase Storage, Backblaze B2, Wasabi)
- **Auth**: Session-based with secure cookies

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- S3-compatible storage account

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and configure
cp .env.example .env
# Edit .env with your settings

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Variables

See `.env.example` for all required configuration options.

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
app/
├── api/          # API routes
├── core/         # Security, config, middleware
├── models/       # SQLAlchemy models
├── schemas/      # Pydantic schemas
├── services/     # Business logic
└── tasks/        # Background jobs
```

## License

MIT
