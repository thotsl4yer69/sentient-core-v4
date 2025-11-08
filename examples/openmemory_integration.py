#!/usr/bin/env python3
"""
OpenMemory Integration Example for Sentient Core v4

This example demonstrates how to use OpenMemory as the memory backend
for Sentient Core v4, showcasing the brain-inspired memory system with
multi-sector organization, automatic decay, and advanced retrieval.
"""

import sys
from pathlib import Path

# Add parent directory to path to import sentient_core
sys.path.insert(0, str(Path(__file__).parent.parent))

from sentient_core.core.config import Config
from sentient_core.core.memory.memory_system import MemorySystem
import time


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def basic_memory_operations():
    """Demonstrate basic memory operations with OpenMemory."""
    print_section("Basic Memory Operations")

    # Create configuration with OpenMemory backend
    config_dict = {
        'memory.backend': 'openmemory',
        'openmemory.url': 'http://localhost:8080',
        'openmemory.user_id': 'demo_user',
        'openmemory.api_key': ''
    }
    config = Config(config_dict)

    # Initialize memory system
    memory = MemorySystem(config)
    memory.initialize()

    print("✓ Memory system initialized with OpenMemory backend\n")

    # Store memories of different types
    print("Storing memories across different sectors...")

    # 1. Episodic memory (events)
    memory.store(
        data="Met with the AI research team to discuss the new project",
        memory_type='episodic',
        metadata={
            'tags': ['meeting', 'research', 'ai'],
            'importance': 0.7,
            'location': 'conference_room_a'
        }
    )
    print("✓ Stored episodic memory (event)")

    # 2. Semantic memory (facts)
    memory.store(
        data="Python is a high-level, interpreted programming language with dynamic typing",
        memory_type='semantic',
        metadata={
            'tags': ['programming', 'python', 'knowledge'],
            'importance': 0.8,
            'category': 'programming_languages'
        }
    )
    print("✓ Stored semantic memory (fact)")

    # 3. Procedural memory (habits/procedures)
    memory.store(
        data="Morning routine: wake up at 6am, exercise for 30 minutes, have breakfast, review daily goals",
        memory_type='procedural',
        metadata={
            'tags': ['routine', 'morning', 'habits'],
            'importance': 0.6,
            'frequency': 'daily'
        }
    )
    print("✓ Stored procedural memory (habit)")

    # 4. Emotional memory
    memory.store(
        data="Feeling excited and motivated about the breakthrough in the AI model training",
        memory_type='emotional',
        metadata={
            'tags': ['excitement', 'motivation', 'achievement'],
            'importance': 0.75,
            'sentiment': 'positive'
        }
    )
    print("✓ Stored emotional memory (sentiment)")

    # 5. Short-term memory (maps to episodic in OpenMemory)
    memory.store(
        data="Just received email from project manager about tomorrow's deadline",
        memory_type='short_term',
        metadata={
            'tags': ['email', 'deadline', 'urgent'],
            'importance': 0.9
        }
    )
    print("✓ Stored short-term memory")

    print("\n✓ Successfully stored 5 memories across different sectors\n")

    return memory


def query_memories(memory):
    """Demonstrate memory retrieval with semantic search."""
    print_section("Memory Retrieval (Semantic Search)")

    # Query 1: Find memories about AI research
    print("Query 1: 'AI research and development'")
    results = memory.retrieve(
        query="AI research and development",
        memory_type='all',
        limit=5,
        min_score=0.3
    )

    print(f"Found {len(results)} relevant memories:\n")
    for i, mem in enumerate(results, 1):
        content = mem.get('content', '')[:80] + '...' if len(mem.get('content', '')) > 80 else mem.get('content', '')
        score = mem.get('score', 0.0)
        sector = mem.get('sector', 'unknown')
        print(f"{i}. [{sector}] Score: {score:.3f}")
        print(f"   {content}\n")

    # Query 2: Find procedural memories
    print("\nQuery 2: 'daily routine'")
    results = memory.retrieve(
        query="daily routine",
        memory_type='procedural',
        limit=3
    )

    print(f"Found {len(results)} procedural memories:\n")
    for i, mem in enumerate(results, 1):
        content = mem.get('content', '')
        score = mem.get('score', 0.0)
        print(f"{i}. Score: {score:.3f}")
        print(f"   {content}\n")

    # Query 3: Find emotional memories
    print("\nQuery 3: 'positive feelings and excitement'")
    results = memory.retrieve(
        query="positive feelings and excitement",
        memory_type='emotional',
        limit=3
    )

    print(f"Found {len(results)} emotional memories:\n")
    for i, mem in enumerate(results, 1):
        content = mem.get('content', '')
        score = mem.get('score', 0.0)
        print(f"{i}. Score: {score:.3f}")
        print(f"   {content}\n")


def memory_statistics(memory):
    """Display memory system statistics."""
    print_section("Memory Statistics")

    stats = memory.get_stats()

    print(f"Backend: {stats.get('backend')}")
    print(f"Status: {stats.get('status')}")
    print(f"Total Memories: {stats.get('total_memories', 0)}")
    print(f"User ID: {stats.get('user_id')}\n")

    # Display sector statistics if available
    sectors = stats.get('sectors', {})
    if sectors and 'sectors' in sectors:
        print("Memories by Sector:")
        for sector_name, sector_info in sectors['sectors'].items():
            count = sector_info.get('count', 0)
            decay = sector_info.get('decay_lambda', 0)
            print(f"  {sector_name}: {count} memories (decay rate: {decay})")


def advanced_features(memory):
    """Demonstrate advanced OpenMemory features."""
    print_section("Advanced Features")

    # Access the OpenMemory backend directly for advanced features
    if memory.openmemory_backend is None:
        print("OpenMemory backend not available")
        return

    backend = memory.openmemory_backend
    client = backend.client

    # 1. Memory reinforcement
    print("1. Memory Reinforcement")
    print("   Reinforcing important memories to prevent decay...\n")

    # Get some memories to reinforce
    results = memory.retrieve("AI research", limit=1)
    if results:
        memory_id = results[0].get('id')
        success = backend.reinforce(memory_id, boost=0.3)
        if success:
            print(f"   ✓ Reinforced memory {memory_id[:8]}... with 0.3 boost\n")

    # 2. Sector information
    print("2. Brain Sector Information")
    try:
        sector_info = client.get_sectors()
        print("   Available cognitive sectors:")
        for sector, info in sector_info.get('sectors', {}).items():
            print(f"   - {sector}: {info.get('description', 'N/A')}")
    except Exception as e:
        print(f"   Error getting sector info: {e}")

    print()

    # 3. User summary (if enabled)
    print("3. User Summary")
    try:
        summary = client.get_user_summary(backend.user_id)
        print(f"   User: {summary.get('user_id')}")
        print(f"   Summary: {summary.get('summary', 'No summary available')}")
        print(f"   Reflections: {summary.get('reflection_count', 0)}")
    except Exception as e:
        print(f"   Error getting user summary: {e}")


def cleanup(memory):
    """Clean up and shutdown."""
    print_section("Cleanup")

    print("Shutting down memory system...")
    memory.shutdown()
    print("✓ Memory system shut down successfully")


def main():
    """Main demonstration function."""
    print("\n" + "="*60)
    print("  OpenMemory Integration Demo - Sentient Core v4")
    print("="*60)

    print("\nThis demo showcases the OpenMemory brain-inspired memory system")
    print("integrated with Sentient Core v4.\n")

    print("Requirements:")
    print("- OpenMemory backend must be running on http://localhost:8080")
    print("- Start with: cd openmemory-backend && npm install && npm start")
    print("\nPress Enter to continue or Ctrl+C to exit...")

    try:
        input()
    except KeyboardInterrupt:
        print("\nDemo cancelled.")
        return

    try:
        # Run demonstrations
        memory = basic_memory_operations()
        time.sleep(1)  # Give OpenMemory time to index

        query_memories(memory)
        memory_statistics(memory)
        advanced_features(memory)
        cleanup(memory)

        print("\n" + "="*60)
        print("  Demo Complete!")
        print("="*60)
        print("\nNext steps:")
        print("- Check the OpenMemory dashboard at http://localhost:3000")
        print("- Explore the memory visualization and statistics")
        print("- Try different query patterns and memory types")
        print("- Experiment with memory decay and reinforcement\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure the OpenMemory backend is running:")
        print("  cd openmemory-backend")
        print("  npm install")
        print("  npm start\n")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
