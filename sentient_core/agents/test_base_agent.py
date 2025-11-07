"""
Tests for the BaseAgent class.
"""

import unittest
from sentient_core.agents.base_agent import BaseAgent, AgentCapability

class MockAgent(BaseAgent):
    """A mock agent for testing."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.capabilities = self.get_capabilities()

    def get_capabilities(self):
        return [AgentCapability("test_capability", "A test capability")]

    def process_task(self, task, context=None):
        return {"status": "completed"}

class TestBaseAgent(unittest.TestCase):
    """Test suite for the BaseAgent."""

    def test_can_handle_active_vs_inactive(self):
        """Test that can_handle respects the agent's active status."""
        agent = MockAgent()

        # Agent is inactive by default
        self.assertFalse(agent.can_handle("test_capability"))

        # Agent is active
        agent.activate()
        self.assertTrue(agent.can_handle("test_capability"))

        # Agent is inactive again
        agent.deactivate()
        self.assertFalse(agent.can_handle("test_capability"))

if __name__ == "__main__":
    unittest.main()
