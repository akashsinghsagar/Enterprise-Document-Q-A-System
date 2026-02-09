#!/bin/bash

# Quick Deploy Script for Enterprise Document Q&A System
# Usage: ./deploy.sh [docker|render|railway|streamlit]

set -e

DEPLOY_METHOD="${1:-docker}"

echo "🚀 Enterprise Document Q&A - Quick Deploy"
echo "=========================================="
echo ""

# Check for NVIDIA API Key
if [ -z "$NVIDIA_API_KEY" ]; then
    echo "⚠️  NVIDIA_API_KEY not found in environment"
    read -p "Enter your NVIDIA API Key: " NVIDIA_API_KEY
    export NVIDIA_API_KEY
fi

case $DEPLOY_METHOD in
    docker)
        echo "🐳 Deploying with Docker..."
        echo ""
        
        # Build image
        echo "📦 Building Docker image..."
        docker build -t docqa-system:latest .
        
        # Stop existing container if running
        docker stop docqa 2>/dev/null || true
        docker rm docqa 2>/dev/null || true
        
        # Run container
        echo "🏃 Starting container..."
        docker run -d \
            -p 8000:8000 \
            -p 8501:8501 \
            -e NVIDIA_API_KEY="$NVIDIA_API_KEY" \
            -v "$(pwd)/data:/app/data" \
            -v "$(pwd)/logs:/app/logs" \
            --name docqa \
            --restart unless-stopped \
            docqa-system:latest
        
        echo ""
        echo "✅ Deployment complete!"
        echo ""
        echo "🌐 Access your application:"
        echo "   Frontend: http://localhost:8501"
        echo "   Backend:  http://localhost:8000"
        echo "   API Docs: http://localhost:8000/docs"
        echo ""
        echo "📝 View logs: docker logs -f docqa"
        ;;
        
    docker-compose)
        echo "🐳 Deploying with Docker Compose..."
        echo ""
        
        # Create .env file
        echo "NVIDIA_API_KEY=$NVIDIA_API_KEY" > .env
        
        # Stop existing services
        docker-compose down 2>/dev/null || true
        
        # Start services
        echo "🏃 Starting services..."
        docker-compose up -d --build
        
        echo ""
        echo "✅ Deployment complete!"
        echo ""
        echo "🌐 Access your application:"
        echo "   Frontend: http://localhost:8501"
        echo "   Backend:  http://localhost:8000"
        echo ""
        echo "📝 View logs: docker-compose logs -f"
        ;;
        
    render)
        echo "☁️  Deploying to Render.com..."
        echo ""
        
        # Check if git repo exists
        if [ ! -d .git ]; then
            echo "Initializing git repository..."
            git init
            git add .
            git commit -m "Initial commit for Render deployment"
        fi
        
        echo "📋 Next steps:"
        echo "1. Push code to GitHub/GitLab"
        echo "2. Go to https://render.com"
        echo "3. Click 'New +' → 'Blueprint'"
        echo "4. Connect your repository"
        echo "5. Add NVIDIA_API_KEY environment variable"
        echo "6. Click 'Apply'"
        echo ""
        echo "💡 Render will automatically detect render.yaml"
        ;;
        
    railway)
        echo "🚂 Deploying to Railway..."
        echo ""
        
        # Check if Railway CLI is installed
        if ! command -v railway &> /dev/null; then
            echo "Installing Railway CLI..."
            npm install -g @railway/cli
        fi
        
        # Initialize and deploy
        echo "🔐 Login to Railway..."
        railway login
        
        echo "🚀 Deploying..."
        railway init
        railway variables set NVIDIA_API_KEY="$NVIDIA_API_KEY"
        railway up
        
        echo ""
        echo "✅ Deployment complete!"
        echo "🌐 Generate domain with: railway domain"
        ;;
        
    streamlit)
        echo "🎈 Preparing for Streamlit Community Cloud..."
        echo ""
        
        # Check if git repo exists
        if [ ! -d .git ]; then
            echo "Initializing git repository..."
            git init
            git add .
            git commit -m "Initial commit for Streamlit Cloud"
        fi
        
        echo "📋 Next steps:"
        echo "1. Push code to GitHub (must be public)"
        echo "   git remote add origin https://github.com/yourusername/docqa.git"
        echo "   git push -u origin main"
        echo ""
        echo "2. Go to https://share.streamlit.io"
        echo "3. Click 'New app'"
        echo "4. Select your repo and set main file: frontend/ui.py"
        echo "5. Add secrets in Advanced settings:"
        echo "   API_BASE_URL = your_backend_url"
        echo "   NVIDIA_API_KEY = $NVIDIA_API_KEY"
        echo ""
        echo "⚠️  Note: You need to deploy backend separately!"
        ;;
        
    local)
        echo "💻 Starting local development servers..."
        echo ""
        
        # Install dependencies
        echo "📦 Installing dependencies..."
        pip install -r requirements.txt
        
        # Start backend in background
        echo "🔧 Starting backend..."
        python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
        BACKEND_PID=$!
        
        # Wait for backend to start
        sleep 3
        
        # Start frontend
        echo "🎨 Starting frontend..."
        streamlit run frontend/ui.py --server.port 8501 &
        FRONTEND_PID=$!
        
        echo ""
        echo "✅ Local servers running!"
        echo ""
        echo "🌐 Access your application:"
        echo "   Frontend: http://localhost:8501"
        echo "   Backend:  http://localhost:8000"
        echo ""
        echo "Press Ctrl+C to stop servers"
        
        # Wait for interrupt
        trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
        wait
        ;;
        
    *)
        echo "❌ Unknown deployment method: $DEPLOY_METHOD"
        echo ""
        echo "Usage: ./deploy.sh [METHOD]"
        echo ""
        echo "Available methods:"
        echo "  docker          - Deploy with single Docker container (default)"
        echo "  docker-compose  - Deploy with Docker Compose"
        echo "  render          - Deploy to Render.com"
        echo "  railway         - Deploy to Railway.app"
        echo "  streamlit       - Deploy to Streamlit Cloud"
        echo "  local           - Run local development servers"
        echo ""
        exit 1
        ;;
esac
