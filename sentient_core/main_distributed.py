"""
Sentient Core v4 - Distributed System Main Orchestrator.

Integrates all components for Pi 5 + Hailo distributed consciousness.
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import Optional

from .core.config import Config
from .hardware.hardware_manager import HardwareManager
from .distributed.consciousness import DistributedConsciousness
from .distributed.node import NodeSpec, NodeRole, NodeCapability
from .distributed.cortana_unified import CortanaUnified
from .sensors.rf_monitor import RFMonitor, DroneDetector
from .sensors.sensor_fusion import SensorFusion
from .sensors.health_monitor import HealthMonitor
from .pixelscape.consciousness_renderer import ConsciousnessRenderer
from .models.llamacpp_interface import LlamaCppInterface

logger = logging.getLogger(__name__)


class SentientCoreDistributed:
    """
    Main orchestrator for distributed Sentient Core system.

    Integrates:
    - Hardware acceleration (Hailo/Coral)
    - Distributed consciousness (Pi5 ↔ Jetson)
    - Cortana unified persona
    - Multi-sensor fusion
    - Real-time visualization
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize distributed system.

        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        if config_path:
            self.config = Config.from_yaml(config_path)
        else:
            self.config = Config.from_yaml("config/pi5_hailo.yaml")

        self.config.ensure_directories()

        # Setup logging
        self._setup_logging()

        # Core components
        self.hardware_manager: Optional[HardwareManager] = None
        self.distributed_consciousness: Optional[DistributedConsciousness] = None
        self.cortana: Optional[CortanaUnified] = None
        self.llm: Optional[LlamaCppInterface] = None

        # Sensors
        self.rf_monitor: Optional[RFMonitor] = None
        self.drone_detector: Optional[DroneDetector] = None
        self.sensor_fusion: Optional[SensorFusion] = None
        self.health_monitor: Optional[HealthMonitor] = None

        # Visualization
        self.consciousness_renderer: Optional[ConsciousnessRenderer] = None

        # State
        self.running = False
        self.initialized = False

        logger.info(f"Sentient Core Distributed initialized: {self.config.system.get('name', 'Unknown')}")

    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = getattr(logging, self.config.system.get('log_level', 'INFO'))
        log_format = self.config.logging.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(
                    Path(self.config.logging.get('file', '~/.sentient_core/logs/sentient_core.log')).expanduser()
                )
            ]
        )

    async def initialize(self):
        """Initialize all components."""
        if self.initialized:
            logger.warning("System already initialized")
            return

        logger.info("=" * 70)
        logger.info("SENTIENT CORE V4 - DISTRIBUTED SYSTEM INITIALIZATION")
        logger.info("=" * 70)

        try:
            # Initialize hardware
            await self._initialize_hardware()

            # Initialize LLM
            await self._initialize_llm()

            # Initialize sensors
            await self._initialize_sensors()

            # Initialize distributed consciousness
            await self._initialize_distributed()

            # Initialize Cortana
            await self._initialize_cortana()

            # Initialize visualization
            await self._initialize_visualization()

            self.initialized = True

            logger.info("=" * 70)
            logger.info("SENTIENT CORE OPERATIONAL")
            logger.info("=" * 70)

        except Exception as e:
            logger.error(f"Initialization failed: {e}", exc_info=True)
            raise

    async def _initialize_hardware(self):
        """Initialize hardware accelerators."""
        logger.info("Initializing hardware accelerators...")

        self.hardware_manager = HardwareManager(self.config)

        # Detect hardware
        detection_results = self.hardware_manager.detect_hardware()
        logger.info(f"Hardware detection: {detection_results}")

        # Initialize detected hardware
        if self.hardware_manager.initialize_all():
            logger.info("✓ Hardware accelerators initialized")
        else:
            logger.warning("⚠ No hardware accelerators available (CPU fallback)")

    async def _initialize_llm(self):
        """Initialize local LLM."""
        logger.info("Initializing local LLM...")

        llm_config = self.config.llm
        model_path = Path(llm_config.get('model_path', '')).expanduser()

        if not model_path.exists():
            logger.warning(f"LLM model not found: {model_path}")
            logger.warning("Cortana will use simulated responses")
            return

        try:
            self.llm = LlamaCppInterface(
                model_path=str(model_path),
                n_ctx=llm_config.get('n_ctx', 2048),
                n_threads=llm_config.get('n_threads', 4),
                n_gpu_layers=llm_config.get('n_gpu_layers', 0),
                temperature=llm_config.get('temperature', 0.7),
                max_tokens=llm_config.get('max_tokens', 512)
            )

            if self.llm.initialize():
                logger.info("✓ Local LLM loaded")
            else:
                logger.warning("⚠ LLM initialization failed")
                self.llm = None

        except Exception as e:
            logger.error(f"LLM initialization error: {e}")
            self.llm = None

    async def _initialize_sensors(self):
        """Initialize sensor systems."""
        logger.info("Initializing sensors...")

        sensors_config = self.config.sensors

        # RF Monitor
        if sensors_config.get('rf_monitor', {}).get('enabled', False):
            self.rf_monitor = RFMonitor(sensors_config.get('rf_monitor', {}))
            self.rf_monitor.initialize()
            self.rf_monitor.start()

            self.drone_detector = DroneDetector(self.rf_monitor)
            logger.info("✓ RF Monitor started")

        # Sensor Fusion
        if sensors_config.get('fusion', {}).get('enabled', True):
            self.sensor_fusion = SensorFusion(sensors_config.get('fusion', {}))
            self.sensor_fusion.start()
            logger.info("✓ Sensor Fusion started")

        # Health Monitor
        if self.config.health_monitor.get('enabled', True):
            self.health_monitor = HealthMonitor(self.config.health_monitor)
            self.health_monitor.start()
            logger.info("✓ Health Monitor started")

    async def _initialize_distributed(self):
        """Initialize distributed consciousness."""
        logger.info("Initializing distributed consciousness...")

        if not self.config.distributed.get('enable', False):
            logger.info("Distributed mode disabled")
            return

        # Create distributed consciousness
        self.distributed_consciousness = DistributedConsciousness(self.config.distributed)

        # Create local node spec
        node_config = self.config.node
        local_node = NodeSpec(
            node_id=node_config.get('node_id', 'pi5-node-001'),
            name=node_config.get('name', 'Pi5 Node'),
            role=NodeRole(node_config.get('role', 'fast_response')),
            capabilities=[NodeCapability(cap) for cap in node_config.get('capabilities', [])],
            hardware=node_config.get('hardware', 'Raspberry Pi 5'),
            max_latency=node_config.get('max_latency', 2.0),
            priority=node_config.get('priority', 1)
        )

        # Start distributed consciousness
        await self.distributed_consciousness.start(local_node)

        # Register remote nodes
        for remote_node_config in self.config.distributed.get('remote_nodes', []):
            remote_spec = NodeSpec(
                node_id=remote_node_config['node_id'],
                name=remote_node_config['name'],
                role=NodeRole(remote_node_config['role']),
                capabilities=[NodeCapability(cap) for cap in remote_node_config['capabilities']],
                endpoint_url=remote_node_config['endpoint_url'],
                hardware=remote_node_config.get('hardware', 'unknown'),
                model=remote_node_config.get('model'),
                max_latency=remote_node_config.get('max_latency', 5.0),
                priority=remote_node_config.get('priority', 1)
            )

            await self.distributed_consciousness.register_remote_node(remote_spec)

        logger.info("✓ Distributed Consciousness operational")

    async def _initialize_cortana(self):
        """Initialize Cortana unified persona."""
        logger.info("Initializing Cortana...")

        if self.distributed_consciousness:
            self.cortana = CortanaUnified(
                self.config.cortana,
                self.distributed_consciousness
            )
            logger.info(f"✓ Cortana initialized (bond: {self.cortana.personality['creator_bond']})")
        else:
            logger.warning("⚠ Cortana requires distributed consciousness")

    async def _initialize_visualization(self):
        """Initialize consciousness visualization."""
        logger.info("Initializing consciousness renderer...")

        pixelscape_config = self.config.pixelscape.get('consciousness_renderer', {})

        if pixelscape_config.get('enabled', False):
            self.consciousness_renderer = ConsciousnessRenderer(pixelscape_config)
            self.consciousness_renderer.start()
            logger.info("✓ Consciousness Renderer started")

    async def run(self):
        """Main execution loop."""
        await self.initialize()

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        self.running = True

        logger.info("Entering main loop...")

        try:
            while self.running:
                # Update visualization with system state
                await self._update_visualization()

                # Update sensor fusion
                await self._update_sensors()

                # Process any pending tasks
                await asyncio.sleep(0.1)

        except Exception as e:
            logger.error(f"Runtime error: {e}", exc_info=True)
        finally:
            await self.shutdown()

    async def _update_visualization(self):
        """Update consciousness visualization."""
        if not self.consciousness_renderer:
            return

        try:
            # Get emotional state from Cortana
            emotional_state = self.cortana.get_emotional_state() if self.cortana else {'state': 'idle', 'thinking_intensity': 0.0}

            # Get health score
            health_score = self.health_monitor.get_health_score() if self.health_monitor else 1.0

            # Update renderer
            self.consciousness_renderer.update_state({
                'emotional_state': emotional_state['state'],
                'thinking_intensity': emotional_state.get('thinking_intensity', 0.5),
                'health_score': health_score
            })

        except Exception as e:
            logger.debug(f"Visualization update error: {e}")

    async def _update_sensors(self):
        """Update sensor fusion with latest data."""
        if not self.sensor_fusion:
            return

        try:
            # Update RF data
            if self.rf_monitor:
                detections = self.rf_monitor.get_detections()
                if detections:
                    self.sensor_fusion.update_sensor('rf', {'detections': detections})

            # Update health data
            if self.health_monitor:
                health = self.health_monitor.get_health()
                self.sensor_fusion.update_sensor('health', health)

        except Exception as e:
            logger.debug(f"Sensor update error: {e}")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}. Initiating shutdown...")
        self.running = False

    async def shutdown(self):
        """Shutdown all systems gracefully."""
        logger.info("Shutting down Sentient Core...")

        self.running = False

        # Stop sensors
        if self.rf_monitor:
            self.rf_monitor.stop()
        if self.sensor_fusion:
            self.sensor_fusion.stop()
        if self.health_monitor:
            self.health_monitor.stop()

        # Stop visualization
        if self.consciousness_renderer:
            self.consciousness_renderer.stop()

        # Stop distributed consciousness
        if self.distributed_consciousness:
            await self.distributed_consciousness.stop()

        # Cleanup hardware
        if self.hardware_manager:
            self.hardware_manager.cleanup_all()

        # Cleanup LLM
        if self.llm:
            self.llm.shutdown()

        logger.info("Sentient Core shutdown complete")


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Sentient Core v4 - Distributed System")
    parser.add_argument('--config', type=str, help='Path to configuration file')
    args = parser.parse_args()

    # Create and run system
    system = SentientCoreDistributed(config_path=args.config)

    try:
        await system.run()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
