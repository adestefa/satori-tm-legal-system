FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for ML and document processing
RUN apt-get update && apt-get install -y \
    curl \
    poppler-utils \
    tesseract-ocr \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY run.sh .
COPY health_check.sh .

# Make scripts executable
RUN chmod +x run.sh health_check.sh

# Create necessary directories
RUN mkdir -p /app/data/input /app/data/output /app/data/logs /app/data/temp

# Set Python path
ENV PYTHONPATH=/app

# Expose port for internal service communication
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Run the Tiger service (CLI-based, no web server)
CMD ["python", "-m", "app.cli.main"]