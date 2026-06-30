# Multi-stage build for NEXUS AI Agent

# Stage 1: Backend
FROM python:3.11-slim as backend

WORKDIR /app/backend

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY nexus-backend-main.py main.py
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Stage 2: Frontend
FROM python:3.11-slim as frontend

WORKDIR /app/frontend

RUN pip install streamlit requests pandas plotly

COPY nexus-frontend-streamlit.py app.py

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
