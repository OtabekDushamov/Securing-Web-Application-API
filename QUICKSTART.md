# Quick Start Guide

Get the Secure Web Application API running in 5 minutes!

## Prerequisites
- Python 3.12+
- Virtual environment (recommended)

## Steps

### 1. Setup Environment
```bash
# Copy environment file
cp env.example .env

# Edit .env and change SECRET_KEY (important!)
# Generate a secret key:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2. Install Dependencies
```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 3. Setup Database
```bash
# Create migrations
python manage.py makemigrations

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 4. Run Server
```bash
python manage.py runserver
```

## Test the API

### Register a User
```bash
curl -X POST http://localhost:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePass123!"
  }'
```

Save the `access` token from the response.

### Access Protected Endpoint
```bash
curl -X GET http://localhost:8000/api/posts/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

## API Endpoints

- `POST /api/accounts/register/` - Register new user
- `POST /api/accounts/login/` - Login and get tokens
- `POST /api/accounts/logout/` - Logout (blacklist token)
- `GET /api/accounts/profile/` - Get user profile (requires auth)
- `GET /api/posts/` - List posts (requires auth)
- `POST /api/posts/` - Create post (requires auth)
- `GET /api/public/posts/` - Public posts (no auth, rate limited)

## Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Check [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
3. Review security settings in `.env`
4. Test all endpoints with Postman or curl

## Troubleshooting

**Issue**: `ModuleNotFoundError`
- **Solution**: Make sure virtual environment is activated and dependencies are installed

**Issue**: `django.db.utils.OperationalError`
- **Solution**: Run migrations: `python manage.py migrate`

**Issue**: `SECRET_KEY` warning
- **Solution**: Generate a new secret key and update `.env` file

**Issue**: CORS errors
- **Solution**: Update `CORS_ALLOWED_ORIGINS` in `.env` with your frontend URL

