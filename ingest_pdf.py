import requests
import os

pdf_dir = "./data/raw_docs"
api_url = "http://localhost:8000/upload"

for pdf_file in os.listdir(pdf_dir):
    if pdf_file.endswith('.pdf'):
        pdf_path = os.path.join(pdf_dir, pdf_file)
        print(f"Ingesting: {pdf_file}")
        
        with open(pdf_path, 'rb') as f:
            files = {'file': (pdf_file, f, 'application/pdf')}
            try:
                response = requests.post(api_url, files=files, timeout=60)
                print(f"Status: {response.status_code}")
                print(f"Response: {response.json()}")
                print("-" * 50)
            except Exception as e:
                print(f"Error: {e}")
