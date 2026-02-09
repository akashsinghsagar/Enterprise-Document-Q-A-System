#!/usr/bin/env python
"""Quick test of the RAG system."""

import requests
import json

def test_system():
    """Test end-to-end RAG pipeline."""
    print("\n" + "="*60)
    print("TESTING ENTERPRISE DOCUMENT Q&A SYSTEM")
    print("="*60)
    
    # Test 1: Health check
    print("\n1️⃣  Testing Backend Health...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Backend: {data.get('status').upper()}")
            print(f"   ✅ Message: {data.get('message')}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False
    
    # Test 2: System stats
    print("\n2️⃣  Checking Configuration...")
    try:
        response = requests.get("http://localhost:8000/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            config = stats.get("config", {})
            print(f"   ✅ Embedding Model: {config.get('embedding_model')}")
            print(f"   ✅ LLM Model: {config.get('llm_model')}")
            print(f"   ✅ Chunk Size: {config.get('chunk_size')}")
            print(f"   ✅ Top-K: {config.get('top_k')}")
    except Exception as e:
        print(f"   ❌ Stats error: {e}")
    
    # Test 3: List documents
    print("\n3️⃣  Checking Uploaded Documents...")
    try:
        response = requests.get("http://localhost:8000/documents", timeout=5)
        if response.status_code == 200:
            docs = response.json()
            total = docs.get("total_documents", 0)
            print(f"   ✅ Total Documents: {total}")
            if total > 0:
                for doc in docs.get("documents", []):
                    print(f"      • {doc}")
            else:
                print("   ⚠️  No documents uploaded. Upload a PDF first!")
                return False
    except Exception as e:
        print(f"   ❌ Documents error: {e}")
        return False
    
    # Test 4: Query
    print("\n4️⃣  Testing Question Answering...")
    try:
        payload = {
            "question": "What is the main topic of the document?",
            "return_sources": True
        }
        response = requests.post(
            "http://localhost:8000/query",
            json=payload,
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Query successful")
            print(f"      Question: {result.get('question')}")
            print(f"      Answer available: {result.get('answer_available')}")
            print(f"      Confidence: {result.get('confidence')}")
            print(f"      Sources: {result.get('num_sources')}")
            answer = result.get('answer', '')[:150]
            print(f"      Answer preview: {answer}...")
        else:
            print(f"   ❌ Query failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Query error: {e}")
    
    print("\n" + "="*60)
    print("✅ SYSTEM TEST COMPLETE")
    print("="*60)
    print("\n🌐 Access the UI at: http://localhost:8501")
    print("📚 API Docs at: http://localhost:8000/docs")
    print("\n")
    return True

if __name__ == "__main__":
    test_system()
