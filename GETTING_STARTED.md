# 🎯 Getting Started with Product Importer

Welcome! This guide will help you get the Product Importer application running in the easiest way possible.

## 🎬 Choose Your Adventure

### Option 1: Docker (Easiest - 2 minutes) 🐳

**Best for**: Quick testing and evaluation

```bash
# 1. Clone the repository
git clone [your-repo-url]
cd product-importer

# 2. Start everything with one command
docker-compose up --build

# 3. Open another terminal and run migrations
docker-compose exec web python manage.py migrate

# 4. Create admin user (optional)
docker-compose exec web python manage.py createsuperuser

# 5. Open your browser
http://localhost:8000
```

That's it! ✨

### Option 2: Automated Setup Script (5 minutes) 🤖

**Best for**: Local development with automatic configuration

```bash
# 1. Clone the repository
git clone [your-repo-url]
cd product-importer

# 2. Make setup script executable and run it
chmod +x setup.sh
./setup.sh

# 3. Start all services
chmod +x run_local.sh
./run_local.sh

# 4. Open your browser
http://localhost:8000
```

### Option 3: Manual Setup (10 minutes) 👨‍💻

**Best for**: Understanding the architecture

#### Prerequisites

Install these first:
- Python 3.11+
- PostgreSQL 12+
- Redis 6+

#### Steps

1. **Clone and Setup Environment**

```bash
git clone [your-repo-url]
cd product-importer
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

3. **Configure Environment**

Create `.env` file:
```bash
cp .env.example .env
```

Edit `.env` and update these values:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/product_importer
REDIS_URL=redis://localhost:6379/0
```

4. **Setup Database**

```bash
createdb product_importer  # Create PostgreSQL database
python manage.py migrate   # Run migrations
python manage.py createsuperuser  # Create admin user
```

5. **Prepare Static Files**

```bash
mkdir -p static staticfiles media/uploads
python manage.py collectstatic --noinput
```

6. **Start Services** (requires 3 terminal windows)

**Terminal 1 - Redis:**
```bash
redis-server
```

**Terminal 2 - Celery Worker:**
```bash
source venv/bin/activate
celery -A config worker --loglevel=info
```

**Terminal 3 - Django Server:**
```bash
source venv/bin/activate
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

7. **Access Application**

Open http://localhost:8000

## 🧪 Test the Application

### 1. Generate Sample Data

```bash
# Generate 100 products
python generate_sample_csv.py -n 100 -o test_100.csv

# Or use the included sample
# sample_products_small.csv (10 products)
```

### 2. Upload CSV

1. Go to http://localhost:8000
2. Click on "Upload CSV" tab
3. Drag and drop your CSV file or click to browse
4. Watch the real-time progress! 🎉

### 3. Test Product Management

1. Click on "Products" tab
2. Try filtering by SKU or name
3. Click "Add Product" to create manually
4. Edit and delete products

### 4. Test Webhooks

1. Go to https://webhook.site to get a test URL
2. Click on "Webhooks" tab in the app
3. Click "Add Webhook"
4. Paste your webhook.site URL
5. Select an event type
6. Click "Save"
7. Click "Test" to verify it works
8. Go back to webhook.site to see the payload

## 🎨 What You'll See

### Main Interface

- **Upload Tab**: Beautiful drag-and-drop interface with real-time progress
- **Products Tab**: Sortable, filterable product list with pagination
- **Webhooks Tab**: Webhook management with testing capability

### Features to Try

✅ Upload large CSV files  
✅ Watch real-time progress updates  
✅ Create products manually  
✅ Filter and search products  
✅ Edit product details  
✅ Delete individual products  
✅ Bulk delete all products (with confirmation)  
✅ Configure webhooks  
✅ Test webhooks live  

## 🔧 Admin Interface

Access Django admin at http://localhost:8000/admin

**Features**:
- View all products
- Manage webhooks
- View import job history
- User management

**Login**: Use the superuser credentials you created

## 📊 API Endpoints

Test the API directly:

```bash
# List products
curl http://localhost:8000/api/products/

# Get specific product
curl http://localhost:8000/api/products/1/

# Create product
curl -X POST http://localhost:8000/api/products/ \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "TEST001",
    "name": "Test Product",
    "description": "Test description",
    "is_active": true
  }'

# List webhooks
curl http://localhost:8000/api/webhooks/
```

## 🐛 Troubleshooting

### "WebSocket connection failed"

**Problem**: Using wrong server  
**Solution**: Use Daphne, not `python manage.py runserver`

```bash
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

### "Celery tasks not processing"

**Problem**: Redis or Celery not running  
**Solution**: 

```bash
# Check Redis
redis-cli ping

# Start Celery
celery -A config worker --loglevel=info
```

### "Static files not loading"

**Problem**: Static files not collected  
**Solution**:

```bash
python manage.py collectstatic --noinput
```

### "Database connection error"

**Problem**: PostgreSQL not running or wrong DATABASE_URL  
**Solution**:

```bash
# Check PostgreSQL
pg_isready

# Verify your DATABASE_URL in .env file
```

### Port Already in Use

**Problem**: Port 8000 already taken  
**Solution**: Use different port

```bash
daphne -b 0.0.0.0 -p 8080 config.asgi:application
```

## 🎓 Next Steps

### 1. Learn More

- Read the [README.md](README.md) for full documentation
- Check [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) to understand the codebase
- Review [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment

### 2. Deploy to Production

- Deploy to Heroku: Follow [DEPLOYMENT.md](DEPLOYMENT.md#heroku)
- Deploy to Render: Follow [DEPLOYMENT.md](DEPLOYMENT.md#render)
- Deploy with Docker: Use the provided Dockerfile

### 3. Customize

- Modify the frontend in `templates/index.html`
- Add new models in `products/models.py`
- Create new API endpoints in `products/views.py`
- Add webhook events in `products/tasks.py`

## 💡 Tips

1. **Use Docker** for the quickest setup
2. **Generate sample data** to test with realistic datasets
3. **Check the logs** if something doesn't work
4. **Use the admin interface** for quick data inspection
5. **Test webhooks** with webhook.site before using real URLs

## 📚 Resources

- **Full Documentation**: [README.md](README.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **API Reference**: Check `/api/` endpoints
- **Django Docs**: https://docs.djangoproject.com/
- **Celery Docs**: https://docs.celeryproject.org/

## 🆘 Get Help

- **Issues**: Open an issue on GitHub
- **Questions**: Check the documentation
- **Bugs**: Please report with steps to reproduce

## 🎉 You're Ready!

Congratulations! You now have a fully functional product import system running.

Try uploading a CSV file and watch it process in real-time. The application is designed to handle up to 500,000 records efficiently!

---

**Happy coding!** 🚀

*Built with ❤️ for Acme Inc.*

