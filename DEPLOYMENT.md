# Deployment Guide

This guide covers deploying the Secure Web Application API to production.

## Pre-Deployment Checklist

- [ ] Change `SECRET_KEY` in `.env`
- [ ] Change `JWT_SECRET_KEY` in `.env`
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Set `SECURE_SSL_REDIRECT=True`
- [ ] Set `SESSION_COOKIE_SECURE=True`
- [ ] Set `CSRF_COOKIE_SECURE=True`
- [ ] Database is configured (SQLite by default)
- [ ] Set up SSL/TLS certificates
- [ ] Configure reverse proxy (Nginx)
- [ ] Set up logging and monitoring
- [ ] Configure backup strategy

## Environment Variables for Production

```env
# Django Settings
SECRET_KEY=<generate-strong-secret-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database Configuration (SQLite - default)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
# SQLite doesn't require USER, PASSWORD, HOST, or PORT
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

# JWT Settings
JWT_SECRET_KEY=<generate-strong-jwt-secret>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_LIFETIME_MINUTES=15
REFRESH_TOKEN_LIFETIME_DAYS=7

# Security Settings (MUST be True in production)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
X_FRAME_OPTIONS=DENY

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# CORS Settings
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CORS_ALLOW_CREDENTIALS=True

# Logging
LOG_LEVEL=WARNING
```

## Server Setup

### 1. Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `env.example` to `.env` and update with your production values:
```bash
cp env.example .env
nano .env  # Edit with your settings
```

### 3. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

## Nginx + Gunicorn Setup

1. **Install Nginx:**
```bash
sudo apt-get install nginx
```

2. **Create Nginx configuration** (`/etc/nginx/sites-available/secure-api`):
```nginx
upstream django {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    
    location / {
        limit_req zone=api_limit burst=20 nodelay;
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/staticfiles/;
    }

    location /media/ {
        alias /path/to/media/;
    }
}
```

3. **Enable the site:**
```bash
sudo ln -s /etc/nginx/sites-available/secure-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

4. **Set up SSL with Let's Encrypt:**
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

5. **Install Gunicorn:**
```bash
pip install gunicorn
```

6. **Run Gunicorn as a service** (`/etc/systemd/system/secure-api.service`):
```ini
[Unit]
Description=Secure API Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/project
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    --timeout 30 \
    --access-logfile /path/to/logs/gunicorn_access.log \
    --error-logfile /path/to/logs/gunicorn_error.log \
    config.wsgi:application

[Install]
WantedBy=multi-user.target
```

**Note:** Adjust the Gunicorn configuration (workers, bind address, timeouts, etc.) according to your server's resources and requirements.

7. **Start the service:**
```bash
sudo systemctl daemon-reload
sudo systemctl start secure-api
sudo systemctl enable secure-api
sudo systemctl status secure-api  # Check status
```

## Security Hardening

### 1. Generate Strong Secret Keys

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 2. Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### 3. Database Security

- SQLite database file should have proper file permissions (readable/writable by application user only)
- Regular backups of the database file
- Store database file in a secure location
- Consider file system encryption for sensitive data

### 4. File Permissions

```bash
# Set proper permissions
chmod 600 .env
chmod 755 manage.py
chmod 600 db.sqlite3  # SQLite database file should be readable/writable by owner only
```

### 5. Monitoring and Logging

- Set up log rotation
- Monitor error logs
- Set up alerts for security events
- Regular security audits

## Backup Strategy

### Database Backup

```bash
# SQLite backup (simply copy the database file)
cp db.sqlite3 backup_$(date +%Y%m%d).sqlite3

# Or create a compressed backup
tar -czf backup_$(date +%Y%m%d).tar.gz db.sqlite3
```

### Automated Backups

Create a backup script (`backup.sh`):
```bash
#!/bin/bash
BACKUP_DIR="/path/to/backups"
mkdir -p $BACKUP_DIR
cp db.sqlite3 $BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sqlite3
# Keep only last 30 days of backups
find $BACKUP_DIR -name "backup_*.sqlite3" -mtime +30 -delete
```

Create a cron job:
```bash
0 2 * * * /path/to/backup.sh
```

## Monitoring

### Health Check Endpoint

Add to your API:
```python
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    return Response({'status': 'healthy'})
```

### Log Monitoring

Monitor logs for:
- Failed authentication attempts
- Rate limit violations
- Error patterns
- Unusual traffic

## Troubleshooting

### Common Issues

1. **502 Bad Gateway**: Check Gunicorn is running
2. **Static files not loading**: Run `collectstatic`
3. **Database connection errors**: Check database credentials
4. **SSL errors**: Verify certificate paths and permissions

### Debug Mode

If you need to debug in production temporarily:
1. Set `DEBUG=True` in `.env`
2. Check error logs
3. **IMPORTANT**: Set back to `False` immediately after debugging

## Post-Deployment

1. Test all endpoints
2. Verify SSL certificate
3. Check security headers
4. Test rate limiting
5. Monitor logs
6. Set up automated backups
7. Document any custom configurations

