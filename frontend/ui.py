"""
Professional Streamlit UI for Enterprise Document Q&A System

Modern, responsive interface with professional CSS styling for:
- Document upload
- Question answering
- Source visualization
- System status monitoring
"""

import os
import sys
import time
from pathlib import Path

import streamlit as st
import requests

# ============================================================================
# Page Configuration
# ============================================================================

try:
    st.set_page_config(
        page_title="Document Q&A System",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
except Exception as e:
    # Config already set or error occurred
    pass

# ============================================================================
# Custom CSS & Styling
# ============================================================================

CUSTOM_CSS = """
<style>
    :root {
        --bg: #f5f7fb;
        --surface: #ffffff;
        --surface-muted: #f0f3f9;
        --border: #e2e8f0;
        --text-primary: #0f172a;
        --text-secondary: #475569;
        --accent: #2563eb;
        --accent-strong: #1d4ed8;
        --success: #16a34a;
        --danger: #dc2626;
        --warning: #f59e0b;
        --shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
    }

    /* App background and container width */
    .stApp {
        background: var(--bg);
        color: var(--text-primary);
    }

    .stMain {
        background: var(--bg) !important;
    }

    section.stMain {
        background: var(--bg) !important;
    }

    .block-container {
        max-width: 1100px;
        padding: 2.5rem 2rem 3rem;
    }

    /* Typography and base text */
    .stMarkdown,
    .stMarkdown p,
    .stMarkdown li,
    .stMarkdown span,
    .stMarkdown h1,
    .stMarkdown h2,
    .stMarkdown h3,
    .stMarkdown h4,
    .stMarkdown h5,
    .stMarkdown h6,
    .stMarkdown a {
        color: var(--text-primary) !important;
    }

    h1, h2, h3, h4 {
        letter-spacing: -0.02em;
    }

    .stMarkdown p {
        line-height: 1.75;
        color: var(--text-secondary) !important;
    }

    /* Header */
    .page-header {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        box-shadow: var(--shadow);
    }

    .page-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.35rem;
        color: var(--text-primary);
    }

    .page-subtitle {
        font-size: 1.05rem;
        color: var(--text-secondary);
    }

    /* Card layout */
    .card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.5rem 1.75rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--shadow);
    }

    .card-title {
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
        color: var(--text-primary);
    }

    .card-subtitle {
        color: var(--text-secondary);
        margin-bottom: 1.25rem;
        font-size: 0.98rem;
    }

    /* Inputs and controls */
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox select,
    .stFileUploader input {
        border-radius: 10px !important;
        border: 1px solid var(--border) !important;
        padding: 0.65rem 0.9rem !important;
        font-size: 0.98rem !important;
        background: var(--surface) !important;
        color: var(--text-primary) !important;
    }

    .stTextInput input:focus,
    .stTextArea textarea:focus,
    .stSelectbox select:focus,
    .stFileUploader input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
    }

    /* Buttons */
    .stButton > button {
        background: var(--accent);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 1.4rem;
        font-weight: 600;
        transition: all 0.2s ease;
        box-shadow: 0 6px 18px rgba(37, 99, 235, 0.2);
    }

    .stButton > button:hover {
        background: var(--accent-strong);
        transform: translateY(-1px);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        color: var(--text-secondary);
        padding: 0.5rem 1rem;
    }

    .stTabs [aria-selected="true"] {
        color: var(--text-primary);
        border-bottom: 2px solid var(--accent);
    }

    /* Answer containers */
    .answer-box-success,
    .answer-box-error {
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin: 1.25rem 0;
        box-shadow: var(--shadow);
    }

    .answer-box-success {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
    }

    .answer-box-error {
        background: #fff1f2;
        border: 1px solid #fecdd3;
    }

    .answer-text {
        font-size: 1rem;
        line-height: 1.7;
        color: var(--text-primary);
    }

    .answer-text ul {
        margin: 0.75rem 0;
        padding-left: 1.5rem;
    }

    .answer-text li {
        margin: 0.35rem 0;
    }

    /* Source box */
    .source-box {
        background: var(--surface-muted);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 1rem;
        font-family: "Courier New", monospace;
        font-size: 0.9rem;
        white-space: pre-wrap;
        word-wrap: break-word;
    }

    /* Status indicators */
    .status-ok {
        color: var(--success);
        font-weight: 600;
    }

    .status-error {
        color: var(--danger);
        font-weight: 600;
    }

    /* Responsive layout */
    @media (max-width: 768px) {
        .block-container {
            padding: 2rem 1.25rem 2.5rem;
        }

        .page-header {
            padding: 1.5rem;
        }

        .card {
            padding: 1.25rem;
        }
    }
</style>
"""

try:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
except Exception as e:
    st.warning(f"CSS injection failed: {e}. Using default styles.")

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
    """Upload PDF."""
    try:
        files = {"file": (file.name, file, "application/pdf")}
        response = requests.post(f"{API_BASE_URL}/upload", files=files, timeout=60)
        return response.status_code == 200, response.json() if response.status_code == 200 else {"error": "Upload failed"}
    except Exception as e:
        return False, {"error": str(e)}

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
    # Initialize session state for history
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    # Header
    st.markdown(
        '<div class="page-header">'
        '<div class="page-title">Document Q&A System</div>'
        '<div class="page-subtitle">Retrieval-Augmented Generation with source-backed answers</div>'
        '</div>',
        unsafe_allow_html=True
    )
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ System Status")
        
        is_healthy, health_data = check_api_health()
        if is_healthy:
            st.markdown('<div class="status-ok">✓ Backend Online</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-error">✗ Backend Offline</div>', unsafe_allow_html=True)
            st.error("Backend unavailable. Start with: `python -m uvicorn app.main:app --port 8000`")
        
        if st.button("▶ Start Backend", use_container_width=True):
            st.info("Run this from the project root:")
            st.code("python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload", language="bash")
        
        st.markdown("---")
        
        st.header("📊 System Info")
        success, stats = get_system_stats()
        if success:
            config = stats.get("config", {})
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Chunk Size", f"{config.get('chunk_size', 'N/A')} ch")
            with col2:
                st.metric("Top-K", config.get('top_k', 'N/A'))
            
            st.caption(f"🤖 **Embedding**: {config.get('embedding_model', 'N/A').split('/')[-1]}")
            st.caption(f"🧠 **LLM**: {config.get('llm_model', 'N/A').split('/')[-1]}")
        
        st.markdown("---")
        st.header("📄 Documents")
        doc_success, docs_data = list_documents()
        if doc_success:
            total = docs_data.get("total_documents", 0)
            st.metric("Total", total)
            if total > 0:
                st.caption("**Files:**")
                for doc in docs_data.get("documents", [])[:5]:
                    doc_str = str(doc)[:30] if doc else "Unknown"
                    st.text(f"• {doc_str}")
    
    # Main Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Ask Questions", "📤 Upload Documents", "📋 View Documents", "📊 Dashboard"])
    
    # ========================================================================
    # Tab 1: Ask Questions
    # ========================================================================
    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Ask Questions</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-subtitle">Query your documents with precise, source-backed answers.</div>', unsafe_allow_html=True)
        
        doc_success, docs_data = list_documents()
        has_docs = doc_success and docs_data.get("total_documents", 0) > 0
        
        if not has_docs:
            st.info("📤 **No documents yet.** Upload a PDF in the 'Upload Documents' tab.")
        
        question = st.text_input(
            "Your Question:",
            placeholder="What is the main topic?",
            disabled=not has_docs
        )
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            show_sources = st.checkbox("Show sources", value=True, disabled=not has_docs)
        with col3:
            ask_btn = st.button("🔍 Ask", type="primary", use_container_width=True, disabled=not (has_docs and question))
        
        # Examples
        st.markdown("**Quick Examples:**")
        examples = ["What is the main topic?", "Summarize key findings", "What are conclusions?", "Who are authors?"]
        cols = st.columns(2)
        for i, ex in enumerate(examples):
            with cols[i % 2]:
                if st.button(ex, key=f"ex{i}", use_container_width=True):
                    question = ex
                    ask_btn = True
        
        st.markdown("</div>", unsafe_allow_html=True)

        # Process
        if ask_btn and question:
            with st.spinner("🔍 Generating answer..."):
                success, result = query_documents(question, show_sources)
            
            if success:
                answer_avail = result.get("answer_available", False)
                answer = result.get("answer", "")
                confidence = result.get("confidence", "low")
                num_sources = result.get("num_sources", 0)
                
                # Format answer with bullet points
                formatted_answer = answer
                if "•" in answer or "\n- " in answer:
                    # Convert bullet points to HTML list
                    lines = answer.split("\n")
                    formatted_lines = []
                    in_list = False
                    for line in lines:
                        line = line.strip()
                        if line.startswith("•") or line.startswith("-"):
                            if not in_list:
                                formatted_lines.append("<ul>")
                                in_list = True
                            item = line.lstrip("•-").strip()
                            formatted_lines.append(f"<li>{item}</li>")
                        else:
                            if in_list:
                                formatted_lines.append("</ul>")
                                in_list = False
                            if line:
                                formatted_lines.append(f"<p>{line}</p>")
                    if in_list:
                        formatted_lines.append("</ul>")
                    formatted_answer = "".join(formatted_lines)
                else:
                    # Keep regular paragraph format
                    formatted_answer = answer.replace("\n", "<br>")
                
                # Store in conversation history
                st.session_state.conversation_history.append({
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "question": question,
                    "answer": answer,
                    "sources_count": num_sources,
                    "confidence": confidence
                })
                
                st.markdown('<div class="card">', unsafe_allow_html=True)

                if answer_avail:
                    st.markdown(
                        f'<div class="answer-box-success"><strong>✅ Answer Found</strong><div class="answer-text">{formatted_answer}</div></div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<div class="answer-box-error"><strong>⚠️ Not Found</strong><div class="answer-text">{formatted_answer}</div></div>',
                        unsafe_allow_html=True
                    )
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Confidence", confidence.upper())
                with col2:
                    st.metric("Sources", num_sources)
                with col3:
                    st.metric("Quality", "✓ High" if confidence == "high" else "○ Low")
                
                if show_sources and result.get("sources"):
                    st.markdown("### 📚 Source Documents")
                    for i, src in enumerate(result["sources"], 1):
                        with st.expander(f"📄 Source {i}: {src.get('source', 'Unknown')[:40]}"):
                            st.markdown(f'<div class="source-box">{src.get("content", "")}</div>', unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error(f"❌ {result.get('error', 'Error')}")
    
    # ========================================================================
    # Tab 2: Upload
    # ========================================================================
    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Upload Documents</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-subtitle">Add PDFs to your knowledge base for retrieval.</div>', unsafe_allow_html=True)
        
        uploaded = st.file_uploader("Choose PDF", type=['pdf'])
        
        if uploaded:
            size_mb = uploaded.size / (1024 ** 2)
            st.info(f"📄 **{uploaded.name}** • {size_mb:.2f} MB")
            
            if st.button("⬆️ Upload & Process", type="primary", use_container_width=True):
                if size_mb > MAX_FILE_SIZE_MB:
                    st.error(f"❌ Max {MAX_FILE_SIZE_MB} MB")
                else:
                    with st.spinner("Processing..."):
                        success, result = upload_document(uploaded)
                    
                    if success:
                        st.success("✅ Uploaded successfully!")
                        with st.expander("Details"):
                            st.json(result.get("details", {}))
                        st.info("Processing in background...")
                    else:
                        st.error(f"❌ {result.get('error', 'Error')}")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # ========================================================================
    # Tab 3: View
    # ========================================================================
    with tab3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Uploaded Documents</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-subtitle">Manage and verify your indexed files.</div>', unsafe_allow_html=True)
        
        success, docs_data = list_documents()
        if success:
            total = docs_data.get("total_documents", 0)
            if total == 0:
                st.info("No documents yet")
            else:
                st.success(f"✓ **{total}** documents in knowledge base")
                for doc in docs_data.get("documents", []):
                    st.text(f"📄 {doc}")
        else:
            st.error("Failed to load documents")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # ========================================================================
    # Tab 4: Dashboard
    # ========================================================================
    with tab4:
        st.header("📊 System Dashboard")
        
        # System Health
        st.subheader("🔧 System Health")
        is_healthy, health_data = check_api_health()
        
        col1, col2 = st.columns(2)
        with col1:
            if is_healthy:
                st.success("✅ Backend API: **Online**")
            else:
                st.error("❌ Backend API: **Offline**")
        
        with col2:
            vector_exists = health_data.get("vector_store_exists", False) if is_healthy else False
            if vector_exists:
                st.success("✅ Vector Store: **Available**")
            else:
                st.warning("⚠️ Vector Store: **Not Available**")
        
        st.markdown("---")
        
        # Statistics
        st.subheader("📈 System Statistics")
        success_stats, stats = get_system_stats()
        
        if success_stats:
            config = stats.get("config", {})
            vs_stats = stats.get("vector_store_stats", {})
            
            # Key Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                doc_count = vs_stats.get("estimated_documents", 0)
                st.metric(
                    label="📄 Documents",
                    value=doc_count,
                    delta="Indexed"
                )
            
            with col2:
                chunk_size = config.get("chunk_size", "N/A")
                st.metric(
                    label="📏 Chunk Size",
                    value=f"{chunk_size}",
                    delta="characters"
                )
            
            with col3:
                top_k = config.get("top_k", "N/A")
                st.metric(
                    label="🔍 Retrieval",
                    value=f"Top-{top_k}",
                    delta="results"
                )
            
            with col4:
                overlap = config.get("chunk_overlap", "N/A")
                st.metric(
                    label="🔄 Overlap",
                    value=f"{overlap}",
                    delta="chars"
                )
            
            st.markdown("---")
            
            # Model Information
            st.subheader("🤖 AI Models")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Embedding Model**")
                embed_model = config.get("embedding_model", "N/A")
                st.code(embed_model, language="text")
                st.caption("Used for converting text to vectors")
            
            with col2:
                st.markdown("**Language Model (LLM)**")
                llm_model = config.get("llm_model", "N/A")
                st.code(llm_model, language="text")
                st.caption("Used for generating answers")
            
            st.markdown("---")
            
            # Configuration Details
            with st.expander("⚙️ Advanced Configuration", expanded=False):
                st.json(config)
            
            # Vector Store Details
            with st.expander("🗄️ Vector Store Information", expanded=False):
                st.json(vs_stats)
        
        else:
            st.warning("Unable to retrieve system statistics")
        
        st.markdown("---")
        
        # Quick Actions
        st.subheader("⚡ Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Refresh Dashboard", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("📚 View API Docs", use_container_width=True):
                st.markdown("[Open API Documentation](http://localhost:8000/docs)", unsafe_allow_html=True)
        
        with col3:
            if st.button("🧪 Test Health", use_container_width=True):
                with st.spinner("Testing connection..."):
                    healthy, data = check_api_health()
                    if healthy:
                        st.success("Connection successful!")
                        st.json(data)
                    else:
                        st.error("Connection failed!")
        
        st.markdown("---")
        
        # Conversation History Section
        st.subheader("💬 Conversation History")
        
        if st.session_state.conversation_history:
            total_queries = len(st.session_state.conversation_history)
            st.info(f"📊 **Total Queries:** {total_queries}")
            
            # Show recent 10 conversations
            recent_history = st.session_state.conversation_history[-10:][::-1]  # Last 10, reversed
            
            for idx, entry in enumerate(recent_history, 1):
                with st.expander(f"🕒 {entry['timestamp']} - {entry['question'][:50]}...", expanded=False):
                    st.markdown(f"**Question:**")
                    st.info(entry['question'])
                    
                    st.markdown(f"**Answer:**")
                    st.success(entry['answer'][:300] + "..." if len(entry['answer']) > 300 else entry['answer'])
                    
                    st.caption(f"📄 Sources used: {entry['sources_count']}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 Export History", use_container_width=True):
                    history_text = "\n\n".join([
                        f"[{h['timestamp']}]\nQ: {h['question']}\nA: {h['answer']}\n---"
                        for h in st.session_state.conversation_history
                    ])
                    st.download_button(
                        label="💾 Download as TXT",
                        data=history_text,
                        file_name=f"conversation_history_{time.strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
            
            with col2:
                if st.button("🗑️ Clear History", use_container_width=True):
                    st.session_state.conversation_history = []
                    st.success("History cleared!")
                    st.rerun()
        else:
            st.info("📭 No conversation history yet. Ask a question to get started!")
        
        st.markdown("---")
        
        # System Requirements
        with st.expander("📋 System Requirements", expanded=False):
            st.markdown("""
            **Minimum Requirements:**
            - Python 3.10+
            - 2GB RAM
            - Active internet connection (for NVIDIA API)
            - Valid NVIDIA API Key
            
            **Recommended:**
            - Python 3.11
            - 4GB+ RAM
            - SSD storage
            - Stable internet connection
            
            **Current Status:**
            - Backend: {}
            - Vector Store: {}
            """.format(
                "✅ Running" if is_healthy else "❌ Offline",
                "✅ Available" if vector_exists else "⚠️ Not Available"
            ))

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        st.error(f"❌ Application Error: {type(e).__name__}: {str(e)}")
        st.code(traceback.format_exc())
        st.warning("The application encountered an error during startup. Please check the configuration and try again.")
