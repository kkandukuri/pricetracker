# Deployment Scripts

Docker and EC2 deployment scripts for Price Tracker.

## 🚀 Quick Start

### Local Docker Deployment

```bash
cd deployment
./deploy.sh
```

Access: **http://localhost:5000**

---

## ☁️ AWS EC2 Deployment

### 1. Launch EC2 Instance

- **Type**: t3.medium (2 vCPU, 4GB RAM)
- **AMI**: Ubuntu 22.04 LTS
- **Storage**: 20GB+
- **Ports**: 22, 80, 443, 5000

### 2. Connect to EC2

```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

### 3. Run Setup

```bash
sudo su -
curl -O https://raw.githubusercontent.com/YOUR_REPO/deployment/setup-ec2.sh
chmod +x setup-ec2.sh
./setup-ec2.sh
```

### 4. Deploy

```bash
sudo su - pricetracker
cd /home/pricetracker/app/deployment
./deploy.sh
```

---

## 📁 Files

| File | Description |
|------|-------------|
| `Dockerfile` | Container image definition |
| `docker-compose.yml` | Multi-container setup |
| `nginx.conf` | Reverse proxy configuration |
| `.env.example` | Environment variables template |
| `deploy.sh` | Main deployment script |
| `setup-ec2.sh` | EC2 initial setup |
| `update.sh` | Update existing deployment |
| `DEPLOYMENT_GUIDE.md` | Complete deployment guide |

---

## 🔧 Common Commands

```bash
# Deploy
./deploy.sh

# Update
./update.sh

# View logs
docker logs -f pricetracker-app

# Restart
docker-compose restart

# Stop
docker-compose down

# Check status
docker ps
```

---

## 📚 Full Documentation

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for complete documentation including:
- Detailed setup instructions
- SSL/HTTPS configuration
- Domain setup
- Monitoring & maintenance
- Troubleshooting
- Security best practices

---

## ⚙️ Configuration

1. Copy environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit configuration:
   ```bash
   nano .env
   ```

3. Important settings:
   ```bash
   FLASK_ENV=production
   SECRET_KEY=your-secret-key
   WORKERS=4
   ```

---

## 🆘 Troubleshooting

**Container won't start:**
```bash
docker logs pricetracker-app
```

**Port already in use:**
```bash
sudo lsof -ti:5000 | xargs sudo kill -9
```

**Out of memory:**
```bash
docker stats
# Reduce workers or increase instance size
```

---

## 📞 Support

- Documentation: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- Logs: `docker logs pricetracker-app`
- Status: `docker ps`

---

**Quick Deploy: `./deploy.sh` 🚀**
