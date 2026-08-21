# 🚀 Deployment Guide: Career Intelligence Engine

This document provides step-by-step instructions to deploy the **Career Intelligence Engine** across multiple platforms, from **100% free cloud tiers** (Streamlit Cloud, Render, Hugging Face) to **production containerized environments** (Docker, AWS EC2).

---

## 📋 Table of Contents
1. [Prerequisites & Git Repository Setup](#1-prerequisites--git-repository-setup)
2. [Option A: Streamlit Community Cloud (Easiest & 100% Free)](#option-a-streamlit-community-cloud-easiest--100-free)
3. [Option B: Render.com (FastAPI Backend + Streamlit UI)](#option-b-rendercom-fastapi-backend--streamlit-ui)
4. [Option C: Hugging Face Spaces (Free ML Hosting)](#option-c-hugging-face-spaces-free-ml-hosting)
5. [Option D: Docker Container Deployment (Local or Any Cloud)](#option-d-docker-container-deployment-local-or-any-cloud)
6. [Option E: AWS EC2 / Linux VPS Production Deployment](#option-e-aws-ec2--linux-vps-production-deployment)
7. [Environment Variables & Security Checklist](#environment-variables--security-checklist)

---

## 1. Prerequisites & Git Repository Setup

Before deploying to any cloud service, push your codebase to GitHub:

### Step 1.1: Initialize Git & Commit Code
Open your terminal in the project directory (`Career Intelligence Engine`):

```bash
# Initialize git repository
git init

# Add all project files
git add .

# Create initial commit
git commit -m "Initial commit: Career Intelligence Engine full platform"
```

### Step 1.2: Push to GitHub
1. Go to [GitHub.com](https://github.com) and click **New Repository**.
2. Name it: `career-intelligence-engine` (set to Public or Private).
3. Push your local repository:

```bash
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/career-intelligence-engine.git
git push -u origin main
```

---

## Option A: Streamlit Community Cloud (Easiest & 100% Free)

> **Best for:** Showing your live interactive dashboard to recruiters with zero cloud fees and instant URL sharing.

### Step-by-Step Instructions:
1. Go to [share.streamlit.io](https://share.streamlit.io/) and log in with your **GitHub account**.
2. Click the **"Create app"** button.
3. Select your repository: `YOUR_GITHUB_USERNAME/career-intelligence-engine`.
4. Fill in the deployment settings:
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL:** Customize your subdomain (e.g. `career-intelligence-engine.streamlit.app`).
5. Click **"Deploy!"**.
6. Streamlit Cloud will automatically install all dependencies from `requirements.txt` and boot your dashboard in 1-2 minutes.

---

## Option B: Render.com (FastAPI Backend + Streamlit UI)

> **Best for:** Hosting both your **FastAPI REST API** (with live `/docs`) and the **Streamlit Web UI** on free web services.

### Deploying the FastAPI Backend:
1. Sign up / Log in at [Render.com](https://render.com).
2. Click **New +** $\to$ **Web Service**.
3. Connect your GitHub repository: `career-intelligence-engine`.
4. Configure the Web Service:
   - **Name:** `career-intelligence-api`
   - **Environment:** `Python 3`
   - **Region:** Choose the closest (e.g. Singapore or Frankfurt)
   - **Branch:** `main`
   - **Build Command:**
     ```bash
     pip install -r requirements.txt && python data/generate_datasets.py && python -m src.models.train_models
     ```
   - **Start Command:**
     ```bash
     uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance Type:** Free
5. Click **Create Web Service**. Once deployed, your interactive API will be live at:
   `https://career-intelligence-api.onrender.com/docs`

---

## Option C: Hugging Face Spaces (Free ML Hosting)

> **Best for:** Machine Learning portfolios and AI communities.

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces) and click **"Create new Space"**.
2. Set Space Name: `career-intelligence-engine`.
3. Choose **Space SDK**: **Streamlit**.
4. Set Space hardware: **Free (CPU basic - 2 vCPU, 16 GB RAM)**.
5. Clone the space repo or connect your GitHub repository.
6. Make sure `app.py` and `requirements.txt` are in the root directory.
7. Hugging Face will build the container and provide an embeddable URL.

---

## Option D: Docker Container Deployment (Local or Any Cloud)

> **Best for:** Running both the Streamlit UI and FastAPI backend together in isolated containers.

### Step-by-Step Instructions:

```bash
# 1. Build and launch all services in the background
docker compose up -d --build

# 2. Check running container status
docker compose ps

# 3. View real-time logs
docker compose logs -f
```

**Access Endpoints:**
- **Streamlit Web Dashboard:** `http://localhost:8501`
- **FastAPI REST API & Swagger UI:** `http://localhost:8000/docs`

To stop containers:
```bash
docker compose down
```

---

## Option E: AWS EC2 / Linux VPS Production Deployment

> **Best for:** Dedicated production server on Ubuntu (AWS EC2, DigitalOcean, Hetzner, Linode).

### Step E.1: Launch AWS EC2 Instance
1. Launch an `Ubuntu 22.04 LTS` or `Ubuntu 24.04 LTS` instance (`t3.small` or `t3.medium` recommended).
2. Configure **Security Group** inbound rules:
   - Port `22` (SSH)
   - Port `80` (HTTP)
   - Port `443` (HTTPS)
   - Port `8501` (Streamlit)
   - Port `8000` (FastAPI)

### Step E.2: SSH into EC2 & Install Docker
```bash
ssh -i "your-key.pem" ubuntu@YOUR_EC2_PUBLIC_IP

# Update packages and install Docker
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose git

# Allow ubuntu user to run Docker
sudo usermod -aG docker ubuntu
newgrp docker
```

### Step E.3: Clone Repo & Run with Docker Compose
```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/career-intelligence-engine.git
cd "career-intelligence-engine"

# Build and start background daemon
docker-compose up -d --build
```

### Step E.4: (Optional) Set Up Nginx Reverse Proxy & SSL
To access via domain `https://your-domain.com`:

1. Install Nginx & Certbot:
```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

2. Create Nginx config `/etc/nginx/sites-available/career_engine`:
```nginx
server {
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. Enable site and install free SSL certificate:
```bash
sudo ln -s /etc/nginx/sites-available/career_engine /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo certbot --nginx -d your-domain.com
```

---

## 🔒 Environment Variables & Pre-Flight Checklist

- [x] Ensure `requirements.txt` contains all pinned dependencies (`streamlit`, `fastapi`, `uvicorn`, `pypdf`, `reportlab`, `scikit-learn`, `plotly`, `pandas`, `numpy`).
- [x] Run `python data/generate_datasets.py` and `python -m src.models.train_models` before runtime if not including generated artifacts in git.
- [x] Verify that port `8501` (Streamlit) or `8000` (FastAPI) is properly mapped.
- [x] Test that PDF resume uploads and PDF exports work without file path permission errors.
