# 🚀 Product Importer - Acme Inc.

A scalable, production-ready web application for importing large CSV files (up to 500,000 products) into a SQL database with real-time progress tracking, product management, and webhook notifications.

## ✨ Features

### 📤 **STORY 1: File Upload via UI**
- Upload large CSV files (up to 500,000 products) through an intuitive web interface
- Real-time progress indicator with WebSocket updates
- Automatic duplicate handling based on case-insensitive SKU
- Unique SKU constraint enforcement
- Active/Inactive product status management

### 📊 **STORY 1A: Upload Progress Visibility**
- Real-time progress updates with visual progress bar
- Live statistics: total rows, processed, created, updated, errors
- Dynamic status messages (Parsing, Validating, Import Complete)
- Error handling with clear failure messages and retry option

### 📦 **STORY 2: Product Management UI**
- Full CRUD operations (Create, Read, Update, Delete)
- Advanced filtering by SKU, name, and active status
- Paginated product list with 50 items per page
- Inline editing with modal forms
- Clean, modern, responsive design

### 🗑️ **STORY 3: Bulk Delete from UI**
- Delete all products with double confirmation
- Success/failure notifications
- Responsive with visual feedback

### 🔗 **STORY 4: Webhook Configuration via UI**
- Configure and manage multiple webhooks
- Support for multiple event types:
  - Product Created
  - Product Updated
  - Product Deleted
  - Bulk Import Started/Completed
  - Bulk Delete Completed
- Test webhooks with visual confirmation
- Display response codes and response times

## 🛠️ Tech Stack

- **Framework**: Django 4.2
- **API**: Django REST Framework
- **Async Processing**: Celery with Redis
- **Real-time Updates**: Django Channels (WebSockets)
- **Database**: PostgreSQL
- **ORM**: Django ORM
- **Frontend**: Vanilla JavaScript (Single Page Application)
- **Production Server**: Daphne (ASGI) + Gunicorn fallback

## 📋 Requirements

- Python 3.11+
- PostgreSQL 12+
- Redis 6+

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/product-importer.git
cd product-importer
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DATABASE_URL=postgresql://user:password@localhost:5432/product_importer
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 5. Set Up Database

```bash
# Create PostgreSQL database
createdb product_importer

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 6. Create Static Files Directory

```bash
mkdir -p static staticfiles media/uploads
python manage.py collectstatic --noinput
```

### 7. Run the Application

You need to run three processes:

**Terminal 1 - Django Server:**
```bash
python manage.py runserver
# Or for production:
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

**Terminal 2 - Celery Worker:**
```bash
celery -A config worker --loglevel=info --concurrency=4
```

**Terminal 3 - Redis:**
```bash
redis-server
```

### 8. Access the Application

Open your browser and navigate to:
- **Main Application**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **API Documentation**: http://localhost:8000/api/

## 🐳 Docker Setup (Recommended)

The easiest way to run the application is using Docker Compose:

```bash
# Build and start all services
docker-compose up --build

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

This will start:
- PostgreSQL database on port 5432
- Redis on port 6379
- Django web server on port 8000
- Celery worker

## 📝 CSV File Format

Your CSV file should have the following columns:

```csv
sku,name,description
PROD001,Product Name 1,Product description here
PROD002,Product Name 2,Another description
```

**Notes:**
- `sku` and `name` are required fields
- `description` is optional
- SKU is case-insensitive and must be unique
- Duplicates will be automatically updated based on SKU

## 🌐 Deployment

### Heroku Deployment

1. **Install Heroku CLI**
```bash
brew install heroku/brew/heroku  # macOS
# or download from https://devcenter.heroku.com/articles/heroku-cli
```

2. **Login and Create App**
```bash
heroku login
heroku create your-app-name
```

3. **Add Addons**
```bash
heroku addons:create heroku-postgresql:mini
heroku addons:create heroku-redis:mini
```

4. **Set Environment Variables**
```bash
heroku config:set SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=.herokuapp.com
```

5. **Deploy**
```bash
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

6. **Scale Worker**
```bash
heroku ps:scale web=1 worker=1
```

7. **Open Application**
```bash
heroku open
```

### Render Deployment

1. **Create Account**: Sign up at https://render.com

2. **Create New Blueprint**
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`
   - Click "Apply" to create all services

3. **Set Environment Variables** (if not auto-configured)
   - Navigate to each service
   - Add environment variables from `.env.example`

4. **Deploy**
   - Render will automatically deploy on git push
   - Monitor deployment in the dashboard

### AWS/GCP Deployment

For AWS or GCP deployment:

1. Use the provided `Dockerfile` to build a container image
2. Push to ECR (AWS) or GCR (GCP)
3. Deploy using ECS, EKS, Cloud Run, or App Engine
4. Set up managed PostgreSQL and Redis services
5. Configure environment variables
6. Set up load balancer and auto-scaling

## 📊 API Documentation

### Products API

- `GET /api/products/` - List all products (paginated)
- `POST /api/products/` - Create a product
- `GET /api/products/{id}/` - Get product details
- `PUT /api/products/{id}/` - Update a product
- `DELETE /api/products/{id}/` - Delete a product
- `POST /api/products/upload_csv/` - Upload CSV file
- `GET /api/products/import_status/?task_id={id}` - Get import status
- `DELETE /api/products/bulk_delete/` - Delete all products

### Webhooks API

- `GET /api/webhooks/` - List all webhooks
- `POST /api/webhooks/` - Create a webhook
- `GET /api/webhooks/{id}/` - Get webhook details
- `PUT /api/webhooks/{id}/` - Update a webhook
- `DELETE /api/webhooks/{id}/` - Delete a webhook
- `POST /api/webhooks/{id}/test/` - Test a webhook

### WebSocket Endpoint

- `ws://localhost:8000/ws/import/{task_id}/` - Real-time import progress

## 🎨 Code Quality

This project follows Python and Django best practices:

- **PEP 8** compliant code
- **Type hints** for better code clarity
- **Docstrings** for all classes and functions
- **DRY principle** - Don't Repeat Yourself
- **Separation of concerns** - Models, Views, Serializers, Tasks
- **Error handling** with proper logging
- **Security best practices** - CSRF protection, SQL injection prevention
- **Scalable architecture** - Async workers, batch processing

## 📈 Performance Optimizations

- **Batch Processing**: Processes CSV in batches of 1,000 rows
- **Database Indexing**: Optimized indexes on SKU, is_active, and created_at
- **Connection Pooling**: Configured with `conn_max_age=600`
- **Async Workers**: Celery handles long-running tasks
- **WebSocket Updates**: Efficient real-time progress without polling
- **Static File Compression**: WhiteNoise for optimized static file serving

## 🔒 Security Features

- CSRF protection enabled
- SQL injection prevention via ORM
- XSS protection with Django templates
- Secure password hashing
- HTTPS support in production
- Environment variable management
- CORS configuration for API access

## 🧪 Testing

```bash
# Run tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 📦 Sample CSV Generator

Create a sample CSV file for testing:

```python
import csv

with open('sample_products.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['sku', 'name', 'description'])
    
    for i in range(1000):
        writer.writerow([
            f'SKU{i:06d}',
            f'Product {i}',
            f'Description for product {i}'
        ])
```

## 🐛 Troubleshooting

### Issue: WebSocket connection failed

**Solution**: Ensure Daphne is running (not Django dev server) and Redis is accessible.

```bash
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

### Issue: Celery tasks not processing

**Solution**: Make sure Redis is running and Celery worker is started.

```bash
redis-server
celery -A config worker --loglevel=info
```

### Issue: Static files not loading

**Solution**: Run collectstatic command.

```bash
python manage.py collectstatic --noinput
```

### Issue: Database connection error

**Solution**: Verify PostgreSQL is running and DATABASE_URL is correct.

```bash
# Check PostgreSQL status
pg_isready

# Test connection
psql $DATABASE_URL
```

## 📞 Support

For issues, questions, or contributions:

- Open an issue on GitHub
- Email: support@acme-inc.com
- Documentation: https://docs.acme-inc.com

## 📄 License

This project is proprietary software owned by Acme Inc.

## 👥 Contributors

- Your Name - Initial development

## 🙏 Acknowledgments

- Django community for excellent documentation
- Celery team for robust async task processing
- Channels team for WebSocket support

---

**Built with ❤️ for Acme Inc.**

