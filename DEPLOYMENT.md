# 🚀 Deployment Guide

This guide covers multiple deployment options for the Enterprise Document Q&A System.

---

## 📋 Prerequisites

Before deploying, ensure you have:
- ✅ NVIDIA API Key ([Get it here](https://build.nvidia.com/))
- ✅ Git repository with your code
- ✅ All dependencies in `requirements.txt`

---

## 🐳 Option 1: Docker (Recommended)

### Single Container
```bash
# Build the image
docker build -t docqa-system .

# Run the container
docker run -d \
  -p 8000:8000 \
  -p 8501:8501 \
  -e NVIDIA_API_KEY="your_key_here" \
  -v $(pwd)/data:/app/data \
  --name docqa \
  docqa-system
```

### Docker Compose (Multi-Container)
```bash
# Create .env file
echo "NVIDIA_API_KEY=your_key_here" > .env

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Access:**
- Backend API: http://localhost:8000
- Frontend UI: http://localhost:8501
- API Docs: http://localhost:8000/docs

---

## ☁️ Option 2: Render.com (Easy Cloud Deploy)

### Step-by-Step:

1. **Create Account**: [render.com](https://render.com)

2. **Connect Repository**:
   - Click "New +" → "Blueprint"
   - Connect your GitHub/GitLab repo
   - Render will detect `render.yaml`

3. **Set Environment Variables**:
   - Go to Backend service settings
   - Add: `NVIDIA_API_KEY` = `your_key_here`

4. **Deploy**:
   - Click "Apply"
   - Wait 5-10 minutes for build

**Access:**
- Backend: `https://docqa-backend.onrender.com`
- Frontend: `https://docqa-frontend.onrender.com`

**Pricing**: 
- Free tier available (spins down after 15 min inactivity)
- Starter: $7/month per service ($14 total)

---

## 🚂 Option 3: Railway.app (Modern Platform)

### Deployment:

1. **Install Railway CLI**:
```bash
npm install -g @railway/cli
# or
brew install railway
```

2. **Login & Deploy**:
```bash
railway login
railway init
railway up
```

3. **Add Environment Variable**:
```bash
railway variables set NVIDIA_API_KEY=your_key_here
```

4. **Generate Domain**:
```bash
railway domain
```

**Pricing**: 
- Free: $5 credit/month
- Hobby: $5/month + usage

---

## 🎈 Option 4: Streamlit Community Cloud (Frontend Only)

**Note**: Only deploys Streamlit UI. Backend must be hosted elsewhere.

1. **Push to GitHub**:
```bash
git add .
git commit -m "Deploy to Streamlit Cloud"
git push
```

2. **Deploy**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select repo → `frontend/ui.py`

3. **Configure**:
   - Add `API_BASE_URL` secret pointing to your backend
   - Add `NVIDIA_API_KEY` secret

**Pricing**: FREE for public repos

---

## 🤗 Option 5: Hugging Face Spaces

### Setup:

1. **Create Space**:
   - Go to [huggingface.co/spaces](https://huggingface.co/spaces)
   - Click "Create new Space"
   - Select "Streamlit" SDK

2. **Push Code**:
```bash
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/docqa
git push hf main
```

3. **Configure**:
   - Add `NVIDIA_API_KEY` in Space settings → Secrets
   - Create `app.py` in root:
```python
import subprocess
import sys

# Start backend
backend = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
)

# Start frontend
subprocess.run(
    [sys.executable, "-m", "streamlit", "run", "frontend/ui.py", "--server.port", "7860"]
)
```

**Pricing**: FREE (with GPU options available)

---

## 🌐 Option 6: AWS EC2 (Full Control)

### Launch Instance:

```bash
# SSH into EC2
ssh -i key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python & dependencies
sudo apt install python3.11 python3.11-venv python3-pip -y

# Clone your repo
git clone https://github.com/yourusername/docqa.git
cd docqa

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export NVIDIA_API_KEY="your_key_here"

# Run with PM2 (process manager)
sudo npm install -g pm2
pm2 start "uvicorn app.main:app --host 0.0.0.0 --port 8000" --name backend
pm2 start "streamlit run frontend/ui.py --server.port 8501" --name frontend
pm2 save
pm2 startup
```

### Configure Security Group:
- Open ports: 8000, 8501, 22 (SSH)

**Pricing**: 
- t2.micro: FREE (first year)
- t3.small: ~$15/month

---

## 📊 Option 7: Google Cloud Run (Serverless)

### Deploy Backend:

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash

# Initialize
gcloud init

# Deploy backend
gcloud run deploy docqa-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars NVIDIA_API_KEY=your_key_here
```

### Deploy Frontend:

```bash
gcloud run deploy docqa-frontend \
  --source ./frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars API_BASE_URL=https://docqa-backend-xxx.run.app
```

**Pricing**: Pay-per-request (free tier: 2M requests/month)

---

## 🔒 Security Checklist

Before deploying to production:

- [ ] Set `NVIDIA_API_KEY` as environment variable (never hardcode)
- [ ] Enable HTTPS/SSL certificates
- [ ] Add authentication (OAuth, API keys)
- [ ] Set rate limiting on API endpoints
- [ ] Configure CORS properly
- [ ] Use secrets management service
- [ ] Enable monitoring & logging
- [ ] Set up automatic backups for vector store
- [ ] Configure firewall rules
- [ ] Use production ASGI server (Gunicorn + Uvicorn workers)

---

## 🎯 Recommended Deployment Strategy

### For Development/Testing:
→ **Docker Compose** (local) or **Streamlit Cloud** (free)

### For Small Teams:
→ **Railway** or **Render** ($10-20/month total)

### For Production:
→ **AWS EC2** + **Load Balancer** or **Google Cloud Run** (scalable)

### For Enterprise:
→ **Kubernetes** + **AWS EKS/GKE** with auto-scaling

---

## 📈 Monitoring & Logs

### Docker:
```bash
docker logs -f docqa
docker stats
```

### Cloud Platforms:
- Render: Built-in logs dashboard
- Railway: `railway logs`
- AWS: CloudWatch
- GCP: Cloud Logging

---

## 🆘 Troubleshooting

### Issue: Backend not connecting
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check logs
docker logs docqa-backend
```

### Issue: Out of memory
- Increase container memory limit
- Use FAISS with smaller index
- Enable swap memory

### Issue: Slow cold starts
- Use Render paid plan (always-on instances)
- Pre-warm with scheduled pings
- Consider serverless alternatives

---

## 📞 Support

- 📧 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions
- 📚 Docs: README.md

---

**Choose your platform and deploy in under 10 minutes!** 🚀
