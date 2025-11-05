# Sentient Core v4 - Docker Image
# Multi-stage build for optimized production image

# Build stage
FROM python:3.10-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.10-slim as production

LABEL maintainer="Sentient Core Team"
LABEL version="4.0.0"
LABEL description="Sentient Core v4 - Advanced AI Cognitive Architecture"

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    portaudio19-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application
COPY . .

# Install application
RUN pip install --no-cache-dir -e .

# Create necessary directories
RUN mkdir -p /app/data /app/models /app/logs /app/config

# Create non-root user
RUN useradd -m -u 1000 sentient && \
    chown -R sentient:sentient /app
USER sentient

# Environment variables
ENV SENTIENT_HOME=/app
ENV SENTIENT_CONFIG=/app/config/config.yaml
ENV SENTIENT_MODELS=/app/models
ENV PYTHONUNBUFFERED=1
ENV PATH=/root/.local/bin:$PATH

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1

# Run application
CMD ["python", "-m", "sentient_core.main", "run", "--host", "0.0.0.0", "--port", "8080"]
