FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (excluding development artifacts)
COPY main.py .
COPY data_manager.py .
COPY file_watcher.py .
COPY models.py .
COPY service_runner.py .
COPY icloud_service.py .
COPY sync_manager.py .
COPY config/ ./config/
COPY static/ ./static/

# Create necessary directories
RUN mkdir -p /app/data/test-cases /app/data/outputs /app/data/uploads

# Expose port 7000 (updated from 8000 to avoid Coolify conflict)
EXPOSE 7000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7000/api/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7000"]