# Heroku Procfile
web: sh -c "uvicorn app.main:app --host 0.0.0.0 --port $PORT & streamlit run frontend/ui.py --server.port 8501 --server.address 0.0.0.0"
