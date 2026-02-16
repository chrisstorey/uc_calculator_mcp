# FastAPI Project Outline

A comprehensive outline and starter template for a production-ready FastAPI project.

## Project Structure

```
python_fastapi_outline/
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                   # FastAPI application entry point
│   ├── config.py                 # Configuration settings (environment variables)
│   ├── routers/                  # API route handlers
│   │   ├── __init__.py
│   │   ├── health.py             # Health check endpoints
│   │   ├── users.py              # User management endpoints
│   │   └── items.py              # Item management endpoints
│   ├── models/                   # SQLAlchemy database models
│   │   ├── __init__.py
│   │   ├── user.py               # User model
│   │   └── item.py               # Item model
│   ├── schemas/                  # Pydantic schemas for validation
│   │   ├── __init__.py
│   │   ├── user.py               # User request/response schemas
│   │   └── item.py               # Item request/response schemas
│   ├── database/                 # Database configuration
│   │   ├── __init__.py
│   │   ├── base.py               # SQLAlchemy base configuration
│   │   └── session.py            # Database session management
│   ├── dependencies/             # Dependency injection
│   │   ├── __init__.py
│   │   └── auth.py               # Authentication utilities
│   ├── utils/                    # Utility functions
│   │   ├── __init__.py
│   │   └── validators.py         # Validation helpers
│   └── middleware/               # Custom middleware
│       ├── __init__.py
│       └── cors.py               # CORS configuration
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── conftest.py               # Pytest configuration and fixtures
│   ├── test_health.py            # Health check tests
│   ├── test_users.py             # User endpoint tests
│   └── test_items.py             # Item endpoint tests
├── docker/                       # Docker configuration
│   ├── Dockerfile                # Container image definition
│   └── docker-compose.yml        # Multi-container setup
├── .env.example                  # Environment variables template
├── pytest.ini                    # Pytest configuration
├── pyproject.toml                # Project metadata and dependencies
├── uv.lock                       # Locked dependency versions
└── README.md                     # This file
```

## Key Components

### Configuration (config.py)
- Centralized settings management using Pydantic
- Environment variable support
- Database, security, and CORS configuration

### Routers
- **health.py**: Basic health check endpoint
- **users.py**: Full CRUD operations for users
- **items.py**: Full CRUD operations for items

### Models & Schemas
- **models/**: SQLAlchemy ORM models for database tables
- **schemas/**: Pydantic models for request/response validation

### Database
- Session management with SQLAlchemy
- Support for SQLite (default) and PostgreSQL
- Base declarative configuration

### Authentication
- JWT token creation and validation
- Bearer token support
- Dependency injection for protected routes

### Tests
- Pytest-based test suite
- Test fixtures and client setup
- Examples for CRUD operations

### Docker
- Multi-stage Dockerfile for production builds
- Docker Compose configuration with PostgreSQL support

## Getting Started

### Prerequisites
- Python 3.9+
- [uv](https://docs.astral.sh/uv/)

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd python_fastapi_outline
```

2. Install dependencies
```bash
uv sync
```

This command will create a virtual environment and install all dependencies.

3. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your settings
```

4. Run the application
```bash
uv run uvicorn app.main:app --reload
```

The application will be available at `http://localhost:8000`

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Running Tests

```bash
uv run pytest
uv run pytest -v                    # Verbose output
uv run pytest --cov                 # With coverage report
uv run pytest tests/test_users.py   # Specific test file
```

## Docker

### Build and run with Docker Compose
```bash
docker-compose -f docker/docker-compose.yml up
```

## Development

### Code Formatting
```bash
uv run black app tests
```

### Linting
```bash
uv run ruff check app tests
```

### Type Checking
```bash
uv run mypy app
```

## Project Features

✓ Modular and scalable architecture
✓ Environment-based configuration
✓ SQLAlchemy ORM integration
✓ Pydantic data validation
✓ JWT authentication
✓ CORS middleware
✓ Comprehensive test suite
✓ Docker support
✓ Type hints throughout
✓ RESTful API design

## API Endpoints

### Health
- `GET /health` - Health check

### Users
- `POST /api/users/` - Create user
- `GET /api/users/` - List users
- `GET /api/users/{user_id}` - Get user
- `PUT /api/users/{user_id}` - Update user
- `DELETE /api/users/{user_id}` - Delete user

### Items
- `POST /api/items/` - Create item
- `GET /api/items/` - List items
- `GET /api/items/{item_id}` - Get item
- `PUT /api/items/{item_id}` - Update item
- `DELETE /api/items/{item_id}` - Delete item

## Database

### SQLite (Development)
Default configuration uses SQLite database file in the project directory.

### PostgreSQL (Production)
Update `DATABASE_URL` in `.env`:
```
DATABASE_URL=postgresql://user:password@localhost/dbname
```

## Security Considerations

⚠️ **Important for Production:**
- Change `SECRET_KEY` in `.env` to a strong random value
- Use HTTPS in production
- Implement rate limiting
- Add request validation
- Use environment secrets management
- Enable CORS only for trusted origins

## License

MIT License