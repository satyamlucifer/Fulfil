# 📁 Project Structure

This document provides an overview of the project's file structure and organization.

## Directory Tree

```
fulfil/
├── config/                      # Django project configuration
│   ├── __init__.py             # Celery app initialization
│   ├── settings.py             # Django settings
│   ├── celery.py               # Celery configuration
│   ├── asgi.py                 # ASGI configuration (WebSocket support)
│   ├── wsgi.py                 # WSGI configuration
│   └── urls.py                 # Root URL routing
│
├── products/                    # Main Django app
│   ├── migrations/             # Database migrations
│   ├── __init__.py             
│   ├── admin.py                # Django admin configuration
│   ├── apps.py                 # App configuration
│   ├── models.py               # Data models (Product, Webhook, ImportJob)
│   ├── serializers.py          # DRF serializers
│   ├── views.py                # API views and viewsets
│   ├── urls.py                 # API URL routing
│   ├── frontend_views.py       # Frontend view (serves HTML)
│   ├── frontend_urls.py        # Frontend URL routing
│   ├── consumers.py            # WebSocket consumers
│   ├── routing.py              # WebSocket routing
│   ├── tasks.py                # Celery tasks
│   └── tests.py                # Unit and integration tests
│
├── templates/                   # HTML templates
│   └── index.html              # Main frontend SPA
│
├── static/                      # Static files (CSS, JS, images)
│   └── .gitkeep
│
├── staticfiles/                 # Collected static files (generated)
│
├── media/                       # User-uploaded files
│   └── uploads/                # CSV upload directory
│       └── .gitkeep
│
├── .github/                     # GitHub configuration
│   └── workflows/
│       └── tests.yml           # CI/CD workflow
│
├── requirements.txt             # Python dependencies
├── manage.py                   # Django management script
├── Procfile                    # Heroku process configuration
├── runtime.txt                 # Python version for deployment
├── app.json                    # Heroku app configuration
├── render.yaml                 # Render deployment configuration
├── Dockerfile                  # Docker image configuration
├── docker-compose.yml          # Docker Compose configuration
├── .dockerignore               # Docker ignore patterns
├── .gitignore                  # Git ignore patterns
├── pytest.ini                  # Pytest configuration
├── setup.sh                    # Automated setup script
├── generate_sample_csv.py      # Sample CSV generator
│
├── README.md                   # Main documentation
├── QUICKSTART.md               # Quick start guide
├── DEPLOYMENT.md               # Deployment guide
├── CONTRIBUTING.md             # Contribution guidelines
├── PROJECT_STRUCTURE.md        # This file
└── AI_PROMPTS.md              # AI assistance transparency doc
```

## Core Components

### 1. Configuration (`config/`)

**Purpose**: Django project configuration and setup

- **`settings.py`**: All Django settings including database, middleware, apps, Celery, Channels
- **`celery.py`**: Celery app initialization and configuration
- **`asgi.py`**: ASGI application for WebSocket support via Channels
- **`wsgi.py`**: Traditional WSGI application
- **`urls.py`**: Root URL patterns

### 2. Products App (`products/`)

**Purpose**: Main application logic for product import and management

#### Models (`models.py`)

1. **Product**: Product data with case-insensitive unique SKU
   - Fields: `sku`, `name`, `description`, `is_active`, timestamps
   - Indexes on `sku`, `is_active`, `created_at`

2. **Webhook**: Webhook configuration for event notifications
   - Fields: `url`, `event_type`, `is_active`, response metrics
   - Tracks last trigger time and response

3. **ImportJob**: CSV import job tracking
   - Fields: `task_id`, `filename`, `status`, progress metrics
   - Computed property: `progress_percentage`

#### Views (`views.py`)

1. **ProductViewSet**: CRUD operations, filtering, CSV upload, bulk delete
2. **WebhookViewSet**: CRUD operations, webhook testing
3. **ImportJobViewSet**: View import job history

#### Serializers (`serializers.py`)

- **ProductSerializer**: Product data validation and serialization
- **WebhookSerializer**: Webhook configuration serialization
- **ImportJobSerializer**: Import job status serialization

#### Tasks (`tasks.py`)

1. **`process_csv_import`**: Main async task for CSV processing
   - Batch processing (1000 rows at a time)
   - Real-time progress via WebSocket
   - Webhook triggers on events

2. **`trigger_webhook`**: Async webhook triggering
3. **`trigger_webhook_sync`**: Synchronous webhook helper

#### WebSocket (`consumers.py`, `routing.py`)

- **ImportProgressConsumer**: Real-time progress updates
- WebSocket URL: `/ws/import/{task_id}/`

#### Frontend (`frontend_views.py`, `frontend_urls.py`)

- Simple view to serve the main SPA

### 3. Frontend (`templates/index.html`)

**Purpose**: Single-page application for user interaction

**Features**:
- Tab-based navigation (Upload, Products, Webhooks)
- Real-time CSV upload with progress tracking
- Product CRUD with filtering and pagination
- Webhook management with testing
- WebSocket client for live updates
- Responsive design with gradient styling

**Technology**: Vanilla JavaScript, no frameworks

### 4. Deployment Configurations

#### Heroku (`Procfile`, `runtime.txt`, `app.json`)

- **Procfile**: Defines web (Daphne) and worker (Celery) processes
- **runtime.txt**: Specifies Python version
- **app.json**: App manifest with addons

#### Render (`render.yaml`)

- Complete blueprint for web, worker, database, and Redis

#### Docker (`Dockerfile`, `docker-compose.yml`)

- Multi-container setup with PostgreSQL and Redis
- Development and production ready

### 5. Utilities

#### `generate_sample_csv.py`

- Generates test CSV files with configurable row count
- Usage: `python generate_sample_csv.py -n 1000`

#### `setup.sh`

- Automated setup script for local development
- Creates venv, installs dependencies, runs migrations

### 6. Tests (`products/tests.py`)

**Test Coverage**:
- Model tests (Product, Webhook, ImportJob)
- API endpoint tests (CRUD operations)
- CSV upload tests
- Filtering and pagination tests
- Bulk operations tests

**Run tests**: `python manage.py test`

## Data Flow

### CSV Import Flow

```
User → Upload CSV → API Endpoint
                        ↓
                   Save to media/uploads/
                        ↓
                   Create ImportJob
                        ↓
                   Start Celery Task
                        ↓
        ┌───────────────┴───────────────┐
        ↓                               ↓
  Process in batches            Send progress via WebSocket
        ↓                               ↓
  Create/Update Products          User sees real-time updates
        ↓
  Trigger Webhooks
        ↓
  Mark ImportJob complete
```

### Webhook Flow

```
Event (Product Created/Updated/Deleted)
        ↓
  Find active webhooks for event type
        ↓
  Send HTTP POST to webhook URLs
        ↓
  Record response code and time
        ↓
  Update webhook last_triggered_at
```

### WebSocket Connection Flow

```
Client connects to ws://host/ws/import/{task_id}/
        ↓
  Join channel group 'import_{task_id}'
        ↓
  Celery task sends updates to group
        ↓
  Consumer broadcasts to connected clients
        ↓
  Client receives and displays progress
```

## Database Schema

### Tables

1. **products**
   - Primary key: `id`
   - Unique: `sku` (case-insensitive via uppercase storage)
   - Indexes: `sku`, `is_active`, `created_at`

2. **webhooks**
   - Primary key: `id`
   - Indexes: `event_type`, `is_active`

3. **import_jobs**
   - Primary key: `id`
   - Unique: `task_id`
   - Index: `task_id`

## API Endpoints

### Products API (`/api/products/`)

- `GET /api/products/` - List products (paginated)
- `POST /api/products/` - Create product
- `GET /api/products/{id}/` - Get product
- `PUT /api/products/{id}/` - Update product
- `DELETE /api/products/{id}/` - Delete product
- `POST /api/products/upload_csv/` - Upload CSV
- `GET /api/products/import_status/` - Get import status
- `DELETE /api/products/bulk_delete/` - Delete all

### Webhooks API (`/api/webhooks/`)

- `GET /api/webhooks/` - List webhooks
- `POST /api/webhooks/` - Create webhook
- `GET /api/webhooks/{id}/` - Get webhook
- `PUT /api/webhooks/{id}/` - Update webhook
- `DELETE /api/webhooks/{id}/` - Delete webhook
- `POST /api/webhooks/{id}/test/` - Test webhook

### Import Jobs API (`/api/import-jobs/`)

- `GET /api/import-jobs/` - List import jobs
- `GET /api/import-jobs/{id}/` - Get import job

## Environment Variables

See `.env.example` for all required environment variables:

- **Django**: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
- **Database**: `DATABASE_URL`
- **Redis**: `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`
- **CORS**: `CORS_ALLOWED_ORIGINS`

## Technology Stack Summary

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Web Framework | Django 4.2 | Core application framework |
| API | Django REST Framework | RESTful API |
| Database | PostgreSQL | Data persistence |
| ORM | Django ORM | Database abstraction |
| Async Tasks | Celery | Background job processing |
| Message Broker | Redis | Celery broker & result backend |
| WebSockets | Django Channels | Real-time updates |
| ASGI Server | Daphne | Production ASGI server |
| Frontend | Vanilla JS | User interface |
| Containerization | Docker | Deployment packaging |

## Development Workflow

1. **Local Development**:
   - Use Docker Compose or manual setup
   - Run migrations: `python manage.py migrate`
   - Start Redis, Celery worker, and Daphne

2. **Making Changes**:
   - Edit code in `products/` or `config/`
   - Run tests: `python manage.py test`
   - Check for migrations: `python manage.py makemigrations`

3. **Deployment**:
   - Push to Git repository
   - Deploy to Heroku, Render, or Docker platform
   - Run migrations on production
   - Scale worker dynos as needed

## Performance Considerations

1. **Batch Processing**: CSV processed in 1000-row batches
2. **Database Indexing**: Optimized indexes on frequently queried fields
3. **Connection Pooling**: Django `CONN_MAX_AGE` set to 600 seconds
4. **Async Workers**: Long operations offloaded to Celery
5. **Static Files**: Compressed and served via WhiteNoise

## Security Features

- CSRF protection enabled
- SQL injection prevention (ORM)
- XSS protection
- Secure password hashing
- HTTPS enforcement in production
- Environment-based secrets

## Future Enhancements

Potential areas for expansion:
- [ ] Bulk export to CSV
- [ ] Product categories and tags
- [ ] Image upload support
- [ ] Advanced search with Elasticsearch
- [ ] Rate limiting for API
- [ ] OAuth authentication
- [ ] Scheduled imports
- [ ] Data validation rules
- [ ] Audit logging
- [ ] Multi-tenancy support

---

For questions about the project structure, refer to the README or open an issue.

