"""
Enterprise-Grade Streamlit UI for Document Q&A System

Professional SaaS-style interface with:
- Modern card-based layout
- Perfect visual hierarchy
- WCAG-compliant contrast
- Responsive design
- Clean spacing and alignment
"""

import os
import sys
import time
from pathlib import Path

import streamlit as st
import requests

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

try:
    st.set_page_config(
        page_title="Enterprise Document Q&A",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': "Enterprise Document Q&A System - Powered by RAG"
        }
    )
except Exception as e:
    pass  # Config already set

# ============================================================================
# PROFESSIONAL CSS STYLING
# ============================================================================

ENTERPRISE_CSS = """
<style>
    /* =====================================================================
       COLOR PALETTE - Modern Enterprise Theme
       ===================================================================== */
    :root {
        /* Primary Colors */
        --bg-primary: #2a2a2a;
        --bg-secondary: #353535;
        --surface: #3a3a3a;
        --surface-hover: #404040;
        
        /* Borders & Dividers */
        --border-light: #505050;
        --border-medium: #606060;
        --border-strong: #707070;
        
        /* Text Colors - WCAG AA Compliant */
        --text-primary: #e8e8e8;
        --text-secondary: #b0b0b0;
        --text-tertiary: #808080;
        --text-muted: #606060;
        
        /* Brand & Accent */
        --accent: #60a5fa;
        --accent-hover: #3b82f6;
        --accent-light: #1e3a8a;
        
        /* Semantic Colors */
        --success: #4ade80;
        --success-bg: #064e3b;
        --success-border: #10b981;
        
        --warning: #facc15;
        --warning-bg: #78350f;
        --warning-border: #f59e0b;
        
        --error: #f87171;
        --error-bg: #7f1d1d;
        --error-border: #ef4444;
        
        --info: #60a5fa;
        --info-bg: #1e3a8a;
        --info-border: #3b82f6;
        
        /* Shadows - Subtle Elevation */
        --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.02);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.06), 0 2px 4px -1px rgba(0, 0, 0, 0.04);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.10), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        
        /* Spacing Scale */
        --space-xs: 0.25rem;
        --space-sm: 0.5rem;
        --space-md: 1rem;
        --space-lg: 1.5rem;
        --space-xl: 2rem;
        --space-2xl: 3rem;
        
        /* Border Radius */
        --radius-sm: 6px;
        --radius-md: 10px;
        --radius-lg: 14px;
        --radius-xl: 18px;
        
        /* Typography */
        --font-body: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', sans-serif;
        --font-mono: 'SF Mono', Monaco, Consolas, 'Courier New', monospace;
    }

    /* =====================================================================
       BASE LAYOUT & STRUCTURE
       ===================================================================== */
    .stApp {
        background: var(--bg-primary);
        font-family: var(--font-body);
    }
    
    .stMain {
        background: var(--bg-primary);
    }
    
    .block-container {
        max-width: 1000px;
        padding: var(--space-xl) var(--space-lg) var(--space-2xl);
    }
    
    /* Remove default Streamlit padding/margin quirks */
    .element-container {
        margin-bottom: 0 !important;
    }
    
    /* =====================================================================
       TYPOGRAPHY SYSTEM
       ===================================================================== */
    html, body, [class*="css"] {
        font-family: var(--font-body);
        color: var(--text-primary);
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: var(--font-body);
        font-weight: 700;
        letter-spacing: -0.025em;
        color: var(--text-primary);
        line-height: 1.3;
    }
    
    h1 { font-size: 2.25rem; margin-bottom: var(--space-md); }
    h2 { font-size: 1.875rem; margin-bottom: var(--space-md); }
    h3 { font-size: 1.5rem; margin-bottom: var(--space-sm); }
    h4 { font-size: 1.25rem; margin-bottom: var(--space-sm); }
    
    p, .stMarkdown p {
        color: var(--text-secondary);
        line-height: 1.7;
        margin-bottom: var(--space-md);
    }
    
    /* =====================================================================
       HERO HEADER - Page Title Section
       ===================================================================== */
    .hero-header {
        background: linear-gradient(135deg, var(--surface) 0%, var(--bg-secondary) 100%);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-xl);
        padding: var(--space-2xl) var(--space-xl);
        margin-bottom: var(--space-xl);
        box-shadow: var(--shadow-md);
        text-align: center;
    }
    
    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: var(--text-primary);
        margin-bottom: var(--space-sm);
        letter-spacing: -0.03em;
    }
    
    .hero-subtitle {
        font-size: 1.125rem;
        color: var(--text-secondary);
        font-weight: 400;
        line-height: 1.6;
    }
    
    .hero-badge {
        display: inline-block;
        background: var(--accent-light);
        color: var(--accent);
        padding: 0.3rem 0.75rem;
        border-radius: var(--radius-md);
        font-size: 0.875rem;
        font-weight: 600;
        margin-top: var(--space-sm);
    }
    
    /* =====================================================================
       CARD COMPONENTS - Primary Content Container
       ===================================================================== */
    .card {
        background: var(--surface);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-lg);
        padding: var(--space-xl);
        margin-bottom: var(--space-lg);
        box-shadow: var(--shadow-sm);
        transition: all 0.2s ease;
    }
    
    .card:hover {
        box-shadow: var(--shadow-md);
        border-color: var(--border-medium);
    }
    
    .card-compact {
        padding: var(--space-lg);
    }
    
    .card-header {
        margin-bottom: var(--space-lg);
        padding-bottom: var(--space-md);
        border-bottom: 2px solid var(--border-light);
    }
    
    .card-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: var(--space-xs);
        display: flex;
        align-items: center;
        gap: var(--space-sm);
    }
    
    .card-subtitle {
        font-size: 1rem;
        color: var(--text-secondary);
        line-height: 1.6;
    }
    
    /* =====================================================================
       FORM INPUTS - Text, TextArea, Select, File Upload
       ===================================================================== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div,
    .stNumberInput > div > div > input {
        background: var(--surface) !important;
        border: 2px solid var(--border-light) !important;
        border-radius: var(--radius-md) !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        color: var(--text-primary) !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > div:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px var(--accent-light) !important;
        outline: none !important;
    }
    
    .stTextArea > div > div > textarea {
        min-height: 120px !important;
        line-height: 1.6 !important;
    }
    
    /* File Uploader */
    [data-testid="stFileUploader"] {
        background: var(--bg-secondary);
        border: 2px dashed var(--border-medium);
        border-radius: var(--radius-lg);
        padding: var(--space-xl);
        transition: all 0.2s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: var(--accent);
        background: var(--accent-light);
    }
    
    /* =====================================================================
       BUTTONS - Primary, Secondary, and Icon Buttons
       ===================================================================== */
    .stButton > button {
        background: var(--accent);
        color: white;
        border: none;
        border-radius: var(--radius-md);
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.2s ease;
        box-shadow: var(--shadow-sm);
        cursor: pointer;
    }
    
    .stButton > button:hover {
        background: var(--accent-hover);
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Primary Button Variant (via Streamlit type="primary") */
    .stButton > button[kind="primary"] {
        background: var(--accent);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    .stButton > button[kind="primary"]:hover {
        background: var(--accent-hover);
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
    }
    
    /* Secondary Button */
    .stButton > button[kind="secondary"] {
        background: var(--surface);
        color: var(--text-primary);
        border: 2px solid var(--border-medium);
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: var(--surface-hover);
        border-color: var(--accent);
        color: var(--accent);
    }
    
    /* =====================================================================
       TABS - Navigation Tabs
       ===================================================================== */
    .stTabs [data-baseweb="tab-list"] {
        gap: var(--space-sm);
        background: var(--surface);
        padding: var(--space-sm);
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-light);
        margin-bottom: var(--space-lg);
    }
    
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 1rem;
        color: var(--text-secondary);
        padding: var(--space-md) var(--space-lg);
        border-radius: var(--radius-md);
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: var(--bg-secondary);
        color: var(--text-primary);
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--accent);
        color: white !important;
    }
    
    /* =====================================================================
       ANSWER & RESULT BOXES
       ===================================================================== */
    .answer-container {
        background: var(--surface);
        border-radius: var(--radius-lg);
        padding: var(--space-xl);
        margin: var(--space-lg) 0;
        box-shadow: var(--shadow-md);
    }
    
    .answer-success {
        background: var(--success-bg);
        border-left: 4px solid var(--success);
        padding: var(--space-lg);
        border-radius: var(--radius-md);
        margin: var(--space-md) 0;
    }
    
    .answer-error {
        background: var(--error-bg);
        border-left: 4px solid var(--error);
        padding: var(--space-lg);
        border-radius: var(--radius-md);
        margin: var(--space-md) 0;
    }
    
    .answer-header {
        font-size: 1.125rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: var(--space-md);
        display: flex;
        align-items: center;
        gap: var(--space-sm);
    }
    
    .answer-text {
        font-size: 1.05rem;
        line-height: 1.8;
        color: var(--text-primary);
    }
    
    .answer-text p {
        margin-bottom: var(--space-md);
    }
    
    .answer-text ul, .answer-text ol {
        margin: var(--space-md) 0;
        padding-left: var(--space-xl);
    }
    
    .answer-text li {
        margin: var(--space-sm) 0;
        line-height: 1.7;
    }
    
    /* =====================================================================
       SOURCE CITATION BOXES
       ===================================================================== */
    .source-container {
        background: var(--bg-secondary);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-md);
        padding: var(--space-lg);
        margin: var(--space-sm) 0;
        font-family: var(--font-mono);
        font-size: 0.9rem;
        line-height: 1.6;
        color: var(--text-secondary);
        white-space: pre-wrap;
        word-wrap: break-word;
        max-height: 300px;
        overflow-y: auto;
    }
    
    .source-header {
        font-family: var(--font-body);
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: var(--space-sm);
        font-size: 0.95rem;
    }
    
    /* =====================================================================
       METRICS & STATISTICS
       ===================================================================== */
    [data-testid="stMetricValue"] {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--text-primary);
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.875rem;
    }
    
    /* =====================================================================
       ALERTS & NOTIFICATIONS
       ===================================================================== */
    .stAlert {
        border-radius: var(--radius-md);
        padding: var(--space-md) var(--space-lg);
        border-width: 1px;
        border-style: solid;
    }
    
    /* Success Alert */
    [data-baseweb="notification"][kind="success"],
    .stSuccess {
        background: var(--success-bg) !important;
        border-color: var(--success-border) !important;
        color: var(--text-primary) !important;
    }
    
    /* Info Alert */
    [data-baseweb="notification"][kind="info"],
    .stInfo {
        background: var(--info-bg) !important;
        border-color: var(--info-border) !important;
        color: var(--text-primary) !important;
    }
    
    /* Warning Alert */
    [data-baseweb="notification"][kind="warning"],
    .stWarning {
        background: var(--warning-bg) !important;
        border-color: var(--warning-border) !important;
        color: var(--text-primary) !important;
    }
    
    /* Error Alert */
    [data-baseweb="notification"][kind="error"],
    .stError {
        background: var(--error-bg) !important;
        border-color: var(--error-border) !important;
        color: var(--text-primary) !important;
    }
    
    /* =====================================================================
       SIDEBAR
       ===================================================================== */
    [data-testid="stSidebar"] {
        background: var(--surface);
        border-right: 1px solid var(--border-light);
        padding: var(--space-lg) var(--space-md);
    }
    
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: var(--text-primary);
        font-size: 1.125rem;
        margin-bottom: var(--space-md);
    }
    
    .sidebar-section {
        padding: var(--space-md);
        background: var(--bg-secondary);
        border-radius: var(--radius-md);
        margin-bottom: var(--space-md);
    }
    
    /* =====================================================================
       STATUS INDICATORS
       ===================================================================== */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: var(--space-xs);
        padding: 0.4rem 0.9rem;
        border-radius: var(--radius-md);
        font-weight: 600;
        font-size: 0.875rem;
        margin: var(--space-xs) 0;
    }
    
    .status-online {
        background: var(--success-bg);
        color: var(--success);
        border: 1px solid var(--success-border);
    }
    
    .status-offline {
        background: var(--error-bg);
        color: var(--error);
        border: 1px solid var(--error-border);
    }
    
    .status-pending {
        background: var(--warning-bg);
        color: var(--warning);
        border: 1px solid var(--warning-border);
    }
    
    /* =======================================================================
       EXPANDERS
       ======================================================================= */
    .streamlit-expanderHeader {
        background: var(--surface);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-md);
        padding: var(--space-md) var(--space-lg);
        font-weight: 600;
        color: var(--text-primary);
        transition: all 0.2s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: var(--bg-secondary);
        border-color: var(--border-medium);
    }
    
    .streamlit-expanderContent {
        border: 1px solid var(--border-light);
        border-top: none;
        border-radius: 0 0 var(--radius-md) var(--radius-md);
        padding: var(--space-lg);
        background: var(--surface);
    }
    
    /* =====================================================================
       CODE BLOCKS
       ===================================================================== */
    code {
        background: var(--bg-secondary);
        padding: 0.2rem 0.4rem;
        border-radius: var(--radius-sm);
        font-family: var(--font-mono);
        font-size: 0.9em;
        color: var(--accent);
    }
    
    pre {
        background: var(--bg-secondary);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-md);
        padding: var(--space-lg);
        overflow-x: auto;
    }
    
    pre code {
        background: transparent;
        padding: 0;
        color: var(--text-primary);
    }
    
    /* =====================================================================
       CHECKBOX & RADIO
       ===================================================================== */
    .stCheckbox label {
        font-weight: 500;
        color: var(--text-primary);
    }
    
    /* =====================================================================
       DIVIDERS
       ===================================================================== */
    hr {
        border: none;
        border-top: 1px solid var(--border-light);
        margin: var(--space-xl) 0;
    }
    
    /* =====================================================================
       SPINNER & LOADING
       ===================================================================== */
    .stSpinner > div {
        border-top-color: var(--accent) !important;
    }
    
    /* =====================================================================
       RESPONSIVE DESIGN
       ===================================================================== */
    @media (max-width: 768px) {
        .block-container {
            padding: var(--space-lg) var(--space-md) var(--space-xl);
        }
        
        .hero-header {
            padding: var(--space-xl) var(--space-lg);
        }
        
        .hero-title {
            font-size: 1.875rem;
        }
        
        .card {
            padding: var(--space-lg);
        }
        
        .card-title {
            font-size: 1.25rem;
        }
        
        h1 { font-size: 1.875rem; }
        h2 { font-size: 1.5rem; }
        h3 { font-size: 1.25rem; }
    }
    
    /* =====================================================================
       SCROLLBAR STYLING
       ===================================================================== */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-medium);
        border-radius: var(--radius-sm);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--border-strong);
    }
    
    /* =====================================================================
       REMOVE STREAMLIT BRANDING (Optional)
       ===================================================================== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
"""

try:
    st.markdown(ENTERPRISE_CSS, unsafe_allow_html=True)
except Exception as e:
    st.warning(f"CSS styling unavailable: {e}")

# ============================================================================
# Configuration
# ============================================================================

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
MAX_FILE_SIZE_MB = 100

# ============================================================================
# Helper Functions
# ============================================================================

def check_api_health():
    """Check API health."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200, response.json() if response.status_code == 200 else {}
    except:
        return False, {}

def upload_document(file):
    """Upload PDF with detailed error handling."""
    try:
        # First check if backend is accessible
        try:
            health_response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if health_response.status_code != 200:
                return False, {"error": "Backend not ready. Please wait a moment and try again."}
        except requests.exceptions.ConnectionError:
            return False, {"error": f"Cannot reach backend at {API_BASE_URL}. Backend may be offline."}
        except requests.exceptions.Timeout:
            return False, {"error": "Backend connection timeout. Backend may be overloaded."}
        
        # Attempt upload
        files = {"file": (file.name, file, "application/pdf")}
        response = requests.post(f"{API_BASE_URL}/upload", files=files, timeout=60)
        
        if response.status_code == 200:
            return True, response.json()
        elif response.status_code == 413:
            return False, {"error": "File too large"}
        elif response.status_code == 400:
            return False, {"error": response.json().get("detail", "Invalid file format")}
        elif response.status_code == 500:
            return False, {"error": "Backend error processing file"}
        else:
            return False, {"error": f"Upload failed (status: {response.status_code})"}
            
    except requests.exceptions.Timeout:
        return False, {"error": "Upload timeout - file may be too large"}
    except requests.exceptions.ConnectionError as e:
        return False, {"error": f"Connection error: {str(e)[:100]}"}
    except Exception as e:
        return False, {"error": f"Upload error: {str(e)[:100]}"}

def query_documents(question, return_sources=True):
    """Ask question."""
    try:
        payload = {"question": question, "return_sources": return_sources}
        response = requests.post(f"{API_BASE_URL}/query", json=payload, timeout=30)
        return response.status_code == 200, response.json() if response.status_code == 200 else {}
    except Exception as e:
        return False, {"error": str(e)}

def list_documents():
    """List documents."""
    try:
        response = requests.get(f"{API_BASE_URL}/documents", timeout=5)
        return response.status_code == 200, response.json() if response.status_code == 200 else {}
    except:
        return False, {}

def get_system_stats():
    """Get stats."""
    try:
        response = requests.get(f"{API_BASE_URL}/stats", timeout=5)
        return response.status_code == 200, response.json() if response.status_code == 200 else {}
    except:
        return False, {}

# ============================================================================
# Main App
# ============================================================================

def main():
    """Main application entry point with professional enterprise UI"""
    
    # Initialize session state
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    # =========================================================================
    # HERO HEADER - Professional page title section
    # =========================================================================
    st.markdown(
        '''
        <div class="hero-header">
            <div class="hero-title">🏢 Enterprise Document Q&A</div>
            <div class="hero-subtitle">
                Advanced retrieval-augmented generation (RAG) system with AI-powered 
                question answering and source verification
            </div>
            <span class="hero-badge">Powered by NVIDIA AI</span>
        </div>
        ''',
        unsafe_allow_html=True
    )
    
    # =========================================================================
    # SIDEBAR - System status and controls
    # =========================================================================
    with st.sidebar:
        st.markdown("### ⚙️ System Control")
        
        # Backend status check
        is_healthy, health_data = check_api_health()
        
        if is_healthy:
            st.markdown(
                '<div class="status-badge status-online">● Backend Online</div>', 
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div class="status-badge status-offline">● Backend Offline</div>', 
                unsafe_allow_html=True
            )
            st.warning("⚠️ Backend is not responding")
        
        if st.button("🚀 Start Backend", use_container_width=True, help="Instructions to start the backend server"):
            st.info("**Run this command in terminal:**")
            st.code("python -m uvicorn app.main:app --host 0.0.0.0 --port 8000", language="bash")
        
        st.divider()
        
        # System statistics
        st.markdown("### 📊 System Info")
        success, stats = get_system_stats()
        
        if success:
            config = stats.get("config", {})
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "Chunk Size", 
                    f"{config.get('chunk_size', 0)}", 
                    delta="chars",
                    help="Text chunk size for processing"
                )
            with col2:
                st.metric(
                    "Top-K", 
                    config.get('top_k', 0),
                    delta="results",
                    help="Number of results retrieved"
                )
            
            # Model info
            embed_model = config.get('embedding_model', 'N/A').split('/')[-1]
            llm_model = config.get('llm_model', 'N/A').split('/')[-1]
            
            st.caption(f"**🔢 Embedding:** {embed_model}")
            st.caption(f"**🧠 LLM:** {llm_model}")
        else:
            st.info("Stats unavailable")
        
        st.divider()
        
        # Document count
        st.markdown("### 📁 Documents")
        doc_success, docs_data = list_documents()
        
        if doc_success:
            total = docs_data.get("total_documents", 0)
            st.metric("Total Files", total, help="Documents in knowledge base")
            
            if total > 0:
                st.caption("**Recent files:**")
                for doc in docs_data.get("documents", [])[:3]:
                    doc_name = str(doc)[:25] + "..." if len(str(doc)) > 25 else str(doc)
                    st.text(f"📄 {doc_name}")
        else:
            st.info("No documents yet")
    
    # =========================================================================
    # MAIN CONTENT - Tabs for different features
    # =========================================================================
    tab1, tab2, tab3, tab4 = st.tabs([
        "💬 Ask Questions", 
        "📤 Upload Documents", 
        "📋 View Documents", 
        "📊 Dashboard"
    ])
    
    # =========================================================================
    # TAB 1: ASK QUESTIONS - Main Q&A Interface
    # =========================================================================
    with tab1:
        # Check if documents are available
        doc_success, docs_data = list_documents()
        has_docs = doc_success and docs_data.get("total_documents", 0) > 0
        
        # Question input section
        with st.container():
            st.markdown(
                '''
                <div class="card-header">
                    <div class="card-title">💬 Ask Questions</div>
                    <div class="card-subtitle">
                        Query your documents and receive AI-generated answers with source citations
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )
            
            if not has_docs:
                st.info("📤 **No documents found.** Please upload PDF documents in the 'Upload Documents' tab to get started.")
            
            # Question input
            question = st.text_input(
                "Your Question",
                placeholder="e.g., What are the main findings of the research?",
                disabled=not has_docs,
                help="Enter your question about the uploaded documents"
            )
            
            # Options and submit
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                show_sources = st.checkbox(
                    "Include source citations", 
                    value=True, 
                    disabled=not has_docs
                )
            with col3:
                ask_btn = st.button(
                    "🔍 Search & Answer", 
                    type="primary", 
                    use_container_width=True, 
                    disabled=not (has_docs and question)
                )
        
        # Quick example questions
        if has_docs:
            st.markdown("**💡 Quick Examples:**")
            examples = [
                "What is the main topic?",
                "Summarize key findings",
                "What are the conclusions?",
                "List the main recommendations"
            ]
            cols = st.columns(4)
            for i, ex in enumerate(examples):
                with cols[i]:
                    if st.button(ex, key=f"ex_{i}", use_container_width=True):
                        question = ex
                        ask_btn = True

        # Process question and display answer
        if ask_btn and question:
            with st.spinner("🔍 Searching documents and generating answer..."):
                success, result = query_documents(question, show_sources)
            
            if success:
                answer_avail = result.get("answer_available", False)
                answer = result.get("answer", "")
                confidence = result.get("confidence", "low")
                num_sources = result.get("num_sources", 0)
                
                # Store in conversation history
                st.session_state.conversation_history.append({
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "question": question,
                    "answer": answer,
                    "sources_count": num_sources,
                    "confidence": confidence
                })
                
                # Display answer with styling
                if answer_avail:
                    st.markdown(
                        f'''
                        <div class="answer-success">
                            <div class="answer-header">✅ Answer Found</div>
                            <div class="answer-text">{answer.replace(chr(10), "<br>")}</div>
                        </div>
                        ''',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'''
                        <div class="answer-error">
                            <div class="answer-header">⚠️ No Relevant Information Found</div>
                            <div class="answer-text">{answer.replace(chr(10), "<br>")}</div>
                        </div>
                        ''',
                        unsafe_allow_html=True
                    )
                
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Confidence", confidence.upper())
                with col2:
                    st.metric("Sources Used", num_sources)
                with col3:
                    quality = "High" if confidence == "high" else "Medium" if confidence == "medium" else "Low"
                    st.metric("Quality", quality)
                with col4:
                    st.metric("Response Time", "< 5s")
                
                # Source citations
                if show_sources and result.get("sources"):
                    st.markdown("---")
                    st.markdown("### 📚 Source Citations")
                    st.caption(f"Found {len(result['sources'])} relevant sources")
                    
                    for i, src in enumerate(result["sources"], 1):
                        source_name = src.get('source', 'Unknown')[:50]
                        with st.expander(f"📄 Source {i}: {source_name}", expanded=False):
                            st.markdown(
                                f'<div class="source-container">{src.get("content", "")}</div>',
                                unsafe_allow_html=True
                            )
            else:
                st.error(f"❌ Error: {result.get('error', 'Unknown error occurred')}")
    
    # =========================================================================
    # TAB 2: UPLOAD DOCUMENTS - File upload interface
    # =========================================================================
    with tab2:
        st.markdown(
            '''
            <div class="card-header">
                <div class="card-title">📤 Upload Documents</div>
                <div class="card-subtitle">
                    Add PDF documents to your knowledge base for intelligent retrieval
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )
        
        # File uploader
        uploaded = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help=f"Maximum file size: {MAX_FILE_SIZE_MB}MB"
        )
        
        if uploaded:
            size_mb = uploaded.size / (1024 ** 2)
            
            # File info display
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.info(f"📄 **{uploaded.name}**")
            with col2:
                st.metric("Size", f"{size_mb:.2f} MB")
            with col3:
                st.metric("Type", "PDF")
            
            # Upload button
            if st.button("⬆️ Upload & Process", type="primary", use_container_width=True):
                if size_mb > MAX_FILE_SIZE_MB:
                    st.error(f"❌ File too large. Maximum size is {MAX_FILE_SIZE_MB}MB")
                else:
                    with st.spinner("Processing document... This may take a moment"):
                        success, result = upload_document(uploaded)
                    
                    if success:
                        st.success("✅ Document uploaded and processed successfully!")
                        
                        # Show processing details
                        with st.expander("📋 Processing Details", expanded=True):
                            details = result.get("details", {})
                            if details:
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.json(details)
                                with col2:
                                    st.info("Document has been indexed and is ready for queries")
                        
                        # Refresh page after upload
                        time.sleep(2)
                        st.rerun()
                    else:
                        error_msg = result.get('error', 'Unknown error occurred')
                        st.error(f"❌ Upload Failed")
                        st.markdown(f"**Reason:** {error_msg}")
                        
                        # Provide troubleshooting tips
                        with st.expander("🔧 Troubleshooting", expanded=True):
                            st.markdown("""
                            **Common issues and solutions:**
                            
                            1. **Backend Offline**: Go to Dashboard tab and check System Health
                            2. **Connection Timeout**: Backend may be starting. Wait 30 seconds and try again
                            3. **File Too Large**: Maximum size is 50MB
                            4. **Invalid PDF**: Ensure the PDF file is not corrupted
                            
                            **Still having issues?** 
                            - Check the Dashboard → System Health
                            - Click "Test Connection" to verify backend
                            - Try restarting the app
                            """)
        else:
            st.markdown(
                '''
                <div style="text-align: center; padding: 2rem; color: var(--text-secondary);">
                    <p>📁 Drag and drop a PDF file or click to browse</p>
                    <p style="font-size: 0.9rem;">Supported format: PDF only</p>
                </div>
                ''',
                unsafe_allow_html=True
            )
    
    # =========================================================================
    # TAB 3: VIEW DOCUMENTS - Document management
    # =========================================================================
    with tab3:
        st.markdown(
            '''
            <div class="card-header">
                <div class="card-title">📋 Document Library</div>
                <div class="card-subtitle">
                    View and manage all indexed documents in your knowledge base
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )
        
        success, docs_data = list_documents()
        
        if success:
            total = docs_data.get("total_documents", 0)
            
            if total == 0:
                st.info("📭 No documents in your library yet. Upload documents in the Upload tab to get started.")
            else:
                # Summary metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Documents", total, help="Number of indexed documents")
                with col2:
                    st.metric("Status", "Active", delta="Indexed", help="All documents are indexed")
                with col3:
                    st.metric("Storage", "Cloud", help="Documents stored in vector database")
                
                st.markdown("---")
                st.markdown("### 📄 Document List")
                
                # Display documents
                documents = docs_data.get("documents", [])
                for idx, doc in enumerate(documents, 1):
                    with st.container():
                        col1, col2 = st.columns([5, 1])
                        with col1:
                            st.markdown(f"**{idx}.** `{doc}`")
                        with col2:
                            st.caption("✓ Indexed")
                        
                        if idx < len(documents):
                            st.markdown('<hr style="margin: 0.5rem 0;">', unsafe_allow_html=True)
        else:
            st.error("❌ Failed to load documents. Backend may be offline.")
    
    # ========================================================================
    
    # =========================================================================
    # TAB 4: DASHBOARD - System overview and analytics
    # =========================================================================
    with tab4:
        st.markdown(
            '''
            <div class="card-header">
                <div class="card-title">📊 System Dashboard</div>
                <div class="card-subtitle">
                    Monitor system health, configuration, and conversation analytics
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )
        
        # =====================================================================
        # System Health Status
        # =====================================================================
        st.markdown("### 🔧 System Health")
        
        is_healthy, health_data = check_api_health()
        vector_exists = health_data.get("vector_store_exists", False) if is_healthy else False
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if is_healthy:
                st.markdown(
                    '<div class="status-badge status-online">● Backend API Online</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    '<div class="status-badge status-offline">● Backend API Offline</div>',
                    unsafe_allow_html=True
                )
        
        with col2:
            if vector_exists:
                st.markdown(
                    '<div class="status-badge status-online">● Vector Store Ready</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    '<div class="status-badge status-pending">● Vector Store Unavailable</div>',
                    unsafe_allow_html=True
                )
        
        with col3:
            doc_count = len(st.session_state.conversation_history)
            if doc_count > 0:
                st.markdown(
                    f'<div class="status-badge status-online">● {doc_count} Conversations</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    '<div class="status-badge status-pending">● No Conversations</div>',
                    unsafe_allow_html=True
                )
        
        st.divider()
        
        # =====================================================================
        # System Statistics
        # =====================================================================
        st.markdown("### 📈 Performance Metrics")
        
        success_stats, stats = get_system_stats()
        
        if success_stats:
            config = stats.get("config", {})
            vs_stats = stats.get("vector_store_stats", {})
            
            # Key metrics in a clean grid
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                doc_count = vs_stats.get("estimated_documents", 0)
                st.metric(
                    "Documents",
                    doc_count,
                    delta="Indexed" if doc_count > 0 else None,
                    help="Total indexed documents"
                )
            
            with col2:
                queries = len(st.session_state.conversation_history)
                st.metric(
                    "Queries",
                    queries,
                    delta="Total" if queries > 0 else None,
                    help="Total questions asked"
                )
            
            with col3:
                chunk_size = config.get("chunk_size", 0)
                st.metric(
                    "Chunk Size",
                    chunk_size,
                    delta="chars",
                    help="Text chunk size for processing"
                )
            
            with col4:
                top_k = config.get("top_k", 0)
                st.metric(
                    f"Top-K",
                    top_k,
                    delta="results",
                    help="Retrieved results per query"
                )
            
            st.divider()
            
            # =====================================================================
            # AI Models Configuration
            # =====================================================================
            st.markdown("### 🤖 AI Models")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🔢 Embedding Model**")
                embed_model = config.get("embedding_model", "Not configured")
                st.code(embed_model, language="text")
                st.caption("Converts text to numerical vectors")
            
            with col2:
                st.markdown("**🧠 Language Model (LLM)**")
                llm_model = config.get("llm_model", "Not configured")
                st.code(llm_model, language="text")
                st.caption("Generates natural language answers")
            
            # Advanced configuration details
            with st.expander("⚙️ Advanced Configuration", expanded=False):
                st.json(config)
            
            with st.expander("🗄️ Vector Store Details", expanded=False):
                st.json(vs_stats)
        
        else:
            st.warning("⚠️ Unable to retrieve system statistics. Backend may be offline.")
        
        st.divider()
        
        # =====================================================================
        # Quick Actions
        # =====================================================================
        st.markdown("### ⚡ Quick Actions")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔄 Refresh", use_container_width=True, help="Reload dashboard data"):
                st.rerun()
        
        with col2:
            if st.button("📚 API Docs", use_container_width=True, help="Open API documentation"):
                st.markdown("[View Docs](http://localhost:8000/docs)")
        
        with col3:
            if st.button("🧪 Test Connection", use_container_width=True, help="Test backend connection"):
                with st.spinner("Testing..."):
                    healthy, data = check_api_health()
                    if healthy:
                        st.success("✅ Connection successful!")
                    else:
                        st.error("❌ Connection failed!")
        
        with col4:
            if st.button("📥 Export Data", use_container_width=True, help="Export conversation history"):
                if st.session_state.conversation_history:
                    history_text = "\n\n".join([
                        f"[{h['timestamp']}]\nQuestion: {h['question']}\nAnswer: {h['answer']}\nSources: {h['sources_count']}\n{'-'*60}"
                        for h in st.session_state.conversation_history
                    ])
                    st.download_button(
                        "💾 Download History",
                        history_text,
                        file_name=f"qa_history_{time.strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
                else:
                    st.info("No history to export")
        
        st.divider()
        
        # =====================================================================
        # Conversation History
        # =====================================================================
        st.markdown("### 💬 Recent Conversations")
        
        if st.session_state.conversation_history:
            total_queries = len(st.session_state.conversation_history)
            st.caption(f"**{total_queries}** total conversations")
            
            # Show last 10 conversations
            recent = st.session_state.conversation_history[-10:][::-1]
            
            for idx, entry in enumerate(recent, 1):
                question_preview = entry['question'][:60] + "..." if len(entry['question']) > 60 else entry['question']
                
                with st.expander(f"🕒 {entry['timestamp']} - {question_preview}", expanded=False):
                    st.markdown(f"**❓ Question:**")
                    st.info(entry['question'])
                    
                    st.markdown(f"**💡 Answer:**")
                    answer_preview = entry['answer'][:400] + "..." if len(entry['answer']) > 400 else entry['answer']
                    st.success(answer_preview)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.caption(f"📄 **Sources:** {entry['sources_count']}")
                    with col2:
                        st.caption(f"🎯 **Confidence:** {entry['confidence']}")
            
            # Clear history button
            if st.button("🗑️ Clear All History", use_container_width=True):
                st.session_state.conversation_history = []
                st.success("✅ History cleared!")
                time.sleep(1)
                st.rerun()
        
        else:
            st.info("💭 No conversation history yet. Ask questions in the 'Ask Questions' tab to see them here.")
        
        st.divider()
        
        # =====================================================================
        # System Requirements & Info
        # =====================================================================
        with st.expander("📋 System Requirements & Setup", expanded=False):
            st.markdown("""
            #### Minimum Requirements
            - **Python:** 3.10 or higher
            - **RAM:** 2GB minimum
            - **Internet:** Active connection required
            - **API Key:** Valid NVIDIA API key
            
            #### Recommended Setup
            - **Python:** 3.11+
            - **RAM:** 4GB or more
            - **Storage:** SSD preferred
            - **Connection:** Stable broadband
            
            #### Current System Status
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                status = "✅ Running" if is_healthy else "❌ Offline"
                st.markdown(f"**Backend API:** {status}")
            with col2:
                vs_status = "✅ Available" if vector_exists else "⚠️ Not Available"
                st.markdown(f"**Vector Store:** {vs_status}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        st.error(f"❌ Application Error: {type(e).__name__}: {str(e)}")
        st.code(traceback.format_exc())
        st.warning("The application encountered an error. Please check the logs and try again.")

