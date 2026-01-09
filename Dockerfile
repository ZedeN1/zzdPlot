FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

WORKDIR /app

# Install dependencies as root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY --chown=appuser:appuser zzdPlot.py .

# Switch to non-root user
USER appuser

# Expose port (Using 36365 to match your custom port style)
EXPOSE 36365

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:36365')" || exit 1

# Run the application using Gunicorn
# zzdPlot:app.server -> Looks for 'app' object in zzdPlot.py and uses its underlying 'server'
CMD ["gunicorn", "--bind", "0.0.0.0:36365", "--workers", "2", "--threads", "4", "zzdPlot:server"]
