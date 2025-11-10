# Deployment Guide - Price Tracker

Complete guide for deploying Price Tracker to production using Docker and AWS EC2.

## 📋 Table of Contents

1. [Quick Start with Docker](#quick-start-with-docker)
2. [AWS EC2 Deployment](#aws-ec2-deployment)
3. [Docker Configuration](#docker-configuration)
4. [Production Setup](#production-setup)
5. [Monitoring & Maintenance](#monitoring--maintenance)
6. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start with Docker

### Prerequisites

- Docker installed ([Install Docker](https://docs.docker.com/engine/install/))
- Docker Compose installed ([Install Compose](https://docs.docker.com/compose/install/))
- 2GB+ RAM available
- 10GB+ disk space

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd pricetracker
```

### 2. Deploy with Docker

```bash
cd deployment
chmod +x deploy.sh
./deploy.sh
```

That's it! Access at **http://localhost:5000**

---

## ☁️ AWS EC2 Deployment

### Step 1: Launch EC2 Instance

**Recommended specifications:**
- **Instance Type**: t3.medium or larger (2 vCPU, 4GB RAM)
- **AMI**: Ubuntu 22.04 LTS
- **Storage**: 20GB+ EBS volume
- **Security Group**: Allow ports 22 (SSH), 80 (HTTP), 443 (HTTPS), 5000 (optional)

**Launch instance:**

```bash
# Using AWS CLI
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name your-key-pair \
  --security-group-ids sg-xxxxxx \
  --subnet-id subnet-xxxxxx \
  --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":20}}]' \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=PriceTracker}]'
```

Or use AWS Console:
1. Go to EC2 Dashboard
2. Click "Launch Instance"
3. Choose Ubuntu 22.04 LTS
4. Select t3.medium
5. Configure security group
6. Launch

### Step 2: Connect to EC2

```bash
# Get your instance's public IP
aws ec2 describe-instances --instance-ids i-xxxxx --query 'Reservations[0].Instances[0].PublicIpAddress'

# Connect via SSH
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

### Step 3: Run Setup Script

```bash
# Download setup script
curl -O https://raw.githubusercontent.com/YOUR_REPO/deployment/setup-ec2.sh

# Make executable
chmod +x setup-ec2.sh

# Run setup (as root)
sudo ./setup-ec2.sh
```

The script will:
- ✅ Update system packages
- ✅ Install Docker & Docker Compose
- ✅ Create pricetracker user
- ✅ Configure firewall
- ✅ Clone repository
- ✅ Setup systemd service

### Step 4: Deploy Application

```bash
# Switch to pricetracker user
sudo su - pricetracker

# Navigate to app directory
cd /home/pricetracker/app

# Deploy
cd deployment
./deploy.sh
```

### Step 5: Access Application

Open browser:
- **http://YOUR_EC2_PUBLIC_IP:5000** (direct access)
- **http://YOUR_EC2_PUBLIC_IP** (via nginx)

---

## 🐳 Docker Configuration

### Dockerfile

Located at `deployment/Dockerfile`:

**Features:**
- Python 3.11 slim base image
- Chrome/Chromium for Selenium
- Gunicorn WSGI server
- Non-root user for security
- Health checks

### docker-compose.yml

Located at `deployment/docker-compose.yml`:

**Services:**
- `pricetracker` - Main Flask application
- `nginx` - Reverse proxy (optional)

**Volumes:**
- `data/` - SQLite database
- `uploads/` - Uploaded URL files
- `downloads/` - Generated CSV files
- `config/` - Configuration files

### Commands

```bash
# Build image
docker-compose build

# Start containers
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down

# Restart
docker-compose restart

# Check status
docker-compose ps
```

---

## 🏭 Production Setup

### 1. Environment Configuration

Copy and edit environment file:

```bash
cp deployment/.env.example deployment/.env
nano deployment/.env
```

**Important settings:**

```bash
# Production mode
FLASK_ENV=production
FLASK_DEBUG=0

# Security (CHANGE THIS!)
SECRET_KEY=your-random-secret-key-here

# Performance
WORKERS=4
THREADS=2
TIMEOUT=120
```

### 2. SSL/HTTPS Setup

**Using Let's Encrypt:**

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

**Update nginx.conf:**

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # ... rest of config
}
```

### 3. Domain Setup

**Point domain to EC2:**

1. Go to your DNS provider (Route53, Cloudflare, etc.)
2. Add A record:
   - Name: `@` (or subdomain)
   - Value: `YOUR_EC2_PUBLIC_IP`
   - TTL: 300

3. Wait for DNS propagation (5-30 minutes)

4. Test: `ping your-domain.com`

### 4. Firewall Configuration

```bash
# Allow HTTP/HTTPS only
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Optional: Remove direct app access
sudo ufw delete allow 5000/tcp

# Enable firewall
sudo ufw enable
```

### 5. Auto-Start on Boot

**Using systemd:**

```bash
# Enable service
sudo systemctl enable pricetracker

# Start service
sudo systemctl start pricetracker

# Check status
sudo systemctl status pricetracker
```

---

## 📊 Monitoring & Maintenance

### Viewing Logs

```bash
# Application logs
docker logs -f pricetracker-app

# Last 100 lines
docker logs --tail 100 pricetracker-app

# Nginx logs
docker logs -f pricetracker-nginx

# System logs
journalctl -u pricetracker -f
```

### Health Checks

```bash
# Check if app is running
docker ps

# Health check endpoint
curl http://localhost:5000/api/stats

# Container stats
docker stats pricetracker-app
```

### Backup Database

```bash
# Backup SQLite database
docker exec pricetracker-app \
  sqlite3 /app/data/products.db ".backup '/app/data/backup.db'"

# Copy to host
docker cp pricetracker-app:/app/data/backup.db ./backup-$(date +%Y%m%d).db

# Automated backup script
cat > /home/pricetracker/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/pricetracker/backups"
mkdir -p "$BACKUP_DIR"
docker exec pricetracker-app \
  sqlite3 /app/data/products.db \
  ".backup '/app/data/backup-$(date +%Y%m%d-%H%M%S).db'"
docker cp pricetracker-app:/app/data/backup-*.db "$BACKUP_DIR/"
# Keep only last 7 days
find "$BACKUP_DIR" -name "backup-*.db" -mtime +7 -delete
EOF

chmod +x /home/pricetracker/backup.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /home/pricetracker/backup.sh
```

### Update Application

```bash
cd /home/pricetracker/app/deployment
./update.sh
```

This will:
1. Pull latest code
2. Rebuild Docker image
3. Restart containers
4. Clean up old images

### Scaling

**Increase workers:**

Edit `deployment/Dockerfile`:

```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "8", ...]
```

Rebuild: `docker-compose up -d --build`

**Add more resources:**

```bash
# Resize EC2 instance
aws ec2 modify-instance-attribute \
  --instance-id i-xxxxx \
  --instance-type t3.large
```

---

## 🐛 Troubleshooting

### Issue: Container won't start

**Check logs:**
```bash
docker logs pricetracker-app
```

**Common causes:**
- Port 5000 already in use
- Missing environment variables
- Database file corruption

**Solutions:**
```bash
# Kill process on port 5000
sudo lsof -ti:5000 | xargs sudo kill -9

# Reset database
docker exec pricetracker-app rm /app/data/products.db
docker-compose restart
```

### Issue: Out of memory

**Check memory:**
```bash
docker stats pricetracker-app
free -h
```

**Solutions:**
```bash
# Reduce workers in Dockerfile
--workers 2 --threads 1

# Add swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Issue: Selenium not working

**Check Chrome installation:**
```bash
docker exec pricetracker-app which chromium
docker exec pricetracker-app chromium --version
```

**Solutions:**
```bash
# Rebuild with --no-cache
docker-compose build --no-cache
docker-compose up -d
```

### Issue: Can't access from internet

**Check security group:**
```bash
aws ec2 describe-security-groups --group-ids sg-xxxxx
```

**Solutions:**
```bash
# Add inbound rule
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0
```

### Issue: Slow performance

**Check resource usage:**
```bash
docker stats
top
htop
```

**Solutions:**
1. Increase instance size (t3.medium → t3.large)
2. Add more workers
3. Enable caching
4. Optimize database queries

---

## 📁 File Structure

```
deployment/
├── Dockerfile              # Container image definition
├── docker-compose.yml      # Multi-container orchestration
├── nginx.conf             # Nginx reverse proxy config
├── .env.example           # Environment variables template
├── deploy.sh              # Deployment script
├── setup-ec2.sh           # EC2 initial setup
├── update.sh              # Update script
└── DEPLOYMENT_GUIDE.md    # This file
```

---

## 🔒 Security Best Practices

### 1. Use HTTPS

Always use SSL/TLS in production with Let's Encrypt.

### 2. Restrict Access

```bash
# Firewall
sudo ufw allow from TRUSTED_IP to any port 5000

# Or use nginx auth
htpasswd -c /etc/nginx/.htpasswd admin
```

### 3. Regular Updates

```bash
# System updates
sudo apt-get update && sudo apt-get upgrade

# Docker updates
sudo apt-get install docker-ce

# Application updates
cd /home/pricetracker/app/deployment && ./update.sh
```

### 4. Environment Variables

Never commit `.env` file. Always use `.env.example` as template.

### 5. Database Backups

Schedule regular backups (see Backup section above).

---

## 📞 Support

**Issues?**
- Check logs: `docker logs pricetracker-app`
- Review documentation
- Create GitHub issue

**Need help?**
- Email: support@example.com
- Slack: #pricetracker
- Docs: https://docs.example.com

---

## ✅ Deployment Checklist

**Before deploying:**
- [ ] EC2 instance launched
- [ ] Security groups configured
- [ ] Domain configured (if using)
- [ ] SSL certificate obtained
- [ ] Environment variables set
- [ ] Backups configured

**After deploying:**
- [ ] Application accessible
- [ ] SSL working (if configured)
- [ ] Logs are clean
- [ ] Health check passing
- [ ] Auto-start enabled
- [ ] Monitoring setup

---

## 🎯 Quick Reference

```bash
# Deploy
cd deployment && ./deploy.sh

# Logs
docker logs -f pricetracker-app

# Restart
docker-compose restart

# Update
./update.sh

# Stop
docker-compose down

# Backup
docker exec pricetracker-app sqlite3 /app/data/products.db ".backup 'backup.db'"

# Status
docker ps
docker-compose ps
systemctl status pricetracker
```

---

**Happy Deploying! 🚀**
