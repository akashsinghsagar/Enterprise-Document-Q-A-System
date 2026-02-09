"""
Combined Streamlit + FastAPI app for Streamlit Cloud deployment
Runs FastAPI backend in background thread, then launches Streamlit UI
"""

import os
import sys
import threading
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set API_BASE_URL to localhost since backend runs in same process
os.environ["API_BASE_URL"] = "http://localhost:8000"


def run_fastapi_backend():
    """Run FastAPI server in background thread"""
    import uvicorn
    from app.main import app
    
    # Create required directories
    os.makedirs("data/documents", exist_ok=True)
    os.makedirs("data/vector_store", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Run uvicorn server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


# Start FastAPI in background thread
backend_thread = threading.Thread(target=run_fastapi_backend, daemon=True)
backend_thread.start()

# Wait for backend to start
time.sleep(3)

# Import and run Streamlit UI
sys.path.insert(0, str(project_root / "frontend"))

# Execute the Streamlit UI module
with open(project_root / "frontend" / "ui.py") as f:
    code = f.read()
    exec(code, {"__name__": "__main__"})
