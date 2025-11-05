# OpenMemory Backend

Brain-inspired memory system with multi-sector organization, automatic decay, and advanced retrieval capabilities.

This directory contains the OpenMemory backend server (Node.js/TypeScript) integrated with Sentient Core v4.

## Quick Start

### Development

```bash
# Install dependencies
npm install

# Copy environment configuration
cp .env.example .env

# Edit configuration (optional)
nano .env

# Start development server
npm run dev
```

The server will start on http://localhost:8080

### Production

```bash
# Install dependencies
npm install --production

# Configure environment
cp .env.example .env
nano .env

# Build (if needed)
npm run build

# Start production server
npm start
```

### Docker

```bash
# Build image
docker build -t openmemory-backend .

# Run container
docker run -d \
  -p 8080:8080 \
  -v openmemory-data:/data \
  -e NODE_ENV=production \
  --name openmemory \
  openmemory-backend
```

Or use Docker Compose from the parent directory:

```bash
cd ..
docker-compose -f docker-compose.openmemory.yml up -d
```

## Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Server
PORT=8080
NODE_ENV=production

# Database
DB_PATH=/data/openmemory.db

# Embeddings
EMBEDDING_PROVIDER=local  # Options: local, openai, gemini, ollama
# OPENAI_API_KEY=sk-...
# GEMINI_API_KEY=...
# OLLAMA_URL=http://localhost:11434

# Authentication
ENABLE_AUTH=false
# API_KEY=your-secret-key

# Features
ENABLE_COMPRESSION=true
ENABLE_ASSOCIATIONS=true
ENABLE_PATTERN_DETECTION=true

# Performance
BATCH_SIZE=100
CACHE_EMBEDDINGS=true
MAX_CACHE_SIZE=10000

# Logging
LOG_LEVEL=info  # Options: debug, info, warn, error
LOG_FILE=/data/logs/openmemory.log

# CORS
CORS_ORIGIN=*  # Set to specific origins in production
```

### Memory Sectors

OpenMemory organizes memories into five cognitive sectors:

- **Episodic**: Event memories (decay: 0.0001)
- **Semantic**: Facts & knowledge (decay: 0.00001)
- **Procedural**: Habits & routines (decay: 0.00005)
- **Emotional**: Sentiment states (decay: 0.0002)
- **Reflective**: Meta-cognition (decay: 0.00002)

Decay rates determine how quickly memories fade. Lower values = slower decay.

## API Endpoints

### Health & Status

- `GET /health` - Server health check
- `GET /sectors` - Get sector information

### Memory Operations

- `POST /memory/add` - Add a memory
- `POST /memory/query` - Query memories (semantic search)
- `PATCH /memory/:id` - Update a memory
- `DELETE /memory/:id` - Delete a memory
- `GET /memory/all` - Get all memories (paginated)
- `POST /memory/reinforce` - Reinforce a memory (prevent decay)

### User Operations

- `GET /users/:userId/memories` - Get user memories
- `GET /users/:userId/summary` - Get user summary
- `POST /users/:userId/summary/regenerate` - Regenerate summary

### Advanced Features

- `POST /api/compression/compress` - Compress text
- `POST /api/compression/batch` - Batch compress
- `GET /api/compression/stats` - Compression statistics

### IDE Integration

- `POST /api/ide/events` - Store IDE event
- `POST /api/ide/context` - Query context
- `POST /api/ide/session/start` - Start session
- `POST /api/ide/session/end` - End session
- `GET /api/ide/patterns/:sessionId` - Get patterns

### LangGraph Memory

- `POST /lgm/store` - Store LangGraph memory
- `POST /lgm/retrieve` - Retrieve LangGraph memories
- `POST /lgm/context` - Get node context
- `POST /lgm/reflection` - Create reflection
- `GET /lgm/config` - Get configuration

## Development

### Project Structure

```
src/
├── server.ts         # Main server entry
├── routes/           # API routes
├── services/         # Business logic
│   ├── memory/       # Memory management
│   ├── embedding/    # Embedding generation
│   ├── search/       # Vector search
│   └── decay/        # Memory decay
├── models/           # Data models
├── db/               # Database layer
└── utils/            # Utilities
```

### Scripts

```bash
# Development
npm run dev          # Start with hot reload
npm run dev:debug    # Start with debugger

# Building
npm run build        # Build TypeScript
npm run clean        # Clean build artifacts

# Testing
npm test             # Run tests
npm run test:watch   # Run tests in watch mode
npm run test:cov     # Generate coverage report

# Linting
npm run lint         # Check code style
npm run lint:fix     # Fix code style issues

# Type Checking
npm run type-check   # Check TypeScript types
```

### Database

OpenMemory uses SQLite by default for ease of deployment. For production scaling:

**PostgreSQL** (recommended for production):

```bash
# Set in .env
DATABASE_TYPE=postgres
DATABASE_URL=postgresql://user:password@localhost:5432/openmemory
```

**Database Migrations**:

```bash
npm run migrate         # Run pending migrations
npm run migrate:create  # Create new migration
npm run migrate:rollback # Rollback last migration
```

## Integration with Sentient Core

OpenMemory is already integrated with Sentient Core v4. See the main project documentation:

- [OpenMemory Integration Guide](../docs/OPENMEMORY_INTEGRATION.md)
- [Integration Example](../examples/openmemory_integration.py)

### Python SDK

The Python SDK is located at `../sentient_core/integrations/openmemory/`

Basic usage from Sentient Core:

```python
from sentient_core.core.config import Config
from sentient_core.core.memory.memory_system import MemorySystem

config = Config({'memory.backend': 'openmemory'})
memory = MemorySystem(config)
memory.initialize()

memory.store("Important fact", memory_type='semantic')
results = memory.retrieve("fact", limit=5)
```

## Performance

### Benchmarks

- **Throughput**: ~338 queries per second
- **Latency**: 7.9ms per item average
- **Recall**: ~95% accuracy at scale
- **Memory**: ~2-3GB for 1M memories

### Optimization

1. **Enable Caching**:
   ```bash
   CACHE_EMBEDDINGS=true
   MAX_CACHE_SIZE=10000
   ```

2. **Use Local Embeddings**:
   ```bash
   EMBEDDING_PROVIDER=local
   ```

3. **Tune Batch Size**:
   ```bash
   BATCH_SIZE=200  # Higher = better throughput
   ```

4. **Enable Compression**:
   ```bash
   ENABLE_COMPRESSION=true
   ```

## Monitoring

### Logs

```bash
# View logs
tail -f /data/logs/openmemory.log

# With Docker
docker logs -f openmemory

# With Docker Compose
docker-compose -f docker-compose.openmemory.yml logs -f openmemory-backend
```

### Metrics

Access metrics at: http://localhost:8080/metrics (if Prometheus enabled)

### Health Checks

```bash
# Health check
curl http://localhost:8080/health

# Sector statistics
curl http://localhost:8080/sectors
```

## Troubleshooting

### Server Won't Start

1. Check port availability:
   ```bash
   lsof -i :8080
   ```

2. Check logs for errors:
   ```bash
   tail -f /data/logs/openmemory.log
   ```

3. Verify database path is writable:
   ```bash
   ls -la /data
   ```

### Embedding Errors

**Problem**: Embeddings failing to generate

**Solutions**:
- If using `local`: Check model is downloaded
- If using `openai`: Verify API key is set
- If using `ollama`: Ensure Ollama is running

```bash
# Test embedding provider
curl http://localhost:8080/health
# Check response for embedding_provider status
```

### Memory Issues

**Problem**: High memory usage

**Solutions**:
1. Reduce cache size: `MAX_CACHE_SIZE=5000`
2. Enable compression: `ENABLE_COMPRESSION=true`
3. Clean old memories periodically

### Performance Issues

**Problem**: Slow queries

**Solutions**:
1. Enable embedding cache
2. Increase batch size
3. Use local embeddings
4. Consider PostgreSQL for large datasets

## Resources

- **OpenMemory Repository**: https://github.com/thotsl4yer69/OpenMemory
- **Architecture Documentation**: https://github.com/thotsl4yer69/OpenMemory/blob/main/ARCHITECTURE.md
- **API Documentation**: Full API docs in the OpenMemory repository
- **Sentient Core Integration**: [../docs/OPENMEMORY_INTEGRATION.md](../docs/OPENMEMORY_INTEGRATION.md)

## License

See [LICENSE](LICENSE) file in the OpenMemory repository.

## Support

For issues:
- **Integration issues**: File in Sentient Core v4 repository
- **Backend issues**: File in OpenMemory repository
- **Configuration help**: See the integration guide
