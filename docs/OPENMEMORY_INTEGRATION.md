# OpenMemory Integration Guide

OpenMemory is a brain-inspired memory system with advanced cognitive architecture, automatic decay, and sophisticated retrieval capabilities. This guide covers how to use OpenMemory as the memory backend for Sentient Core v4.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Advanced Features](#advanced-features)
- [Performance](#performance)
- [Troubleshooting](#troubleshooting)

## Overview

OpenMemory provides a sophisticated alternative to traditional vector databases by implementing a **cognitive architecture** that organizes memories into different sectors, each with unique characteristics and decay rates. This mirrors how the human brain organizes different types of information.

### Why OpenMemory?

- **Brain-Inspired Design**: Multi-sector memory organization mimicking human cognitive architecture
- **Automatic Memory Decay**: Memories naturally fade unless reinforced, like human memory
- **Graph-Based Associations**: Memories are linked through semantic relationships
- **Superior Performance**: ~95% recall accuracy, 2-3× faster than alternatives
- **User Isolation**: Built-in support for multi-user memory spaces
- **Zero Python Dependencies**: The Python SDK uses only standard library

## Features

### Memory Sectors

OpenMemory organizes memories into five cognitive sectors:

1. **Episodic** (`episodic`)
   - Event memories and temporal experiences
   - Maps to: `short_term` memory type in Sentient Core
   - Use for: Conversations, interactions, recent events
   - Decay rate: Faster (events fade quickly)

2. **Semantic** (`semantic`)
   - Facts, knowledge, and preferences
   - Maps to: `long_term` and `semantic` memory types
   - Use for: Learned facts, user preferences, domain knowledge
   - Decay rate: Slower (knowledge persists longer)

3. **Procedural** (`procedural`)
   - Habits, triggers, and action patterns
   - New memory type in Sentient Core v4
   - Use for: Workflows, routines, behavioral patterns
   - Decay rate: Moderate

4. **Emotional** (`emotional`)
   - Sentiment states and affective data
   - New memory type in Sentient Core v4
   - Use for: Sentiment analysis, emotional context
   - Decay rate: Fast (emotions are transient)

5. **Reflective** (`reflective`)
   - Meta-cognitive insights and introspection
   - New memory type in Sentient Core v4
   - Use for: Self-analysis, learning reflections, summaries
   - Decay rate: Slow (meta-knowledge is valuable)

### Core Capabilities

- **Vector Similarity Search**: Fast, accurate semantic retrieval
- **Automatic Decay**: Memories fade naturally with configurable rates
- **Memory Reinforcement**: Boost salience to prevent decay
- **Association Graphs**: Build and traverse semantic relationships
- **Pattern Detection**: Identify recurring patterns in memories
- **User Summaries**: Generate personality summaries from memories
- **Compression**: Efficient storage with semantic compression
- **LangGraph Integration**: Compatible with LangGraph workflows
- **IDE Integration**: Track coding context and patterns

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Sentient Core v4                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           Memory System (memory_system.py)          │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │  OpenMemory Backend (openmemory_backend.py)  │  │   │
│  │  └────────────────┬─────────────────────────────┘  │   │
│  └───────────────────┼────────────────────────────────┘   │
└────────────────────┼─┼────────────────────────────────────┘
                     │ │ Python SDK (HTTP Client)
                     │ │
                     ▼ ▼
         ┌───────────────────────────────┐
         │  OpenMemory Backend Server    │
         │  (Node.js/TypeScript)         │
         │  ┌─────────────────────────┐  │
         │  │   Vector Engine         │  │
         │  │   - Embedding           │  │
         │  │   - Similarity Search   │  │
         │  └─────────────────────────┘  │
         │  ┌─────────────────────────┐  │
         │  │   Memory Sectors        │  │
         │  │   - Episodic            │  │
         │  │   - Semantic            │  │
         │  │   - Procedural          │  │
         │  │   - Emotional           │  │
         │  │   - Reflective          │  │
         │  └─────────────────────────┘  │
         │  ┌─────────────────────────┐  │
         │  │   Storage (SQLite)      │  │
         │  └─────────────────────────┘  │
         └───────────────────────────────┘
```

## Installation

### Option 1: Docker Compose (Recommended)

The easiest way to run Sentient Core v4 with OpenMemory:

```bash
# Start everything (Sentient Core + OpenMemory + Dashboard)
docker-compose -f docker-compose.openmemory.yml up -d

# View logs
docker-compose -f docker-compose.openmemory.yml logs -f

# Stop everything
docker-compose -f docker-compose.openmemory.yml down
```

Services will be available at:
- **OpenMemory Backend**: http://localhost:8080
- **OpenMemory Dashboard**: http://localhost:3000
- **Sentient Core API**: http://localhost:8000

### Option 2: Manual Installation

#### 1. Install OpenMemory Backend

```bash
cd openmemory-backend

# Install dependencies
npm install

# Copy and configure environment
cp .env.example .env
nano .env  # Edit configuration

# Start the server
npm start
```

#### 2. Install OpenMemory Dashboard (Optional)

```bash
cd openmemory-dashboard

# Install dependencies
npm install

# Configure API URL
echo "NEXT_PUBLIC_API_URL=http://localhost:8080" > .env.local

# Start the dashboard
npm run dev
```

#### 3. Configure Sentient Core

The OpenMemory Python SDK is already integrated. Just configure the backend:

```yaml
# config/local.yaml
memory:
  backend: openmemory

openmemory:
  url: http://localhost:8080
  api_key: ""  # Optional
  user_id: "your_user_id"
```

## Configuration

### Basic Configuration

Edit `config/local.yaml`:

```yaml
memory:
  backend: openmemory  # Use OpenMemory as backend

openmemory:
  # Server connection
  url: "http://localhost:8080"
  api_key: ""  # Set if your server requires auth

  # User isolation
  user_id: "default"  # Unique ID for this agent/user

  # Auto-consolidation
  auto_consolidate: true
```

### Advanced Configuration

```yaml
openmemory:
  # Embedding configuration
  embedding:
    provider: "local"  # Options: local, openai, gemini, ollama
    model: "all-MiniLM-L6-v2"

  # Performance tuning
  performance:
    batch_size: 100
    cache_embeddings: true
    compression_enabled: true

  # Advanced features
  features:
    enable_associations: true      # Build memory graphs
    enable_pattern_detection: true # Detect patterns
    enable_user_summaries: true    # Generate summaries
    enable_ide_integration: false  # IDE tracking
    enable_langgraph: false        # LangGraph support
```

### OpenMemory Backend Configuration

Edit `openmemory-backend/.env`:

```bash
# Server
PORT=8080
NODE_ENV=production

# Database
DB_PATH=/data/openmemory.db

# Embeddings
EMBEDDING_PROVIDER=local  # or: openai, gemini, ollama
# OPENAI_API_KEY=sk-...
# GEMINI_API_KEY=...

# Authentication (optional)
ENABLE_AUTH=false
# API_KEY=your-secret-key

# Features
ENABLE_COMPRESSION=true
ENABLE_ASSOCIATIONS=true
ENABLE_PATTERN_DETECTION=true

# Performance
BATCH_SIZE=100
CACHE_EMBEDDINGS=true

# Logging
LOG_LEVEL=info
```

## Usage

### Basic Usage

```python
from sentient_core.core.config import Config
from sentient_core.core.memory.memory_system import MemorySystem

# Configure with OpenMemory backend
config = Config({
    'memory.backend': 'openmemory',
    'openmemory.url': 'http://localhost:8080',
    'openmemory.user_id': 'my_agent'
})

# Initialize memory system
memory = MemorySystem(config)
memory.initialize()

# Store memories
memory.store(
    data="The user prefers morning meetings",
    memory_type='semantic',  # Stored in semantic sector
    metadata={
        'tags': ['preference', 'meetings'],
        'importance': 0.8
    }
)

# Retrieve memories with semantic search
results = memory.retrieve(
    query="What are the user's meeting preferences?",
    memory_type='semantic',
    limit=5,
    min_score=0.7
)

for mem in results:
    print(f"Score: {mem['score']:.3f}")
    print(f"Content: {mem['content']}")
    print(f"Sector: {mem['sector']}\n")
```

### Memory Types Mapping

| Sentient Core Type | OpenMemory Sector | Use Case |
|-------------------|-------------------|----------|
| `short_term` | `episodic` | Recent conversations, events |
| `long_term` | `semantic` | Persistent knowledge, facts |
| `episodic` | `episodic` | Specific events, experiences |
| `semantic` | `semantic` | Facts, preferences, knowledge |
| `procedural` | `procedural` | Habits, routines, workflows |
| `emotional` | `emotional` | Sentiment, feelings, tone |
| `reflective` | `reflective` | Meta-cognition, insights |

### Working with Different Sectors

```python
# Store episodic memory (events)
memory.store(
    "Completed the AI model training at 3pm",
    memory_type='episodic',
    metadata={'tags': ['event', 'training'], 'importance': 0.6}
)

# Store procedural memory (habits)
memory.store(
    "Always validate input data before processing",
    memory_type='procedural',
    metadata={'tags': ['workflow', 'validation'], 'importance': 0.7}
)

# Store emotional memory (sentiment)
memory.store(
    "User expressed frustration with slow response times",
    memory_type='emotional',
    metadata={'tags': ['sentiment', 'frustration'], 'importance': 0.8}
)

# Store reflective memory (meta-cognition)
memory.store(
    "Learned that breaking complex tasks into smaller steps improves success rate",
    memory_type='reflective',
    metadata={'tags': ['learning', 'strategy'], 'importance': 0.9}
)
```

## Advanced Features

### Memory Reinforcement

Prevent important memories from decaying:

```python
# Get the OpenMemory backend
backend = memory.openmemory_backend

# Reinforce a memory
backend.reinforce(memory_id='abc123', boost=0.3)
```

### Direct SDK Access

For advanced features, access the OpenMemory client directly:

```python
from sentient_core.integrations.openmemory.client import OpenMemory, SECTORS

# Direct client access
client = OpenMemory(base_url='http://localhost:8080')

# Query specific sector
results = client.query_sector(
    query="Python programming",
    sector=SECTORS['SEMANTIC'],
    k=10
)

# Get user summary
summary = client.get_user_summary('my_agent')
print(f"Summary: {summary['summary']}")

# Regenerate summary
new_summary = client.regenerate_user_summary('my_agent')
```

### Memory Associations

Build graphs of related memories:

```python
# OpenMemory automatically builds associations
# Query to traverse the graph
results = client.query(
    query="machine learning",
    k=20  # Get more results to see associations
)

# Memories will include association information
for mem in results['matches']:
    print(f"Memory: {mem['content']}")
    print(f"Associations: {mem.get('associations', [])}")
```

### Pattern Detection

Detect recurring patterns in memories:

```python
# Store memories of a session
session_id = client.ide_start_session(
    user_id='developer',
    project_name='sentient-core'
)

# ... work happens, memories stored ...

# Get detected patterns
patterns = client.ide_get_patterns(session_id)
for pattern in patterns['patterns']:
    print(f"Pattern: {pattern['type']}")
    print(f"Frequency: {pattern['count']}")
```

### Compression

Use semantic compression for efficient storage:

```python
# Compress long text
result = client.compress("Very long text here...")
print(f"Compressed: {result['comp']}")
print(f"Compression ratio: {result['m']['ratio']}")

# Analyze compression options
analysis = client.analyze_compression("Text to analyze...")
print(f"Recommended algorithm: {analysis['rec']}")
```

## Performance

### Benchmarks

OpenMemory provides excellent performance compared to traditional vector databases:

| Metric | OpenMemory | Traditional VectorDB |
|--------|-----------|---------------------|
| Recall Accuracy | ~95% | ~85-90% |
| Throughput | 338 QPS | ~100-150 QPS |
| Scalability | 7.9ms/item | 15-25ms/item |
| Cost (Cloud) | Baseline | 6-12× higher |

### Optimization Tips

1. **Enable Caching**:
   ```yaml
   openmemory:
     performance:
       cache_embeddings: true
   ```

2. **Use Compression**:
   ```yaml
   openmemory:
     performance:
       compression_enabled: true
   ```

3. **Batch Operations**:
   ```python
   # Store multiple memories at once
   for item in batch:
       memory.store(item['data'], item['type'], item['metadata'])
   ```

4. **Tune Batch Size**:
   ```yaml
   openmemory:
     performance:
       batch_size: 200  # Increase for better throughput
   ```

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to OpenMemory backend

**Solution**:
```bash
# Check if backend is running
curl http://localhost:8080/health

# If not running, start it
cd openmemory-backend
npm start

# Check logs
tail -f logs/openmemory.log
```

### Memory Not Found

**Problem**: Stored memories not being retrieved

**Solution**:
1. Check memory was stored successfully
2. Verify user_id matches
3. Try lower min_score threshold
4. Ensure embeddings are generated (check backend logs)

```python
# Debug retrieval
results = memory.retrieve(
    query="test",
    memory_type='all',
    limit=100,
    min_score=0.0  # Get all memories
)
print(f"Total memories: {len(results)}")
```

### Performance Issues

**Problem**: Slow retrieval or storage

**Solutions**:
1. Enable caching and compression
2. Increase batch size
3. Use local embeddings instead of API-based
4. Check database size (consider cleanup)

```python
# Get statistics
stats = memory.get_stats()
print(f"Total memories: {stats['total_memories']}")

# Clear old memories if needed
memory.clear(memory_type='episodic')  # Clear events
```

### Backend Errors

**Problem**: Backend returns errors

**Check**:
```bash
# View backend logs
docker-compose -f docker-compose.openmemory.yml logs openmemory-backend

# Or if running manually
cd openmemory-backend
npm run dev  # Run in development mode for verbose logs
```

## Example Application

See the complete example in `examples/openmemory_integration.py`:

```bash
# Run the example
python examples/openmemory_integration.py
```

This demonstrates:
- Basic memory operations across all sectors
- Semantic search and retrieval
- Memory reinforcement
- Statistics and monitoring
- Advanced features

## Resources

- **OpenMemory GitHub**: https://github.com/thotsl4yer69/OpenMemory
- **OpenMemory Documentation**: https://github.com/thotsl4yer69/OpenMemory/blob/main/README.md
- **Architecture Details**: https://github.com/thotsl4yer69/OpenMemory/blob/main/ARCHITECTURE.md
- **Sentient Core Docs**: [docs/README.md](README.md)

## Support

For issues related to:
- **Integration**: File an issue in the Sentient Core v4 repository
- **OpenMemory Backend**: File an issue in the OpenMemory repository
- **Configuration**: Check this guide and the example configuration files

## Next Steps

1. ✅ Install and configure OpenMemory
2. ✅ Update your `config/local.yaml`
3. ✅ Run the example application
4. ✅ Access the dashboard at http://localhost:3000
5. ✅ Integrate with your Sentient Core agents
6. 🚀 Build amazing AI systems with persistent memory!
