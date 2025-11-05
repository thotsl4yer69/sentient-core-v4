# Sentient Core v4 - Docker Installation Guide

Complete guide for deploying Sentient Core v4 using Docker and Docker Compose, including GPU support and orchestration.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Docker Installation](#docker-installation)
- [GPU Support](#gpu-support)
- [Docker Compose](#docker-compose)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **OS**: Linux, macOS, or Windows with Docker Desktop
- **RAM**: 8 GB minimum (16+ GB recommended)
- **Storage**: 20 GB free space

### For GPU Support

- **NVIDIA GPU**: CUDA-capable GPU
- **NVIDIA Docker Toolkit**: nvidia-docker2
- **Driver**: NVIDIA driver 525+

## Quick Start

```bash
# Clone repository
git clone https://github.com/thotsl4yer69/sentient-core-v4.git
cd sentient-core-v4

# Build and run with Docker Compose
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f sentient-core

# Access API
curl http://localhost:8080/api/health
```

## Docker Installation

### Install Docker

#### Linux

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Test installation
docker --version
docker run hello-world
```

#### macOS

Download and install [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)

#### Windows

Download and install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)

### Install Docker Compose

```bash
# Linux
sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify
docker-compose --version
```

## Building the Docker Image

### Basic Build

```bash
# Clone repository
git clone https://github.com/thotsl4yer69/sentient-core-v4.git
cd sentient-core-v4

# Build image
docker build -t sentient-core:v4 .

# Run container
docker run -d \
  --name sentient-core \
  -p 8080:8080 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/data:/app/data \
  sentient-core:v4
```

### Advanced Build with Build Args

```bash
# Build with specific Python version
docker build \
  --build-arg PYTHON_VERSION=3.10 \
  --build-arg CUDA_VERSION=12.1 \
  -t sentient-core:v4-cuda \
  -f Dockerfile.cuda \
  .
```

### Multi-Stage Build (Production)

The Dockerfile uses multi-stage builds for optimized images:

```dockerfile
# Production image (smaller)
docker build --target production -t sentient-core:v4-prod .

# Development image (includes dev tools)
docker build --target development -t sentient-core:v4-dev .
```

## GPU Support

### Install NVIDIA Container Toolkit

#### Linux

```bash
# Add repository
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Install
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Configure Docker
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Test
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

#### Windows/macOS with WSL2

1. Install Docker Desktop with WSL2 backend
2. Install NVIDIA drivers on Windows
3. Enable GPU support in Docker Desktop settings

### Run with GPU

```bash
# Single GPU
docker run -d \
  --name sentient-core \
  --gpus all \
  -p 8080:8080 \
  sentient-core:v4-cuda

# Specific GPU
docker run -d \
  --name sentient-core \
  --gpus '"device=0"' \
  -p 8080:8080 \
  sentient-core:v4-cuda

# Multiple GPUs
docker run -d \
  --name sentient-core \
  --gpus '"device=0,1"' \
  -p 8080:8080 \
  sentient-core:v4-cuda
```

## Docker Compose

### Basic docker-compose.yml

```yaml
version: '3.8'

services:
  sentient-core:
    image: sentient-core:v4
    build:
      context: .
      dockerfile: Dockerfile
    container_name: sentient-core
    ports:
      - "8080:8080"
    volumes:
      - ./config:/app/config
      - ./data:/app/data
      - ./models:/app/models
      - ./logs:/app/logs
    environment:
      - SENTIENT_CONFIG=/app/config/config.yaml
      - SENTIENT_LOG_LEVEL=INFO
      - SENTIENT_DEVICE=cpu
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### GPU-Enabled docker-compose.yml

```yaml
version: '3.8'

services:
  sentient-core-gpu:
    image: sentient-core:v4-cuda
    build:
      context: .
      dockerfile: Dockerfile.cuda
    container_name: sentient-core-gpu
    ports:
      - "8080:8080"
    volumes:
      - ./config:/app/config
      - ./data:/app/data
      - ./models:/app/models
      - ./logs:/app/logs
    environment:
      - SENTIENT_CONFIG=/app/config/config.yaml
      - SENTIENT_LOG_LEVEL=INFO
      - SENTIENT_DEVICE=cuda
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=compute,utility
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    restart: unless-stopped
```

### Full Stack with Database

```yaml
version: '3.8'

services:
  sentient-core:
    image: sentient-core:v4
    build: .
    container_name: sentient-core
    depends_on:
      - redis
      - postgres
    ports:
      - "8080:8080"
    volumes:
      - ./config:/app/config
      - ./models:/app/models
    environment:
      - SENTIENT_CONFIG=/app/config/config.yaml
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://sentient:password@postgres:5432/sentient
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: sentient-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    container_name: sentient-postgres
    environment:
      - POSTGRES_DB=sentient
      - POSTGRES_USER=sentient
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  redis_data:
  postgres_data:
```

### Commands

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d sentient-core

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Rebuild and restart
docker-compose up -d --build

# Scale service
docker-compose up -d --scale sentient-core=3
```

## Dockerfile Examples

### Basic Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Install application
RUN pip install -e .

# Create necessary directories
RUN mkdir -p /app/data /app/models /app/logs

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1

# Run application
CMD ["sentient-core", "run", "--host", "0.0.0.0", "--port", "8080"]
```

### CUDA Dockerfile

```dockerfile
FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHON_VERSION=3.10

WORKDIR /app

# Install Python and dependencies
RUN apt-get update && apt-get install -y \
    python${PYTHON_VERSION} \
    python${PYTHON_VERSION}-dev \
    python3-pip \
    build-essential \
    git \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Update alternatives
RUN update-alternatives --install /usr/bin/python python /usr/bin/python${PYTHON_VERSION} 1
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python${PYTHON_VERSION} 1

# Copy requirements
COPY requirements.txt requirements-cuda.txt ./

# Install PyTorch with CUDA support
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install other dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-cuda.txt

# Copy application
COPY . .

# Install application
RUN pip install -e .

# Create directories
RUN mkdir -p /app/data /app/models /app/logs

EXPOSE 8080

# Set CUDA environment
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1

CMD ["sentient-core", "run", "--host", "0.0.0.0", "--port", "8080", "--device", "cuda"]
```

## Kubernetes Deployment

### Basic Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sentient-core
  labels:
    app: sentient-core
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sentient-core
  template:
    metadata:
      labels:
        app: sentient-core
    spec:
      containers:
      - name: sentient-core
        image: sentient-core:v4
        ports:
        - containerPort: 8080
        env:
        - name: SENTIENT_CONFIG
          value: "/app/config/config.yaml"
        - name: SENTIENT_LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
        volumeMounts:
        - name: config
          mountPath: /app/config
        - name: models
          mountPath: /app/models
        livenessProbe:
          httpGet:
            path: /api/health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/ready
            port: 8080
          initialDelaySeconds: 20
          periodSeconds: 5
      volumes:
      - name: config
        configMap:
          name: sentient-config
      - name: models
        persistentVolumeClaim:
          claimName: sentient-models-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: sentient-core-service
spec:
  selector:
    app: sentient-core
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: LoadBalancer
```

### GPU Deployment (with NVIDIA GPU Operator)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sentient-core-gpu
spec:
  replicas: 1
  selector:
    matchLabels:
      app: sentient-core-gpu
  template:
    metadata:
      labels:
        app: sentient-core-gpu
    spec:
      containers:
      - name: sentient-core
        image: sentient-core:v4-cuda
        resources:
          limits:
            nvidia.com/gpu: 1
        env:
        - name: NVIDIA_VISIBLE_DEVICES
          value: "all"
        - name: NVIDIA_DRIVER_CAPABILITIES
          value: "compute,utility"
```

## Configuration

### Environment Variables

```bash
# Core settings
SENTIENT_CONFIG=/app/config/config.yaml
SENTIENT_LOG_LEVEL=INFO
SENTIENT_DEVICE=cuda

# API settings
SENTIENT_API_HOST=0.0.0.0
SENTIENT_API_PORT=8080
SENTIENT_API_WORKERS=4

# Model settings
SENTIENT_MODEL_PATH=/app/models
SENTIENT_MAX_MEMORY=8GB

# Database
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379

# Security
SENTIENT_API_KEY=your-secure-api-key
SENTIENT_ENABLE_AUTH=true
```

### Volume Mounts

```bash
# Config files
-v $(pwd)/config:/app/config

# Model storage
-v $(pwd)/models:/app/models

# Data persistence
-v $(pwd)/data:/app/data

# Logs
-v $(pwd)/logs:/app/logs

# Custom plugins
-v $(pwd)/plugins:/app/plugins
```

## Container Management

### Useful Commands

```bash
# View running containers
docker ps

# View all containers
docker ps -a

# View logs
docker logs sentient-core
docker logs -f sentient-core  # Follow logs

# Execute command in container
docker exec -it sentient-core bash
docker exec sentient-core sentient-core --version

# Copy files
docker cp sentient-core:/app/logs/sentient.log ./logs/

# Inspect container
docker inspect sentient-core

# View resource usage
docker stats sentient-core

# Restart container
docker restart sentient-core

# Stop container
docker stop sentient-core

# Remove container
docker rm sentient-core
```

### Image Management

```bash
# List images
docker images

# Remove image
docker rmi sentient-core:v4

# Tag image
docker tag sentient-core:v4 myregistry/sentient-core:v4

# Push to registry
docker push myregistry/sentient-core:v4

# Pull from registry
docker pull myregistry/sentient-core:v4

# Prune unused images
docker image prune -a
```

## Verification

### Health Checks

```bash
# Check container status
docker ps

# Test API endpoint
curl http://localhost:8080/api/health

# Check logs
docker logs sentient-core | tail -n 50

# Execute health check
docker exec sentient-core sentient-core --check-system
```

### Performance Testing

```bash
# Run benchmark inside container
docker exec sentient-core sentient-core benchmark --quick

# Monitor resources
docker stats sentient-core
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs sentient-core

# Check events
docker events --filter container=sentient-core

# Inspect container
docker inspect sentient-core

# Run in interactive mode
docker run -it --rm sentient-core:v4 bash
```

### GPU Not Detected

```bash
# Verify nvidia-docker
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

# Check GPU visibility
docker exec sentient-core-gpu nvidia-smi

# Verify CUDA in container
docker exec sentient-core-gpu python -c "import torch; print(torch.cuda.is_available())"
```

### Permission Issues

```bash
# Run as specific user
docker run --user $(id -u):$(id -g) sentient-core:v4

# Fix volume permissions
sudo chown -R $(id -u):$(id -g) ./data ./logs
```

### Network Issues

```bash
# Check port binding
docker port sentient-core

# Test from within container
docker exec sentient-core curl http://localhost:8080/api/health

# Check network
docker network ls
docker network inspect bridge
```

### Memory Issues

```bash
# Increase memory limit
docker run --memory="8g" --memory-swap="16g" sentient-core:v4

# Monitor memory
docker stats sentient-core
```

## Best Practices

### Security

```yaml
# Run as non-root user
USER sentient

# Use secrets for sensitive data
secrets:
  api_key:
    external: true

# Scan images
docker scan sentient-core:v4
```

### Optimization

```dockerfile
# Use multi-stage builds
FROM python:3.10 AS builder
# ... build steps ...

FROM python:3.10-slim
COPY --from=builder /app /app

# Minimize layers
RUN apt-get update && apt-get install -y \
    package1 package2 \
    && rm -rf /var/lib/apt/lists/*

# Use .dockerignore
# Add: .git, __pycache__, *.pyc, tests, docs
```

### Monitoring

```yaml
# Add Prometheus metrics
services:
  sentient-core:
    # ... other config ...
    labels:
      - "prometheus.scrape=true"
      - "prometheus.port=9090"
```

## Next Steps

- [Configuration Guide](../guides/CONFIGURATION.md)
- [API Reference](../api/API_REFERENCE.md)
- [Scaling Guide](../guides/SCALING.md)
- [Monitoring Guide](../guides/MONITORING.md)

## Support

For Docker-specific issues:
- Check [Troubleshooting Guide](../TROUBLESHOOTING.md)
- Report on [GitHub](https://github.com/thotsl4yer69/sentient-core-v4/issues)
- Tag with `docker` or `kubernetes`
