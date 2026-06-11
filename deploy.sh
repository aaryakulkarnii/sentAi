#!/bin/bash
set -e

# ==============================================================================
# SentinelAI Oracle Cloud Deployment Script (Ubuntu / Oracle Linux)
# ==============================================================================

echo "[1/5] Updating system packages..."
sudo apt-get update -y || sudo yum update -y

echo "[2/5] Installing Docker and Docker Compose..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    # Install docker-compose plugin
    sudo apt-get install docker-compose-plugin -y || sudo yum install docker-compose-plugin -y
    echo "Docker installed successfully."
else
    echo "Docker is already installed."
fi

# Make sure Docker service is running
sudo systemctl enable docker
sudo systemctl start docker

echo "[3/5] Setting up the SentinelAI Repository..."
if [ ! -d "sentinelai" ]; then
    git clone https://github.com/aaryakulkarnii/sentinelai.git
fi
cd sentinelai

echo "[4/5] Configuring Environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "=========================================================="
    echo "WARNING: Created a new .env file."
    echo "Please edit the .env file and add your OPENAI_API_KEY"
    echo "and SECRET_KEY before continuing."
    echo "=========================================================="
fi

# Fetch the public IP of the Oracle Instance dynamically
PUBLIC_IP=$(curl -s ifconfig.me)
echo "PUBLIC_IP=${PUBLIC_IP}" >> .env
export PUBLIC_IP=${PUBLIC_IP}

echo "[5/5] Starting SentinelAI..."
# Navigate to infra folder to run docker compose
cd infra
sudo docker compose -f docker-compose.prod.yml up -d --build

echo "=========================================================="
echo "Deployment initiated!"
echo ""
echo "It may take a few minutes for all containers to download"
echo "and start. Once ready, you can access the dashboard at:"
echo "http://${PUBLIC_IP}"
echo ""
echo "Don't forget to run the seeding scripts inside the backend container:"
echo "sudo docker exec -it sentinelai-backend-1 bash"
echo "python scripts/seed_db.py"
echo "python scripts/load_mitre.py"
echo "=========================================================="
