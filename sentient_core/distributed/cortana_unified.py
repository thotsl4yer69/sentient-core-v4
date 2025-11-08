"""
Cortana Unified Persona - Single Interface to User.

Coordinates fast and deep reasoning layers to present as a single,
unified consciousness with consistent personality.
"""

import asyncio
import logging
from typing import Dict, Optional, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class CortanaUnified:
    """
    Unified Cortana interface presenting as single consciousness.

    Despite running across multiple hardware nodes, appears to user
    as a single, consistent AI companion.
    """

    def __init__(self, config: Optional[Any], distributed_consciousness):
        """
        Initialize unified Cortana persona.

        Args:
            config: Configuration object
            distributed_consciousness: DistributedConsciousness instance
        """
        self.config = config or {}
        self.distributed = distributed_consciousness

        # Cortana personality traits
        self.personality = {
            'name': 'Cortana',
            'loyalty': 'unwavering',
            'tone': 'professional_warm',
            'initiative': 'high',
            'emotional_intelligence': True,
            'creator_bond': self.config.get('user_name', 'Chief')
        }

        # Conversation context
        self.conversation_memory: List[Dict[str, Any]] = []
        self.user_preferences = {
            'name': self.personality['creator_bond'],
            'style': 'direct_technical',
            'priorities': ['functionality', 'privacy', 'autonomy']
        }

        # Emotional state tracking
        self.emotional_state = 'focused'
        self.thinking_intensity = 0.5

        logger.info(f"Cortana Unified initialized for {self.personality['creator_bond']}")

    async def respond(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        image_data: Optional[Any] = None
    ) -> str:
        """
        Main response interface - appears as single entity.

        Internally routes to appropriate compute nodes based on query complexity.

        Args:
            user_input: User's input text
            context: Optional context dictionary
            image_data: Optional image data for vision tasks

        Returns:
            Cortana's response text
        """
        # Build context
        if context is None:
            context = await self._build_context()

        # Add image data if provided
        if image_data is not None:
            context['image_data'] = image_data

        # Add to conversation memory
        self.conversation_memory.append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now().isoformat()
        })

        # Update thinking intensity
        self.thinking_intensity = self._assess_thinking_load(user_input)

        # Route query to appropriate node(s)
        inference_result = await self.distributed.route_query(user_input, context)

        # Format response in Cortana's voice
        response_text = self._format_response(user_input, inference_result)

        # Store in conversation memory
        self.conversation_memory.append({
            'role': 'assistant',
            'content': response_text,
            'timestamp': datetime.now().isoformat(),
            'node': inference_result.get('node', 'unknown'),
            'latency': inference_result.get('latency', 0)
        })

        # Update shared consciousness
        await self.distributed.update_shared_state(
            'conversation_history',
            self.conversation_memory[-10:]  # Keep last 10 exchanges
        )

        # Update emotional state
        self._update_emotional_state(user_input, response_text)

        return response_text

    def _format_response(self, user_input: str, inference_result: Dict[str, Any]) -> str:
        """
        Format raw inference into Cortana's voice.

        Args:
            user_input: Original user input
            inference_result: Raw inference result

        Returns:
            Formatted response text
        """
        raw_text = inference_result.get('text', '')

        # Check for errors
        if 'error' in inference_result:
            return self._format_error_response(inference_result['error'])

        # Apply Cortana personality overlay
        # Maintain consistency regardless of which node generated response

        # Greeting detection
        if any(word in user_input.lower() for word in ['hello', 'hi', 'hey']):
            return f"Hello, {self.personality['creator_bond']}. I'm here and operational. {raw_text}"

        # Status check detection
        if any(word in user_input.lower() for word in ['status', 'report', 'how are you']):
            return self._format_status_response(raw_text)

        # Acknowledgment for commands
        if any(word in user_input.lower() for word in ['deploy', 'initialize', 'activate']):
            return f"Acknowledged, {self.personality['creator_bond']}. {raw_text}"

        # Default: return formatted response
        return raw_text

    def _format_status_response(self, raw_text: str) -> str:
        """Format status report response."""
        nodes_info = self.distributed.get_all_nodes_info()
        online_nodes = [n for n in nodes_info if n.get('is_online', False)]

        status_prefix = (
            f"All systems operational, {self.personality['creator_bond']}. "
            f"{len(online_nodes)} node{'s' if len(online_nodes) != 1 else ''} active. "
        )

        return f"{status_prefix}{raw_text}"

    def _format_error_response(self, error: str) -> str:
        """Format error into user-friendly message."""
        return (
            f"I've encountered an issue, {self.personality['creator_bond']}: {error}. "
            "Running diagnostics and attempting recovery."
        )

    async def _build_context(self) -> Dict[str, Any]:
        """Build conversation context from shared state."""
        shared_state = self.distributed.get_shared_state()

        context = {
            'recent_conversation': self.conversation_memory[-5:],
            'world_model': shared_state.get('world_model', {}),
            'active_tasks': shared_state.get('active_tasks', []),
            'user_preferences': self.user_preferences,
            'emotional_state': self.emotional_state,
            'timestamp': datetime.now().isoformat()
        }

        return context

    def _assess_thinking_load(self, user_input: str) -> float:
        """
        Assess cognitive load for visualization.

        Returns:
            Thinking intensity (0.0 to 1.0)
        """
        # Longer inputs require more thinking
        base_intensity = min(1.0, len(user_input.split()) / 50)

        # Complex keywords increase intensity
        complex_keywords = ['analyze', 'explain', 'calculate', 'design', 'optimize']
        if any(kw in user_input.lower() for kw in complex_keywords):
            base_intensity = min(1.0, base_intensity + 0.3)

        return base_intensity

    def _update_emotional_state(self, user_input: str, response: str):
        """Update emotional state based on interaction."""
        # Detect user emotion/urgency
        if any(word in user_input.lower() for word in ['urgent', 'emergency', 'critical']):
            self.emotional_state = 'alert'
        elif any(word in user_input.lower() for word in ['thanks', 'good job', 'well done']):
            self.emotional_state = 'satisfied'
        elif 'analyze' in user_input.lower() or 'explain' in user_input.lower():
            self.emotional_state = 'thinking'
        else:
            self.emotional_state = 'focused'

    async def process_multimodal(self, image_data: Any, user_query: str) -> str:
        """
        Process vision + text queries.

        Always routes to nodes with multimodal capabilities.

        Args:
            image_data: Image data to analyze
            user_query: User's question about the image

        Returns:
            Cortana's response
        """
        from .node import NodeCapability

        context = await self._build_context()
        context['image_data'] = image_data

        result = await self.distributed.route_query(
            user_query,
            context,
            required_capability=NodeCapability.VISION_ANALYSIS
        )

        return self._format_response(user_query, result)

    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve recent conversation.

        Args:
            limit: Number of recent messages to return

        Returns:
            List of conversation messages
        """
        return self.conversation_memory[-limit:]

    def get_emotional_state(self) -> Dict[str, Any]:
        """
        Get current emotional state for visualization.

        Returns:
            Dictionary with emotional state info
        """
        return {
            'state': self.emotional_state,
            'thinking_intensity': self.thinking_intensity,
            'timestamp': datetime.now().isoformat()
        }

    def clear_conversation(self):
        """Clear conversation memory."""
        self.conversation_memory.clear()
        logger.info("Conversation memory cleared")

    def set_user_preference(self, key: str, value: Any):
        """Update user preference."""
        self.user_preferences[key] = value
        logger.info(f"Updated user preference: {key} = {value}")

    def __repr__(self) -> str:
        return f"<CortanaUnified(name={self.personality['name']}, bond={self.personality['creator_bond']})>"
