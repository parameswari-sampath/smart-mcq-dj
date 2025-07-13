# 🚀 Smart MCQ Platform - Docker Deployment Guide

## 📦 All-in-One Docker Image

This is a **complete, self-contained** Smart MCQ Platform that includes:
- Django Application (v1.4.1)
- PostgreSQL Database
- Nginx Web Server
- All dependencies and configurations

## 🎯 Usage Scenarios

### 🌐 Production Deployment (Your Domain)
```bash
# Build and run for production
docker-compose -f docker-compose.prod.yml up -d

# Access: https://smartmcq.meikuraledutech.in
```

### 🏠 Local Testing/Demo
```bash
# Build and run locally
docker-compose -f docker-compose.local.yml up -d

# Access: http://localhost:8080
```

### 🏢 Any Network Use
```bash
# Run for any network (LAN, WAN, VPN, etc.)
docker run -p 8080:80 your-username/smart-mcq

# Examples:
# LAN: http://192.168.1.100:8080
# Corporate: http://10.0.50.25:8080  
# VPN: http://172.16.0.10:8080
# Cloud: http://your-server-ip:8080
```

## 🛠 Building the Image

### Build Locally
```bash
# Build the image
docker build -t smart-mcq:latest .

# Run locally
docker run -p 8080:80 smart-mcq:latest
```

### Push to Docker Hub
```bash
# Tag for Docker Hub
docker tag smart-mcq:latest your-dockerhub-username/smart-mcq:latest
docker tag smart-mcq:latest your-dockerhub-username/smart-mcq:v1.4.1

# Push to Docker Hub
docker push your-dockerhub-username/smart-mcq:latest
docker push your-dockerhub-username/smart-mcq:v1.4.1
```

## 📖 Quick Start for Friends

### 1. One-Command Demo
```bash
docker run -p 8080:80 your-dockerhub-username/smart-mcq:latest
```

### 2. Access the Platform
- **Local**: `http://localhost:8080`
- **Network**: `http://YOUR-IP:8080` (works with ANY IP address)
- **Examples**: `http://192.168.1.100:8080`, `http://10.0.5.25:8080`, `http://172.16.0.10:8080`
- Default login: **admin** / **admin123**
- ⚠️ **Change password immediately!**

### 3. Network Flexibility
✅ **Works everywhere**: Home WiFi, office LAN, VPN, cloud servers, mobile hotspots
✅ **Any IP range**: 192.168.x.x, 10.x.x.x, 172.x.x.x, public IPs
✅ **Zero configuration**: Just run and access via any network IP

### 4. Features Available
- ✅ Create MCQ tests with multiple choice questions
- ✅ Student test-taking interface with timer
- ✅ Result viewing and management
- ✅ Answer visibility controls
- ✅ Test type indicators (Practice/Assessment)
- ✅ Complete v1.4.1 functionality

## 🔧 Configuration

### Environment Variables
```bash
# Production secrets (your deployment only)
SECRET_KEY=your-production-secret-key

# Database (included in container)
DB_NAME=smart_mcq_db
DB_USER=mcq_user
DB_PASSWORD=mcq_secure_password_2024
```

### Domain Access
- **Production**: `smartmcq.meikuraledutech.in` (hardcoded)
- **Local**: `localhost`, `127.0.0.1`
- **Any Network**: Works with ANY IP address (10.x.x.x, 172.x.x.x, 192.168.x.x, public IPs, etc.)

## 💾 Data Persistence

### Volumes (Important!)
```bash
# Data persists in Docker volumes
mcq_data:/var/lib/postgresql/15/main  # Database
mcq_media:/app/media                  # Uploaded files
mcq_logs:/app/logs                   # Application logs
```

### Backup Data
```bash
# Backup database
docker exec smart_mcq_production pg_dump -U mcq_user smart_mcq_db > backup.sql

# Backup volumes
docker run --rm -v mcq_data:/data -v $(pwd):/backup alpine tar czf /backup/mcq_backup.tar.gz /data
```

## 🔍 Monitoring

### Health Check
```bash
# Check if application is healthy
curl http://localhost:8080/health/
```

### View Logs
```bash
# All services
docker logs smart_mcq_production

# Follow logs
docker logs -f smart_mcq_production
```

### Resource Usage
```bash
# Check resource usage
docker stats smart_mcq_production
```

## 🚨 Important Notes

### ⚠️ For Educational/Testing Use Only
- This platform is designed for **local testing** and **educational purposes**
- For production use, proper security review and configuration required
- Default credentials should be changed immediately

### 🔒 Security Features
- Hardcoded production domain prevents misuse
- Local/LAN access only for non-production deployments
- CSRF protection enabled
- Security headers configured

### 💡 Performance
- **Optimized for 400 concurrent students**
- **1vCPU + 4GB RAM** recommended minimum
- Database tuned for classroom scenarios
- Static files served efficiently via Nginx

## 🆘 Troubleshooting

### Common Issues

**Container won't start:**
```bash
# Check logs
docker logs smart_mcq_production

# Rebuild image
docker-compose build --no-cache
```

**Database connection errors:**
```bash
# Check PostgreSQL status inside container
docker exec smart_mcq_production supervisorctl status postgresql
```

**Permission errors:**
```bash
# Fix volume permissions
docker exec smart_mcq_production chown -R app:app /app
```

### Reset Everything
```bash
# Stop and remove container
docker-compose down

# Remove volumes (⚠️ DELETES ALL DATA!)
docker volume rm mcq_data mcq_media mcq_logs

# Start fresh
docker-compose up -d
```

## 📞 Support

For issues or questions:
1. Check the logs: `docker logs container_name`
2. Verify health: `curl http://localhost:8080/health/`
3. Review this documentation
4. Check your network configuration for LAN access

---

**🎓 Smart MCQ Platform v1.4.1 - Built with Django + PostgreSQL + Docker**