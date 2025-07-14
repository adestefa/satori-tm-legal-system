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

# Copy application code
COPY core/ ./core/
COPY templates/ ./templates/
COPY cli.py .
COPY run.sh .
COPY health_check.sh .

# Make scripts executable
RUN chmod +x run.sh health_check.sh

# Create necessary directories
RUN mkdir -p /app/data/output /app/outputs

# Set Python path
ENV PYTHONPATH=/app

# Expose port for internal service communication
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Run the Monkey service (CLI-based, no web server)
CMD ["python", "cli.py"]