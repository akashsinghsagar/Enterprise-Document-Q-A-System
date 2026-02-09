"""
Combined Streamlit + FastAPI app for Streamlit Cloud deployment
Runs FastAPI backend in background thread, then launches Streamlit UI
"""

import os
import sys
import threading
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set API_BASE_URL to localhost since backend runs in same process
os.environ["API_BASE_URL"] = "http://localhost:8000"


def run_fastapi_backend():
    """Run FastAPI server in background thread"""
    try:
        import uvicorn
        from app.main import app
        
        # Create required directories
        os.makedirs("data/documents", exist_ok=True)
        os.makedirs("data/vector_store", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
        logger.info("🚀 Starting FastAPI backend on port 8000...")
        
        # Run uvicorn server
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="warning"
        )
    except Exception as e:
        logger.error(f"❌ FastAPI backend failed to start: {type(e).__name__}: {str(e)}")
        raise


import requests

def backend_is_healthy() -> bool:
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except Exception:
        return False

# Start FastAPI in background thread only once
if os.environ.get("BACKEND_STARTED") != "1" and not backend_is_healthy():
    logger.info("Starting backend thread...")
    os.environ["BACKEND_STARTED"] = "1"
    backend_thread = threading.Thread(target=run_fastapi_backend, daemon=True)
    backend_thread.start()
else:
    logger.info("Backend already running, skipping start")

# Wait for backend to start and check if it's running
logger.info("Waiting for backend to initialize...")
time.sleep(5)

# Verify backend is accessible
max_retries = 10
for attempt in range(max_retries):
    if backend_is_healthy():
        logger.info("✅ Backend is running and healthy!")
        break
    if attempt < max_retries - 1:
        logger.info(f"Backend not ready yet, attempt {attempt + 1}/{max_retries}...")
        time.sleep(1)
    else:
        logger.warning("Backend may not be available - Streamlit will still start")

# Import and run Streamlit UI
sys.path.insert(0, str(project_root / "frontend"))

# Execute the Streamlit UI module
with open(project_root / "frontend" / "ui.py") as f:
    code = f.read()
    exec(code, {"__name__": "__main__"})
