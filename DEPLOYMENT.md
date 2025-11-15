# 🚀 Deployment Guide

This guide covers deploying the Product Importer application to various platforms.

## 📋 Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database migrations ready
- [ ] Static files collected
- [ ] Debug mode disabled
- [ ] Secret key generated
- [ ] Allowed hosts configured
- [ ] CORS settings reviewed
- [ ] Worker concurrency tuned

## 🌐 Heroku Deployment

### Prerequisites
- Heroku CLI installed
- Git repository initialized
- Heroku account created

### Step-by-Step Guide

1. **Create Heroku App**
```bash
heroku create product-importer-acme
```

2. **Add PostgreSQL and Redis**
```bash
heroku addons:create heroku-postgresql:mini
heroku addons:create heroku-redis:mini
```

3. **Configure Environment Variables**
```bash
# Generate and set secret key
heroku config:set SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

# Set Django settings
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=.herokuapp.com
heroku config:set CORS_ALLOWED_ORIGINS=https://product-importer-acme.herokuapp.com

# Database and Redis URLs are automatically set by addons
```

4. **Deploy Application**
```bash
git push heroku main
```

5. **Run Database Migrations**
```bash
heroku run python manage.py migrate
```

6. **Create Superuser**
```bash
heroku run python manage.py createsuperuser
```

7. **Scale Dynos**
```bash
# 1 web dyno and 1 worker dyno
heroku ps:scale web=1 worker=1

# For production, scale up:
# heroku ps:scale web=2 worker=2
```

8. **Open Application**
```bash
heroku open
```

### Monitoring on Heroku

```bash
# View logs
heroku logs --tail

# Check dyno status
heroku ps

# Monitor resources
heroku addons:open papertrail  # If added
```

### Heroku Cost Optimization

- **Hobby Tier**: ~$14/month (web + worker + postgres + redis)
- **Production Tier**: ~$100/month (2x Standard dynos + Standard Postgres + Premium Redis)

## 🎨 Render Deployment

### Prerequisites
- Render account
- GitHub repository

### Step-by-Step Guide

1. **Connect Repository**
   - Go to https://render.com
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will detect `render.yaml`

2. **Review Services**
   The blueprint creates:
   - Web service (Daphne server)
   - Worker service (Celery)
   - PostgreSQL database
   - Redis instance

3. **Configure Environment Variables**
   Most are auto-configured via `render.yaml`, but verify:
   - `SECRET_KEY` (auto-generated)
   - `ALLOWED_HOSTS` (should include `.onrender.com`)
   - `DATABASE_URL` (auto-linked)
   - `REDIS_URL` (auto-linked)

4. **Deploy**
   - Click "Apply" to create all services
   - Render will build and deploy automatically
   - Monitor progress in dashboard

5. **Run Migrations** (if needed)
   In the web service shell:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Access Application**
   - URL will be provided: `https://your-app-name.onrender.com`

### Render Cost

- **Free Tier**: Free (with limitations)
- **Starter Tier**: ~$28/month (web + worker + postgres + redis)
- **Pro Tier**: ~$100+/month

## ☁️ AWS Deployment (EC2 + RDS + ElastiCache)

### Architecture
- EC2 instances for web and worker
- RDS PostgreSQL for database
- ElastiCache Redis for cache/queue
- Application Load Balancer
- Auto Scaling Groups

### Step-by-Step Guide

1. **Set Up RDS PostgreSQL**
```bash
# Via AWS Console or CLI
aws rds create-db-instance \
  --db-instance-identifier product-importer-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password YourPassword123 \
  --allocated-storage 20
```

2. **Set Up ElastiCache Redis**
```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id product-importer-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1
```

3. **Build Docker Image**
```bash
# Build image
docker build -t product-importer .

# Tag for ECR
docker tag product-importer:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/product-importer:latest

# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/product-importer:latest
```

4. **Deploy with ECS**
   - Create ECS cluster
   - Define task definitions for web and worker
   - Create services with desired count
   - Configure load balancer

5. **Configure Environment Variables**
   In ECS task definition, set:
   - `SECRET_KEY`
   - `DATABASE_URL` (from RDS)
   - `REDIS_URL` (from ElastiCache)
   - `ALLOWED_HOSTS`
   - `DEBUG=False`

### AWS Cost Estimate

- **Development**: ~$50/month
  - t3.small EC2 x2: $30
  - db.t3.micro RDS: $15
  - cache.t3.micro Redis: $12

- **Production**: ~$200+/month
  - t3.medium EC2 x4: $120
  - db.t3.small RDS: $50
  - cache.t3.small Redis: $25
  - Load Balancer: $20

## 🔵 Google Cloud Platform (Cloud Run)

### Prerequisites
- GCP account and project
- gcloud CLI installed

### Step-by-Step Guide

1. **Set Up Cloud SQL (PostgreSQL)**
```bash
gcloud sql instances create product-importer-db \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=us-central1
```

2. **Set Up Memorystore (Redis)**
```bash
gcloud redis instances create product-importer-redis \
  --size=1 \
  --region=us-central1 \
  --redis-version=redis_6_x
```

3. **Build and Push Container**
```bash
# Build image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/product-importer

# Or use docker
docker build -t gcr.io/YOUR_PROJECT_ID/product-importer .
docker push gcr.io/YOUR_PROJECT_ID/product-importer
```

4. **Deploy to Cloud Run (Web)**
```bash
gcloud run deploy product-importer-web \
  --image gcr.io/YOUR_PROJECT_ID/product-importer \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="DATABASE_URL=postgresql://...,REDIS_URL=redis://..." \
  --min-instances=1 \
  --max-instances=10
```

5. **Deploy Worker (Cloud Run Jobs)**
```bash
gcloud run jobs create product-importer-worker \
  --image gcr.io/YOUR_PROJECT_ID/product-importer \
  --command celery \
  --args "-A,config,worker,--loglevel=info" \
  --set-env-vars="DATABASE_URL=postgresql://...,REDIS_URL=redis://..."
```

### GCP Cost Estimate

- **Development**: ~$30/month
- **Production**: ~$150/month

## 🐳 Docker Swarm / Kubernetes

### Docker Swarm

1. **Initialize Swarm**
```bash
docker swarm init
```

2. **Deploy Stack**
```bash
docker stack deploy -c docker-compose.yml product-importer
```

### Kubernetes

1. **Apply Kubernetes Manifests**
```bash
kubectl apply -f k8s/
```

2. **Check Deployment**
```bash
kubectl get pods
kubectl get services
```

## 📊 Production Settings

### Required Environment Variables

```bash
# Django
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,.yourdomain.com

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Redis
REDIS_URL=redis://host:6379/0
CELERY_BROKER_URL=redis://host:6379/0
CELERY_RESULT_BACKEND=redis://host:6379/0

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

### Performance Tuning

**Celery Worker**
```bash
# Adjust concurrency based on server resources
celery -A config worker --loglevel=info --concurrency=8

# Use autoscale
celery -A config worker --autoscale=10,3
```

**Database Connection Pooling**
```python
# In settings.py
DATABASES = {
    'default': {
        'CONN_MAX_AGE': 600,
        'CONN_HEALTH_CHECKS': True,
    }
}
```

**Gunicorn Workers** (if using Gunicorn instead of Daphne)
```bash
gunicorn config.wsgi:application --workers 4 --threads 2 --bind 0.0.0.0:8000
```

## 🔒 Security Hardening

1. **Enable HTTPS**
```python
# settings.py
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
```

2. **Set Security Headers**
```python
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

3. **Use Secret Management**
   - AWS: AWS Secrets Manager
   - GCP: Secret Manager
   - Azure: Key Vault
   - Heroku: Config Vars

## 📈 Monitoring & Logging

### Heroku
```bash
# Add monitoring
heroku addons:create papertrail
heroku addons:create newrelic:wayne

# View logs
heroku logs --tail
```

### AWS CloudWatch
```python
# Install
pip install django-cloudwatch-logs

# Configure in settings.py
LOGGING = {
    'handlers': {
        'cloudwatch': {
            'class': 'watchtower.CloudWatchLogHandler',
        },
    },
}
```

### Sentry (Error Tracking)
```bash
pip install sentry-sdk
```

```python
# settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
)
```

## 🔄 CI/CD Pipeline

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to Heroku
        uses: akhileshns/heroku-deploy@v3.12.12
        with:
          heroku_api_key: ${{secrets.HEROKU_API_KEY}}
          heroku_app_name: "product-importer-acme"
          heroku_email: "your-email@example.com"
```

## ✅ Post-Deployment Checklist

- [ ] Application is accessible
- [ ] Database migrations applied
- [ ] Static files serving correctly
- [ ] WebSocket connections working
- [ ] Celery worker processing tasks
- [ ] Webhooks triggering successfully
- [ ] File uploads working
- [ ] Admin panel accessible
- [ ] Monitoring configured
- [ ] Backups scheduled
- [ ] SSL certificate active
- [ ] Domain configured
- [ ] Performance tested

---

**Need Help?** Contact DevOps team or open an issue on GitHub.

