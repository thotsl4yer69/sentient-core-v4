"""
Shared Constants for Sentient Core v4.

Centralizes configuration keys, status codes, and common literals
to prevent typo-related bugs and improve maintainability.
"""

# ============================================================================
# System Constants
# ============================================================================

SYSTEM_NAME = "Sentient Core v4"
SYSTEM_VERSION = "4.0.0"

# ============================================================================
# Configuration Keys
# ============================================================================

# System Config Keys
CONFIG_SYSTEM = "system"
CONFIG_SYSTEM_NAME = "name"
CONFIG_SYSTEM_VERSION = "version"
CONFIG_SYSTEM_PLATFORM = "platform"
CONFIG_SYSTEM_ROLE = "role"
CONFIG_SYSTEM_LOG_LEVEL = "log_level"

# Node Config Keys
CONFIG_NODE = "node"
CONFIG_NODE_ID = "node_id"
CONFIG_NODE_NAME = "name"
CONFIG_NODE_ROLE = "role"
CONFIG_NODE_CAPABILITIES = "capabilities"
CONFIG_NODE_HARDWARE = "hardware"
CONFIG_NODE_MAX_LATENCY = "max_latency"
CONFIG_NODE_PRIORITY = "priority"

# Distributed Config Keys
CONFIG_DISTRIBUTED = "distributed"
CONFIG_DISTRIBUTED_ENABLE = "enable"
CONFIG_DISTRIBUTED_SYNC_INTERVAL = "sync_interval"
CONFIG_DISTRIBUTED_ENABLE_DISCOVERY = "enable_discovery"
CONFIG_DISTRIBUTED_REMOTE_NODES = "remote_nodes"
CONFIG_DISTRIBUTED_HEARTBEAT_INTERVAL = "heartbeat_interval"
CONFIG_DISTRIBUTED_HEARTBEAT_TIMEOUT = "heartbeat_timeout"

# Hardware Config Keys
CONFIG_HARDWARE = "hardware"
CONFIG_HARDWARE_HAILO = "hailo"
CONFIG_HARDWARE_CORAL = "coral"
CONFIG_HARDWARE_GPIO = "gpio"
CONFIG_HARDWARE_ENABLED = "enabled"
CONFIG_HARDWARE_DEVICE_ID = "device_id"
CONFIG_HARDWARE_MODELS = "models"

# LLM Config Keys
CONFIG_LLM = "llm"
CONFIG_LLM_PROVIDER = "provider"
CONFIG_LLM_MODEL_PATH = "model_path"
CONFIG_LLM_N_CTX = "n_ctx"
CONFIG_LLM_N_THREADS = "n_threads"
CONFIG_LLM_N_GPU_LAYERS = "n_gpu_layers"
CONFIG_LLM_TEMPERATURE = "temperature"
CONFIG_LLM_MAX_TOKENS = "max_tokens"

# Cortana Config Keys
CONFIG_CORTANA = "cortana"
CONFIG_CORTANA_NAME = "name"
CONFIG_CORTANA_USER_NAME = "user_name"
CONFIG_CORTANA_LOYALTY_MODE = "loyalty_mode"
CONFIG_CORTANA_EMOTIONAL_INTELLIGENCE = "emotional_intelligence"
CONFIG_CORTANA_TONE = "tone"

# Sensors Config Keys
CONFIG_SENSORS = "sensors"
CONFIG_SENSORS_RF_MONITOR = "rf_monitor"
CONFIG_SENSORS_CAMERA = "camera"
CONFIG_SENSORS_FUSION = "fusion"

# Health Monitor Config Keys
CONFIG_HEALTH_MONITOR = "health_monitor"
CONFIG_HEALTH_ENABLED = "enabled"
CONFIG_HEALTH_UPDATE_INTERVAL = "update_interval"
CONFIG_HEALTH_CPU_THRESHOLD = "cpu_threshold"
CONFIG_HEALTH_MEMORY_THRESHOLD = "memory_threshold"
CONFIG_HEALTH_DISK_THRESHOLD = "disk_threshold"
CONFIG_HEALTH_TEMP_THRESHOLD = "temp_threshold"

# Pixelscape Config Keys
CONFIG_PIXELSCAPE = "pixelscape"
CONFIG_PIXELSCAPE_CONSCIOUSNESS_RENDERER = "consciousness_renderer"

# Logging Config Keys
CONFIG_LOGGING = "logging"
CONFIG_LOGGING_LEVEL = "level"
CONFIG_LOGGING_FORMAT = "format"
CONFIG_LOGGING_FILE = "file"

# Storage Config Keys
CONFIG_STORAGE = "storage"
CONFIG_STORAGE_MODELS_DIR = "models_dir"
CONFIG_STORAGE_DATA_DIR = "data_dir"
CONFIG_STORAGE_LOGS_DIR = "logs_dir"
CONFIG_STORAGE_CACHE_DIR = "cache_dir"

# ============================================================================
# Node Roles
# ============================================================================

ROLE_FAST_RESPONSE = "fast_response"
ROLE_DEEP_REASONING = "deep_reasoning"
ROLE_COORDINATOR = "coordinator"
ROLE_MULTIMODAL = "multimodal"

# ============================================================================
# Node Capabilities
# ============================================================================

CAPABILITY_TEXT_GENERATION = "text_generation"
CAPABILITY_FAST_INFERENCE = "fast_inference"
CAPABILITY_DEEP_REASONING = "deep_reasoning"
CAPABILITY_MULTIMODAL = "multimodal"
CAPABILITY_VISION_ANALYSIS = "vision_analysis"
CAPABILITY_CODE_GENERATION = "code_generation"
CAPABILITY_RF_MONITORING = "rf_monitoring"
CAPABILITY_SENSOR_FUSION = "sensor_fusion"

# ============================================================================
# Node Status
# ============================================================================

STATUS_ONLINE = "online"
STATUS_OFFLINE = "offline"
STATUS_DEGRADED = "degraded"
STATUS_INITIALIZING = "initializing"
STATUS_ERROR = "error"

# ============================================================================
# Query Complexity Levels
# ============================================================================

COMPLEXITY_SIMPLE = "simple"
COMPLEXITY_MODERATE = "moderate"
COMPLEXITY_COMPLEX = "complex"
COMPLEXITY_VISION = "vision"

# ============================================================================
# Emotional States
# ============================================================================

EMOTION_FOCUSED = "focused"
EMOTION_ALERT = "alert"
EMOTION_THINKING = "thinking"
EMOTION_CONCERNED = "concerned"
EMOTION_IDLE = "idle"
EMOTION_PROCESSING = "processing"
EMOTION_CONFIDENT = "confident"

# ============================================================================
# Shared State Keys
# ============================================================================

STATE_CONVERSATION_HISTORY = "conversation_history"
STATE_USER_CONTEXT = "user_context"
STATE_ACTIVE_TASKS = "active_tasks"
STATE_WORLD_MODEL = "world_model"
STATE_EMOTIONAL_STATE = "emotional_state"
STATE_LAST_SYNC = "last_sync"
STATE_LAST_UPDATE = "last_update"
STATE_NODE_STATUS_CHANGE = "node_status_change"

# ============================================================================
# API Endpoints
# ============================================================================

ENDPOINT_HEALTH = "/health"
ENDPOINT_SYNC = "/sync"
ENDPOINT_INFERENCE = "/inference"
ENDPOINT_PING = "/ping"
ENDPOINT_PONG = "/pong"
ENDPOINT_NODES = "/nodes"
ENDPOINT_STATUS = "/status"

# ============================================================================
# Hardware Types
# ============================================================================

HARDWARE_CPU = "cpu"
HARDWARE_GPU = "gpu"
HARDWARE_HAILO = "hailo"
HARDWARE_CORAL = "coral"
HARDWARE_JETSON = "jetson"
HARDWARE_NPU = "npu"

# ============================================================================
# Default Values
# ============================================================================

# Timing defaults (in seconds)
DEFAULT_SYNC_INTERVAL = 0.1  # 10Hz
DEFAULT_HEARTBEAT_INTERVAL = 5.0
DEFAULT_HEARTBEAT_TIMEOUT = 15.0
DEFAULT_UPDATE_INTERVAL = 5.0
DEFAULT_MAX_LATENCY = 2.0

# LLM defaults
DEFAULT_N_CTX = 2048
DEFAULT_N_THREADS = 4
DEFAULT_N_GPU_LAYERS = 0
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 512

# Sensor defaults
DEFAULT_SAMPLE_RATE = 2.4e6
DEFAULT_CENTER_FREQUENCY = 2.4e9
DEFAULT_GAIN = 30
DEFAULT_FUSION_RATE = 20  # Hz
DEFAULT_MAX_SENSOR_HISTORY = 100

# Health thresholds
DEFAULT_CPU_THRESHOLD = 90  # %
DEFAULT_MEMORY_THRESHOLD = 90  # %
DEFAULT_DISK_THRESHOLD = 90  # %
DEFAULT_TEMP_THRESHOLD = 80  # °C

# Display defaults
DEFAULT_DISPLAY_WIDTH = 64
DEFAULT_DISPLAY_HEIGHT = 64
DEFAULT_RENDER_FPS = 30

# ============================================================================
# Log Messages
# ============================================================================

LOG_SYSTEM_INITIALIZED = "Sentient Core Distributed initialized"
LOG_SYSTEM_OPERATIONAL = "SENTIENT CORE OPERATIONAL"
LOG_SYSTEM_SHUTDOWN = "Sentient Core shutdown complete"
LOG_HARDWARE_INITIALIZED = "Hardware accelerators initialized"
LOG_LLM_LOADED = "Local LLM loaded"
LOG_DISTRIBUTED_OPERATIONAL = "Distributed Consciousness operational"
LOG_NODE_REGISTERED = "Registered remote node"
LOG_NODE_STATUS_CHANGED = "Node status changed"

# ============================================================================
# Error Messages
# ============================================================================

ERROR_NO_SUITABLE_NODE = "No suitable node available"
ERROR_SYSTEM_UNAVAILABLE = "System temporarily unavailable"
ERROR_INVALID_TARGET_NODE = "Invalid target node"
ERROR_REMOTE_INFERENCE_FAILED = "Remote inference failed"
ERROR_SYNC_FAILED = "Sync failed"
ERROR_PING_FAILED = "Ping failed"
ERROR_INITIALIZATION_FAILED = "Initialization failed"
ERROR_MODEL_NOT_FOUND = "Model not found"
ERROR_HARDWARE_NOT_DETECTED = "Hardware not detected"

# ============================================================================
# Response Keys
# ============================================================================

RESPONSE_TEXT = "text"
RESPONSE_NODE = "node"
RESPONSE_LATENCY = "latency"
RESPONSE_CONFIDENCE = "confidence"
RESPONSE_ERROR = "error"
RESPONSE_STATUS = "status"
RESPONSE_TIMESTAMP = "timestamp"

# ============================================================================
# Prompt Templates
# ============================================================================

PROMPT_INTENT_CLASSIFICATION = """Classify the following user query into ONE of these categories based on complexity and intent:

Categories:
- simple: Greetings, status checks, yes/no, acknowledgments (fast response needed)
- moderate: General questions, basic information retrieval
- complex: Deep analysis, reasoning, calculations, comparisons, design tasks
- vision: Queries about images, visual content, what can be seen

Query: "{query}"

Respond with ONLY the category name (simple/moderate/complex/vision):"""

# ============================================================================
# File Extensions
# ============================================================================

EXT_HAILO_MODEL = ".hef"
EXT_CORAL_MODEL = ".tflite"
EXT_GGUF_MODEL = ".gguf"
EXT_YAML_CONFIG = ".yaml"
EXT_JSON_CONFIG = ".json"
