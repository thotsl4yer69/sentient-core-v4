"""
Main Sentient Agent implementation.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from .config import Config
from ..agents.team import AgentTeam
from ..models.model_manager import ModelManager
from ..voice.voice_processor import VoiceProcessor
from ..pixelscape.vision_system import VisionSystem
from .reasoning.reasoning_engine import ReasoningEngine
from .memory.memory_system import MemorySystem
from .perception.perception_engine import PerceptionEngine
from .action.action_executor import ActionExecutor


logger = logging.getLogger(__name__)


class SentientAgent:
    """
    Main Sentient Agent class that coordinates all cognitive systems.

    This is the primary interface for interacting with Sentient Core v4.
    It orchestrates reasoning, memory, perception, and action systems.
    """

    def __init__(self, config_path: Optional[str] = None, config: Optional[Config] = None):
        """
        Initialize the Sentient Agent.

        Args:
            config_path: Path to configuration file
            config: Config object (if not loading from file)
        """
        # Load configuration
        if config:
            self.config = config
        elif config_path:
            self.config = Config.from_yaml(config_path)
        else:
            self.config = Config.from_yaml("config/default.yaml")

        # Ensure directories exist
        self.config.ensure_directories()

        # Initialize components
        self.model_manager: Optional[ModelManager] = None
        self.reasoning_engine: Optional[ReasoningEngine] = None
        self.memory_system: Optional[MemorySystem] = None
        self.perception_engine: Optional[PerceptionEngine] = None
        self.action_executor: Optional[ActionExecutor] = None
        self.agent_team: Optional[AgentTeam] = None
        self.voice_processor: Optional[VoiceProcessor] = None
        self.vision_system: Optional[VisionSystem] = None

        # State
        self.initialized = False
        self.running = False

        logger.info(f"Sentient Agent created with model: {self.config.model}")

    def initialize(self):
        """Initialize all agent systems."""
        if self.initialized:
            logger.warning("Agent already initialized")
            return

        logger.info("Initializing Sentient Agent...")

        # Initialize model manager
        self.model_manager = ModelManager(self.config)
        self.model_manager.initialize()

        # Initialize core systems
        if self.config.enable_reasoning:
            self.reasoning_engine = ReasoningEngine(self.config, self.model_manager)
            logger.info("Reasoning engine initialized")

        if self.config.enable_memory:
            self.memory_system = MemorySystem(self.config)
            self.memory_system.initialize()
            logger.info("Memory system initialized")

        # Initialize perception
        self.perception_engine = PerceptionEngine(self.config)
        logger.info("Perception engine initialized")

        # Initialize action system
        self.action_executor = ActionExecutor(self.config)
        logger.info("Action executor initialized")

        # Initialize multi-agent system
        if self.config.enable_multi_agent:
            self.agent_team = AgentTeam(self.config, self.model_manager)
            self.agent_team.initialize()
            logger.info("Agent team initialized")

        # Initialize voice processing
        if self.config.enable_voice:
            self.voice_processor = VoiceProcessor(self.config)
            self.voice_processor.initialize()
            logger.info("Voice processor initialized")

        # Initialize vision system (Pixelscape)
        if self.config.enable_vision:
            self.vision_system = VisionSystem(self.config)
            self.vision_system.initialize()
            logger.info("Vision system (Pixelscape) initialized")

        self.initialized = True
        logger.info("Sentient Agent fully initialized and ready")

    def process(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Process input and generate response.

        Args:
            input_data: Input to process (text, audio, image, etc.)
            context: Optional context dictionary

        Returns:
            Processed response
        """
        if not self.initialized:
            raise RuntimeError("Agent not initialized. Call initialize() first.")

        logger.debug(f"Processing input: {type(input_data)}")

        # Perceive input
        perceived = self.perception_engine.process(input_data)

        # Store in memory
        if self.memory_system:
            self.memory_system.store(perceived)

        # Reason about input
        if self.reasoning_engine:
            reasoning_result = self.reasoning_engine.reason(perceived, context)
        else:
            reasoning_result = perceived

        # Retrieve relevant memories
        if self.memory_system:
            relevant_memories = self.memory_system.retrieve(perceived)
            reasoning_result['memories'] = relevant_memories

        # Generate response using model
        response = self.model_manager.generate(reasoning_result)

        return response

    async def process_async(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """Async version of process()."""
        return await asyncio.to_thread(self.process, input_data, context)

    def process_voice(self, audio_data: Any) -> str:
        """Process voice input and return text response."""
        if not self.voice_processor:
            raise RuntimeError("Voice processing not enabled")

        # Transcribe audio to text
        text = self.voice_processor.transcribe(audio_data)

        # Process text
        response = self.process(text)

        return response

    def process_image(self, image_data: Any, prompt: Optional[str] = None) -> str:
        """Process image input using Pixelscape vision system."""
        if not self.vision_system:
            raise RuntimeError("Vision processing not enabled")

        # Analyze image
        analysis = self.vision_system.analyze(image_data, prompt)

        # Process with reasoning
        response = self.process(analysis)

        return response

    def create_team_task(self, task: str, num_agents: int = 3) -> Dict[str, Any]:
        """
        Create a multi-agent team task.

        Args:
            task: Task description
            num_agents: Number of agents to create

        Returns:
            Task result from team coordination
        """
        if not self.agent_team:
            raise RuntimeError("Multi-agent system not enabled")

        return self.agent_team.execute_task(task, num_agents)

    def start(self):
        """Start the agent in continuous mode."""
        if not self.initialized:
            self.initialize()

        self.running = True
        logger.info("Sentient Agent started")

    def stop(self):
        """Stop the agent."""
        self.running = False
        logger.info("Sentient Agent stopped")

    def shutdown(self):
        """Shutdown and cleanup all systems."""
        logger.info("Shutting down Sentient Agent...")

        if self.memory_system:
            self.memory_system.shutdown()

        if self.model_manager:
            self.model_manager.shutdown()

        self.initialized = False
        self.running = False

        logger.info("Sentient Agent shutdown complete")

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            'initialized': self.initialized,
            'running': self.running,
            'config': {
                'model': self.config.model,
                'device': self.config.device,
            },
            'components': {
                'reasoning': self.reasoning_engine is not None,
                'memory': self.memory_system is not None,
                'multi_agent': self.agent_team is not None,
                'voice': self.voice_processor is not None,
                'vision': self.vision_system is not None,
            }
        }
