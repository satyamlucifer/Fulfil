# ⚡ Quick Start Guide

Get the Product Importer up and running in 5 minutes!

## 🐳 Option 1: Docker (Recommended - Easiest)

**Prerequisites**: Docker and Docker Compose installed

```bash
# Clone the repository
git clone https://github.com/yourusername/product-importer.git
cd product-importer

# Start all services
docker-compose up --build

# In another terminal, run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Access the app at http://localhost:8000
```

That's it! 🎉

## 💻 Option 2: Local Development

**Prerequisites**: Python 3.11+, PostgreSQL, Redis

```bash
# Clone the repository
git clone https://github.com/yourusername/product-importer.git
cd product-importer

# Run the setup script
chmod +x setup.sh
./setup.sh

# Start Redis (in separate terminal)
redis-server

# Start Celery worker (in separate terminal)
source venv/bin/activate
celery -A config worker --loglevel=info

# Start Django server (in separate terminal)
source venv/bin/activate
daphne -b 0.0.0.0 -p 8000 config.asgi:application

# Access the app at http://localhost:8000
```

## 📤 Test CSV Upload

1. Generate a sample CSV:
```bash
python generate_sample_csv.py -n 1000 -o test_products.csv
```

2. Open http://localhost:8000
3. Click "Upload CSV" tab
4. Drag and drop `test_products.csv`
5. Watch real-time progress! ⚡

## 🔗 Test Webhooks

1. Go to "Webhooks" tab
2. Click "Add Webhook"
3. Use https://webhook.site to get a test URL
4. Add webhook with URL and event type
5. Click "Test" to verify

## 📱 What's Next?

- Explore product management
- Try filtering and pagination
- Test bulk delete
- Check out the admin panel at http://localhost:8000/admin
- Read the full [README.md](README.md) for deployment

## 🆘 Having Issues?

**WebSocket not working?**
- Make sure you're using Daphne, not `manage.py runserver`
- Check Redis is running

**Celery tasks not processing?**
- Verify Redis connection
- Ensure Celery worker is running

**Database errors?**
- Run migrations: `python manage.py migrate`
- Check DATABASE_URL in `.env`

## 📚 Resources

- [Full Documentation](README.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Contributing](CONTRIBUTING.md)

Happy coding! 🚀

