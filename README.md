# Securing Web Application API

A secure Django REST Framework API implementing JWT authentication, HTTPS, rate limiting, and OWASP best practices.

## Project Overview

This project demonstrates modern API security practices including:
- **JWT Authentication**: Access and refresh tokens with rotation
- **HTTPS/TLS Configuration**: Secure transport layer
- **Rate Limiting**: Protection against brute-force and DDoS attacks
- **OWASP Best Practices**: Input validation, secure headers, error handling
- **Role-Based Access Control**: User permissions and authorization

## Features

### Security Features
- ✅ JWT-based authentication with access/refresh tokens
- ✅ Token rotation and blacklisting
- ✅ Rate limiting (IP-based and user-based)
- ✅ HTTPS/TLS ready configuration
- ✅ Security headers (CSP, X-Frame-Options, etc.)
- ✅ Input validation and sanitization
- ✅ Secure error handling (no information leakage)
- ✅ Request logging and monitoring
- ✅ CORS configuration
- ✅ SQL injection prevention (Django ORM)
- ✅ XSS protection

### API Endpoints

#### Authentication (`/api/accounts/`)
- `POST /api/accounts/register/` - User registration
- `POST /api/accounts/login/` - User login
- `POST /api/accounts/logout/` - User logout (blacklist token)
- `GET /api/accounts/profile/` - Get user profile
- `PUT /api/accounts/profile/` - Update user profile

#### JWT Tokens (`/api/token/`)
- `POST /api/token/refresh/` - Refresh access token
- `POST /api/token/verify/` - Verify token validity

#### API Endpoints (`/api/`)
- `GET /api/posts/` - List posts (authenticated)
- `POST /api/posts/` - Create post (authenticated)
- `GET /api/posts/{id}/` - Get post details
- `PUT /api/posts/{id}/` - Update post (author only)
- `DELETE /api/posts/{id}/` - Delete post (author only)
- `POST /api/posts/{id}/publish/` - Publish post (author only)
- `GET /api/public/posts/` - Public posts (rate limited)
- `GET /api/stats/` - User statistics (authenticated)

## Installation & Setup

### Prerequisites
- Python 3.12+
- SQLite (default, included with Python)
- Virtual environment

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd Securing-Web-Application-API
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
```bash
# Copy the example environment file
cp env.example .env

# Edit .env file with your settings
# IMPORTANT: Change SECRET_KEY and JWT_SECRET_KEY in production!
```

### Step 5: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### Step 7: Run Development Server
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## Environment Variables

Key environment variables (see `env.example` for full list):

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# JWT Settings
JWT_SECRET_KEY=your-jwt-secret-key
ACCESS_TOKEN_LIFETIME_MINUTES=15
REFRESH_TOKEN_LIFETIME_DAYS=7

# Security Settings
SECURE_SSL_REDIRECT=False  # Set to True in production with HTTPS
SESSION_COOKIE_SECURE=False  # Set to True in production
CSRF_COOKIE_SECURE=False  # Set to True in production

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

## Production Deployment

For detailed production deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

### Quick Production Setup

1. **Configure `.env` file for production:**
   - Set `DEBUG=False`
   - Set `SECURE_SSL_REDIRECT=True`
   - Set `SESSION_COOKIE_SECURE=True`
   - Set `CSRF_COOKIE_SECURE=True`
   - Configure `ALLOWED_HOSTS` with your domain

2. **Install Gunicorn:**
```bash
pip install gunicorn
```

3. **Run migrations and collect static files:**
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

4. **Run with Gunicorn:**
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

5. **Set up Nginx reverse proxy** (see DEPLOYMENT.md for detailed configuration)

6. **Configure SSL/TLS certificates** (Let's Encrypt recommended)

## API Usage Examples

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

### Access Protected Endpoint
```bash
curl -X GET http://localhost:8000/api/posts/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Refresh Token
```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

## Security Best Practices Implemented

### OWASP API Security Top 10
1. ✅ **Broken Object Level Authorization** - Implemented with user-based filtering
2. ✅ **Broken Authentication** - JWT with secure token handling
3. ✅ **Excessive Data Exposure** - Serializers filter sensitive data
4. ✅ **Lack of Resources & Rate Limiting** - Implemented throttling
5. ✅ **Broken Function Level Authorization** - Permission classes
6. ✅ **Mass Assignment** - Explicit field definitions
7. ✅ **Security Misconfiguration** - Secure headers and settings
8. ✅ **Injection** - Django ORM prevents SQL injection
9. ✅ **Improper Assets Management** - Version control and documentation
10. ✅ **Insufficient Logging & Monitoring** - Request logging implemented

### Additional Security Measures
- Password validation
- Secure headers (CSP, X-Frame-Options, etc.)
- CORS configuration
- Input sanitization
- Error handling without information leakage
- Token blacklisting
- IP tracking for login

## Testing

### Manual Testing
Use tools like Postman or curl to test endpoints.

### Security Testing
- Use OWASP ZAP for vulnerability scanning
- Test rate limiting
- Test authentication flows
- Test authorization boundaries

## Project Structure

```
Securing-Web-Application-API/
├── apps/
│   ├── accounts/          # User authentication and management
│   ├── api/               # Main API endpoints
│   └── security/          # Security utilities and middleware
├── config/                # Django project settings
├── logs/                  # Application logs
├── manage.py
├── requirements.txt
├── env.example            # Environment variables template
├── setup.sh               # Automated setup script
├── README.md              # Project documentation
├── QUICKSTART.md          # Quick start guide
└── DEPLOYMENT.md          # Production deployment guide
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational purposes as part of a university course.

## Author

**Otabek Dushamov**
- Student Number: 2427234
- Email: d.o.dushamov@wlv.ac.uk
- Supervisor: Dilshod Ergashev

## References

- [Django Security Documentation](https://docs.djangoproject.com/en/5.2/topics/security/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [OWASP API Security Top 10](https://owasp.org/API-Security/editions/2023/en/0x11-t10/)
- [JWT RFC 7519](https://tools.ietf.org/html/rfc7519)
