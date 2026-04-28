FROM python:3.11-slim

WORKDIR /app

# Efficiency: Install gevent for async workers
# Security: Create non-root user
RUN pip install --no-cache-dir gevent && \
    useradd -m -r -u 1000 appuser

# Copy requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Security: Switch to non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Expose the port Cloud Run expects
EXPOSE 8080

# Efficiency: Run gunicorn with gevent workers
CMD ["gunicorn", "--worker-class", "gevent", "--workers", "4", "--bind", "0.0.0.0:8080", "backend.app:app"]
