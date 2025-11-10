# Sentient Core v4 - Async Architecture Documentation

## Overview

Sentient Core v4 is built on a fully asynchronous architecture using Python's `asyncio` library. This document explains the design patterns, best practices, and implementation details of the async system.

## Table of Contents

1. [Why Async?](#why-async)
2. [Core Async Components](#core-async-components)
3. [Task Lifecycle Management](#task-lifecycle-management)
4. [Error Handling Patterns](#error-handling-patterns)
5. [Concurrency Patterns](#concurrency-patterns)
6. [Best Practices](#best-practices)
7. [Common Pitfalls](#common-pitfalls)

---

## Why Async?

The distributed consciousness system requires:
- **Concurrent I/O**: Network communication between nodes (Pi 5 ↔ Jetson)
- **Real-time Responsiveness**: 10Hz state synchronization without blocking
- **Sensor Integration**: Multi-sensor data fusion from RF, camera, health monitors
- **Heartbeat Monitoring**: Continuous node health checks
- **Resource Efficiency**: Thousands of concurrent operations without thread overhead

Traditional threading would create:
- High memory overhead (1MB+ per thread)
- Complex synchronization requirements
- GIL contention in CPU-bound operations
- Difficult debugging and race conditions

Asyncio provides:
- **Cooperative Multitasking**: Single-threaded, no GIL issues
- **Low Overhead**: 100KB per coroutine vs 1MB+ per thread
- **Explicit Context Switching**: Clear control flow with `await`
- **Native Support**: aiohttp, asyncio primitives

---

## Core Async Components

### 1. Main Event Loop

**Location**: `sentient_core/main_distributed.py`

```python
async def main():
    """Main entry point."""
    system = SentientCoreDistributed(config_path=args.config)

    try:
        await system.run()  # Starts the event loop
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())  # Creates and runs event loop
```

**Key Points**:
- `asyncio.run()` creates the event loop, runs until completion
- Handles KeyboardInterrupt gracefully
- Ensures proper cleanup on exit

### 2. Distributed Consciousness

**Location**: `sentient_core/distributed/consciousness.py`

The distributed consciousness system uses multiple background tasks:

```python
async def start(self, local_node_spec: NodeSpec):
    """Start distributed consciousness system."""
    self.running = True

    # Initialize components
    self.local_node = Node(...)
    self.sync_manager = SyncManager(...)
    self.heartbeat_monitor = HeartbeatMonitor(...)

    # Start heartbeat monitoring
    await self.heartbeat_monitor.start(
        self.nodes,
        self._ping_node,
        self._handle_node_status_change
    )

    # Start background tasks
    self.sync_task = asyncio.create_task(self._sync_loop())
    self.discovery_task = asyncio.create_task(self._discovery_loop())
```

**Background Tasks**:

1. **Sync Loop** (`_sync_loop`): 10Hz state synchronization
2. **Discovery Loop** (`_discovery_loop`): Node auto-discovery
3. **Heartbeat Loop** (in HeartbeatMonitor): Health monitoring

### 3. Heartbeat Monitor

**Location**: `sentient_core/distributed/heartbeat.py`

```python
class HeartbeatMonitor:
    async def start(self, nodes, ping_callback, status_callback):
        """Start heartbeat monitoring."""
        self.running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())

    async def _monitor_loop(self):
        """Continuous heartbeat monitoring."""
        while self.running:
            # Check all nodes
            for node_id, node in self.nodes.items():
                if self._is_alive(node_id):
                    # Ping node
                    await self.ping_callback(node)
                else:
                    # Mark as offline
                    await self.status_callback(node_id, False)

            # Sleep for ping interval
            await asyncio.sleep(self.ping_interval)
```

---

## Task Lifecycle Management

### Creating Tasks

**ALWAYS** store task references for proper cleanup:

```python
# ✅ CORRECT: Store task reference
self.sync_task = asyncio.create_task(self._sync_loop())
self.discovery_task = asyncio.create_task(self._discovery_loop())

# ❌ WRONG: Task not stored (memory leak)
asyncio.create_task(self._sync_loop())  # Task may not be cleaned up
```

### Stopping Tasks

**Pattern**: Cancel → Wait → Handle CancelledError

```python
async def stop(self):
    """Stop distributed consciousness."""
    self.running = False

    # Stop heartbeat monitor
    if self.heartbeat_monitor:
        await self.heartbeat_monitor.stop()

    # Cancel background tasks
    if self.sync_task and not self.sync_task.done():
        self.sync_task.cancel()
        try:
            await self.sync_task
        except asyncio.CancelledError:
            pass  # Expected when cancelling

    if self.discovery_task and not self.discovery_task.done():
        self.discovery_task.cancel()
        try:
            await self.discovery_task
        except asyncio.CancelledError:
            pass
```

**Key Points**:
1. Check `not task.done()` before cancelling
2. `await` the task after cancelling to ensure cleanup
3. Catch and ignore `asyncio.CancelledError`

### Task Patterns

#### Pattern 1: Infinite Loop with Condition

```python
async def _sync_loop(self):
    """Continuous state synchronization loop."""
    while self.running:
        try:
            await self._broadcast_state()
            await asyncio.sleep(self.sync_interval)
        except Exception as e:
            logger.error(f"Sync loop error: {e}")
            await asyncio.sleep(1)  # Backoff on error
```

#### Pattern 2: Periodic Task with Timeout

```python
async def _remote_inference(self, user_input, context, target_node):
    """Run inference on remote node."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=target_node.spec.max_latency)
            ) as resp:
                result = await resp.json()
                return result
    except asyncio.TimeoutError:
        logger.error(f"Remote inference timeout")
        return await self._local_inference(user_input, context)
```

---

## Error Handling Patterns

### Pattern 1: Try-Except with Fallback

```python
async def route_query(self, user_input, context, required_capability):
    """Route query to best available node."""
    try:
        target_node = self._select_node(complexity, required_capability)

        if target_node == self.local_node:
            return await self._local_inference(user_input, context)
        else:
            return await self._remote_inference(user_input, context, target_node)

    except Exception as e:
        logger.error(f"Query routing error: {e}")
        # Fallback to local inference
        return await self._local_inference(user_input, context)
```

### Pattern 2: Network Error Handling

```python
async def _ping_node(self, node: Node) -> bool:
    """Ping a remote node to check availability."""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{node.spec.endpoint_url}{ENDPOINT_HEALTH}"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    node.heartbeat()
                    if self.heartbeat_monitor:
                        self.heartbeat_monitor.record_pong(node.spec.node_id)
                    return True
                return False

    except Exception as e:
        logger.debug(f"Ping failed for {node.spec.name}: {e}")
        return False
```

**Key Points**:
- Catch broad `Exception` for network operations
- Log at `debug` level for expected failures
- Return False/None to indicate failure gracefully

### Pattern 3: Timeout with Fallback

```python
async def _shutdown_distributed(self):
    """Shutdown distributed consciousness with timeout."""
    if self.distributed_consciousness:
        try:
            logger.info("Stopping Distributed Consciousness...")
            # Add timeout to prevent hanging
            await asyncio.wait_for(
                self.distributed_consciousness.stop(),
                timeout=10.0
            )
            logger.info("✓ Distributed Consciousness stopped")
        except asyncio.TimeoutError:
            logger.error("✗ Distributed Consciousness shutdown timeout")
        except Exception as e:
            logger.error(f"✗ Distributed Consciousness shutdown error: {e}")
```

---

## Concurrency Patterns

### Pattern 1: Concurrent HTTP Requests

When broadcasting state to multiple nodes:

```python
async def _broadcast_state(self):
    """Broadcast local state to all remote nodes."""
    state_update = {
        'node_id': self.local_node.spec.node_id,
        'state': self.shared_state,
        'timestamp': datetime.now().isoformat()
    }

    # Send to each node (concurrent, but using loop for error handling)
    for node_id, node in self.nodes.items():
        if not node.is_online or not node.spec.endpoint_url:
            continue

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=state_update,
                    timeout=aiohttp.ClientTimeout(total=2)
                ) as resp:
                    if resp.status == 200:
                        node.heartbeat()
        except Exception as e:
            logger.debug(f"Sync error for {node.spec.name}: {e}")
```

### Pattern 2: Task Gathering

For truly parallel operations:

```python
async def initialize_all_nodes(self, node_specs):
    """Initialize multiple nodes in parallel."""
    tasks = [
        self.register_remote_node(spec)
        for spec in node_specs
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Node {i} initialization failed: {result}")
        else:
            logger.info(f"Node {i} initialized successfully")
```

### Pattern 3: Resource Pooling

Using `async with` for connection management:

```python
async def _remote_inference(self, user_input, context, target_node):
    """Run inference on remote node."""
    # Session is automatically closed when exiting context
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, timeout=timeout) as resp:
            result = await resp.json()
            return result
```

---

## Best Practices

### 1. Always Use `await` for Async Functions

```python
# ✅ CORRECT
result = await self._remote_inference(input, context, node)

# ❌ WRONG: Creates coroutine object but doesn't execute
result = self._remote_inference(input, context, node)
```

### 2. Use `asyncio.sleep()` Not `time.sleep()`

```python
# ✅ CORRECT: Yields control to event loop
await asyncio.sleep(1)

# ❌ WRONG: Blocks entire event loop
time.sleep(1)
```

### 3. Use Async Context Managers

```python
# ✅ CORRECT: Async context manager
async with aiohttp.ClientSession() as session:
    async with session.get(url) as resp:
        data = await resp.json()

# ❌ WRONG: Sync context manager (may not work)
with aiohttp.ClientSession() as session:
    with session.get(url) as resp:
        data = resp.json()
```

### 4. Store Long-Running Task References

```python
# ✅ CORRECT: Store reference
self.sync_task = asyncio.create_task(self._sync_loop())

# Cancel later
if self.sync_task:
    self.sync_task.cancel()
    await self.sync_task
```

### 5. Add Timeouts to Network Operations

```python
# ✅ CORRECT: Always use timeouts
async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
    data = await resp.json()

# ❌ WRONG: No timeout (may hang forever)
async with session.get(url) as resp:
    data = await resp.json()
```

### 6. Handle Cancellation Gracefully

```python
async def _monitor_loop(self):
    """Monitoring loop that handles cancellation."""
    try:
        while self.running:
            await self._check_health()
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logger.info("Monitor loop cancelled")
        # Cleanup
        raise  # Re-raise to propagate cancellation
```

---

## Common Pitfalls

### Pitfall 1: Forgetting `await`

```python
# ❌ WRONG: Coroutine created but not executed
def process_query(self, query):
    self._remote_inference(query)  # Missing await!

# ✅ CORRECT
async def process_query(self, query):
    await self._remote_inference(query)
```

**Symptom**: "coroutine was never awaited" warnings

### Pitfall 2: Blocking Operations in Async Code

```python
# ❌ WRONG: Blocks event loop
async def load_model(self, path):
    data = open(path).read()  # Synchronous file I/O blocks loop
    return data

# ✅ CORRECT: Use async file I/O or run in executor
async def load_model(self, path):
    async with aiofiles.open(path) as f:
        data = await f.read()
    return data

# OR use executor for sync operations
async def load_model(self, path):
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, self._sync_load, path)
    return data
```

### Pitfall 3: Not Handling Task Cancellation

```python
# ❌ WRONG: CancelledError propagates unexpectedly
async def stop(self):
    self.task.cancel()
    # If you await something here, it might raise CancelledError

# ✅ CORRECT: Handle CancelledError
async def stop(self):
    if self.task and not self.task.done():
        self.task.cancel()
        try:
            await self.task
        except asyncio.CancelledError:
            pass
```

### Pitfall 4: Shared State Without Locks

```python
# ❌ WRONG: Race condition
async def update_counter(self):
    current = self.counter
    await asyncio.sleep(0.1)  # Other task might modify counter here!
    self.counter = current + 1

# ✅ CORRECT: Use asyncio.Lock
async def update_counter(self):
    async with self.lock:
        current = self.counter
        await asyncio.sleep(0.1)
        self.counter = current + 1
```

### Pitfall 5: Creating Session Per Request

```python
# ❌ WRONG: Creates new session for each request (slow)
async def ping_node(self, node):
    async with aiohttp.ClientSession() as session:
        async with session.get(node.url) as resp:
            return resp.status == 200

# ✅ CORRECT: Reuse session for multiple requests
class NodeMonitor:
    def __init__(self):
        self.session = None

    async def start(self):
        self.session = aiohttp.ClientSession()

    async def ping_node(self, node):
        async with self.session.get(node.url) as resp:
            return resp.status == 200

    async def stop(self):
        await self.session.close()
```

---

## Async Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    asyncio Event Loop                        │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │          Main Coroutine (run)                          │ │
│  │  - Initializes all components                          │ │
│  │  - Starts background tasks                             │ │
│  │  - Waits for completion                                │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  Background Tasks:                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Sync Loop   │  │ Discovery    │  │  Heartbeat   │     │
│  │  (10Hz)      │  │  Loop        │  │  Monitor     │     │
│  │              │  │  (30s)       │  │  (5s)        │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  On-Demand Coroutines:                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Query        │  │ Remote       │  │ Node         │     │
│  │ Routing      │  │ Inference    │  │ Ping         │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## Performance Considerations

### 1. Task Creation Overhead

Creating tasks has overhead (~100KB memory, 10-50μs CPU):

```python
# ❌ AVOID: Creating tasks in tight loops
for i in range(10000):
    asyncio.create_task(process(i))

# ✅ BETTER: Batch processing
async def process_batch(items):
    for item in items:
        await process(item)

asyncio.create_task(process_batch(items))
```

### 2. Context Switching

Each `await` is a potential context switch:

```python
# ❌ SLOW: Too many awaits
async def process():
    for i in range(1000):
        await asyncio.sleep(0)  # Context switch!

# ✅ FASTER: Batch operations
async def process():
    results = []
    for i in range(1000):
        results.append(compute(i))
    await asyncio.sleep(0)  # Single context switch
    return results
```

### 3. Connection Pooling

Reuse connections instead of creating new ones:

```python
# ✅ CORRECT: Connection pool
connector = aiohttp.TCPConnector(limit=100, limit_per_host=10)
session = aiohttp.ClientSession(connector=connector)
```

---

## Testing Async Code

### Pattern 1: Test with pytest-asyncio

```python
import pytest

@pytest.mark.asyncio
async def test_remote_inference():
    """Test remote inference with mocked response."""
    consciousness = DistributedConsciousness()

    # Mock node
    node = Mock()
    node.spec.endpoint_url = "http://localhost:8000"

    # Test
    result = await consciousness._remote_inference("test query", {}, node)

    assert result is not None
```

### Pattern 2: Test with asyncio.run

```python
def test_sync_loop():
    """Test sync loop behavior."""
    async def run_test():
        consciousness = DistributedConsciousness()
        await consciousness.start(node_spec)

        # Wait for one sync cycle
        await asyncio.sleep(0.2)

        await consciousness.stop()

    asyncio.run(run_test())
```

---

## Summary

Sentient Core v4's async architecture provides:

- ✅ **High Concurrency**: Thousands of simultaneous operations
- ✅ **Low Latency**: Non-blocking I/O for real-time responsiveness
- ✅ **Resource Efficiency**: Minimal memory overhead per task
- ✅ **Clean Shutdown**: Proper task cancellation and cleanup
- ✅ **Error Resilience**: Comprehensive error handling with fallbacks

Key takeaways:

1. Always store task references for proper cleanup
2. Use timeouts on all network operations
3. Handle `asyncio.CancelledError` in background tasks
4. Use `async with` for resource management
5. Prefer `asyncio.gather()` for parallel operations
6. Never use blocking operations in async functions

For more information:
- [Python asyncio documentation](https://docs.python.org/3/library/asyncio.html)
- [aiohttp documentation](https://docs.aiohttp.org/)
- Sentient Core architecture: `docs/IMPLEMENTATION_STATUS.md`
