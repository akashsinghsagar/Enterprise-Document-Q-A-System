"""
Streamlit test app to verify deployment
"""
import streamlit as st

st.set_page_config(page_title="Test", page_icon="✅")

st.title("✅ Steamlit Cloud Test")
st.success("If you see this, Streamlit is working correctly!")
st.info("Deployment successful - basic test passed")

# Test imports
try:
    import requests
    st.success("✅ requests module imported")
except Exception as e:
    st.error(f"❌ requests import failed: {e}")

try:
    import os
    api_url = os.getenv("API_BASE_URL", "not set")
    st.info(f"API_BASE_URL environment variable: {api_url}")
except Exception as e:
    st.error(f"❌ os.getenv failed: {e}")

st.write("Python version info:")
import sys
st.code(sys.version)
