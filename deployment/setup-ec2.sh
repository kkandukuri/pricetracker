#!/bin/bash
# EC2 Instance Setup Script for Price Tracker

set -e

echo "=========================================="
echo "EC2 Instance Setup for Price Tracker"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

echo "Step 1: Updating system packages..."
apt-get update
apt-get upgrade -y

echo ""
echo "Step 2: Installing required packages..."
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    ufw

echo ""
echo "Step 3: Installing Docker..."
# Add Docker's official GPG key
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start Docker
systemctl start docker
systemctl enable docker

echo ""
echo "Step 4: Creating pricetracker user..."
if ! id -u pricetracker &>/dev/null; then
    useradd -m -s /bin/bash pricetracker
    usermod -aG docker pricetracker
    echo "User 'pricetracker' created"
else
    echo "User 'pricetracker' already exists"
fi

echo ""
echo "Step 5: Setting up firewall..."
ufw --force enable
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 5000/tcp  # Direct access (can remove in production)
ufw status

echo ""
echo "Step 6: Creating application directory..."
APP_DIR="/home/pricetracker/app"
mkdir -p "$APP_DIR"
cd "$APP_DIR"

echo ""
echo "Step 7: Cloning repository..."
echo "Please enter the Git repository URL:"
read -r REPO_URL

if [ -n "$REPO_URL" ]; then
    if [ -d ".git" ]; then
        echo "Repository already cloned. Pulling latest changes..."
        sudo -u pricetracker git pull
    else
        sudo -u pricetracker git clone "$REPO_URL" .
    fi
else
    echo -e "${YELLOW}Skipping git clone. Please manually copy your code to $APP_DIR${NC}"
fi

# Set ownership
chown -R pricetracker:pricetracker "$APP_DIR"

echo ""
echo "Step 8: Creating data directories..."
sudo -u pricetracker mkdir -p data uploads downloads config

echo ""
echo "Step 9: Setting up systemd service..."
cat > /etc/systemd/system/pricetracker.service << 'EOF'
[Unit]
Description=Price Tracker Docker Container
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/pricetracker/app/deployment
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
User=pricetracker

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable pricetracker.service

echo ""
echo -e "${GREEN}=========================================="
echo "EC2 Setup Complete!"
echo "==========================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Switch to pricetracker user: sudo su - pricetracker"
echo "  2. Navigate to app: cd /home/pricetracker/app"
echo "  3. Review configuration: edit deployment/.env if needed"
echo "  4. Deploy application: cd deployment && ./deploy.sh"
echo ""
echo "Or use systemd service:"
echo "  sudo systemctl start pricetracker"
echo "  sudo systemctl status pricetracker"
echo ""
echo "Access the application:"
echo "  http://YOUR_EC2_PUBLIC_IP:5000"
echo "  http://YOUR_EC2_PUBLIC_IP (via nginx)"
echo ""
