#!/bin/bash
#
# Sentient Core v4 - Jetson Orin Nano API Server Setup
#
# This script sets up the Jetson as a deep reasoning node for
# distributed consciousness with multimodal capabilities.
#

set -e

echo "================================================================"
echo "Sentient Core v4 - Jetson Orin API Server Setup"
echo "================================================================"
echo ""

GREEN='\033[0;32m'
NC='\033[0m'

function print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

# Update system
print_status "Updating system..."
sudo apt update && sudo apt upgrade -y

# Install dependencies
print_status "Installing system dependencies..."
sudo apt install -y \
    python3-pip python3-venv \
    build-essential \
    git

# Create directory
INSTALL_DIR="$HOME/sentient_core_jetson"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Create virtual environment
VENV_DIR="$INSTALL_DIR/venv"
if [ ! -d "$VENV_DIR" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

# Install Python packages
print_status "Installing Python packages..."
pip install --upgrade pip
pip install \
    torch torchvision torchaudio \
    transformers accelerate \
    fastapi uvicorn \
    pydantic aiohttp \
    pyyaml python-dotenv

# Create API server
print_status "Creating API server..."
cat > jetson_api_server.py <<'PYEOF'
#!/usr/bin/env python3
"""
Sentient Core v4 - Jetson API Server
Provides deep reasoning and multimodal inference capabilities.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
import uvicorn
import logging
from datetime import datetime
from typing import Dict, Optional, List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('JetsonAPI')

app = FastAPI(title="Sentient Core Jetson API", version="4.0.0")

# Global state
jetson_state = {
    'model_loaded': False,
    'model': None,
    'tokenizer': None,
    'connected_nodes': {},
    'inference_count': 0
}

class InferenceRequest(BaseModel):
    input: str
    context: Optional[Dict] = {}
    max_tokens: int = 512
    temperature: float = 0.7

class NodeRegistration(BaseModel):
    node_id: str
    capabilities: List[str]
    timestamp: str

class StateSync(BaseModel):
    node_id: str
    state: Dict
    timestamp: str

@app.on_event("startup")
async def load_model():
    """Load model on startup."""
    global jetson_state

    try:
        logger.info("Loading model...")

        # Adjust model path as needed
        model_path = "/home/nvidia/models/qwen2.5-vl-3b-instruct"

        from transformers import AutoTokenizer, AutoModelForCausalLM

        jetson_state['tokenizer'] = AutoTokenizer.from_pretrained(model_path)
        jetson_state['model'] = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            device_map="auto"
        )

        jetson_state['model_loaded'] = True
        logger.info("✓ Model loaded successfully")

    except Exception as e:
        logger.error(f"Model loading failed: {e}")
        logger.warning("Running without model (responses will be simulated)")
        jetson_state['model_loaded'] = False

@app.get("/")
async def root():
    """API health check."""
    return {
        "service": "Sentient Core Jetson API",
        "status": "operational",
        "model_loaded": jetson_state['model_loaded'],
        "inference_count": jetson_state['inference_count'],
        "version": "4.0.0"
    }

@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "model_loaded": jetson_state['model_loaded'],
        "connected_nodes": len(jetson_state['connected_nodes']),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/register")
async def register_node(registration: NodeRegistration):
    """Register remote node (Pi 5)."""
    jetson_state['connected_nodes'][registration.node_id] = {
        'capabilities': registration.capabilities,
        'registered_at': registration.timestamp,
        'last_seen': datetime.now().isoformat()
    }
    logger.info(f"✓ Node registered: {registration.node_id}")
    return {"status": "registered", "node_id": registration.node_id}

@app.post("/inference")
async def deep_inference(request: InferenceRequest):
    """Deep reasoning inference endpoint."""
    if not jetson_state['model_loaded']:
        # Simulated response if model not loaded
        return {
            "text": f"[Simulated] Response to: {request.input}",
            "node": "jetson_cortana_deep",
            "latency": 0.5,
            "confidence": 0.7,
            "timestamp": datetime.now().isoformat()
        }

    try:
        start_time = datetime.now()

        # Build prompt
        prompt = f"<|im_start|>user\n{request.input}<|im_end|>\n<|im_start|>assistant\n"

        # Tokenize
        inputs = jetson_state['tokenizer'](
            prompt,
            return_tensors="pt"
        ).to(jetson_state['model'].device)

        # Generate
        with torch.no_grad():
            outputs = jetson_state['model'].generate(
                **inputs,
                max_new_tokens=request.max_tokens,
                temperature=request.temperature,
                do_sample=True
            )

        # Decode
        response_text = jetson_state['tokenizer'].decode(
            outputs[0][inputs['input_ids'].shape[1]:],
            skip_special_tokens=True
        )

        latency = (datetime.now() - start_time).total_seconds()
        jetson_state['inference_count'] += 1

        logger.info(f"Inference completed in {latency:.2f}s")

        return {
            "text": response_text,
            "node": "jetson_cortana_deep",
            "latency": latency,
            "confidence": 0.92,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Inference error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sync")
async def sync_state(sync: StateSync):
    """Receive state synchronization from Pi 5."""
    node_id = sync.node_id

    if node_id in jetson_state['connected_nodes']:
        jetson_state['connected_nodes'][node_id]['last_seen'] = datetime.now().isoformat()

    return {"status": "synced", "timestamp": datetime.now().isoformat()}

@app.get("/state")
async def get_state():
    """Provide current state to Pi 5."""
    return {
        "node_id": "jetson_cortana_deep",
        "model_loaded": jetson_state['model_loaded'],
        "inference_count": jetson_state['inference_count'],
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
PYEOF

chmod +x jetson_api_server.py

# Create systemd service
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/sentient-jetson.service > /dev/null <<EOF
[Unit]
Description=Sentient Core Jetson API Server
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$VENV_DIR/bin:\$PATH"
ExecStart=$VENV_DIR/bin/python jetson_api_server.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable sentient-jetson.service

echo ""
echo "================================================================"
echo "Jetson API Server Setup Complete!"
echo "================================================================"
echo ""
echo "Installation directory: $INSTALL_DIR"
echo "Virtual environment: $VENV_DIR"
echo ""
echo "Next steps:"
echo ""
echo "1. Place your model in: $HOME/models/qwen2.5-vl-3b-instruct"
echo "   (or adjust model_path in jetson_api_server.py)"
echo ""
echo "2. Start the service:"
echo "   sudo systemctl start sentient-jetson"
echo ""
echo "3. Check status:"
echo "   sudo systemctl status sentient-jetson"
echo "   curl http://localhost:8000/"
echo ""
echo "4. View logs:"
echo "   journalctl -u sentient-jetson -f"
echo ""
echo "API will be available at: http://<jetson-ip>:8000"
echo ""
