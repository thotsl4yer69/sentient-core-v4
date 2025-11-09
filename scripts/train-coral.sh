#!/bin/bash
# Sentient Core v4 - Coral Model Training Script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Default values
CONFIG_FILE="config/coral_config.yaml"
DATA_DIR="data/coral"
OUTPUT_DIR="models/coral"
EPOCHS=50
BATCH_SIZE=32

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --data)
            DATA_DIR="$2"
            shift 2
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --epochs)
            EPOCHS="$2"
            shift 2
            ;;
        --batch-size)
            BATCH_SIZE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

log_info "Starting Coral model training pipeline..."

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    log_warning "Virtual environment not activated. Activating..."
    source venv/bin/activate
fi

# Check dependencies
log_info "Checking dependencies..."
python -c "import tensorflow; import pycoral" 2>/dev/null || {
    log_error "Required packages not installed. Installing..."
    pip install -r requirements-coral.txt
}

# Create output directory
mkdir -p "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR/edgetpu"
mkdir -p "$OUTPUT_DIR/logs"

# Step 1: Train model
log_info "Step 1/5: Training model..."
python -m sentient_core.coral.train \
    --config "$CONFIG_FILE" \
    --data-dir "$DATA_DIR" \
    --output-dir "$OUTPUT_DIR" \
    --epochs "$EPOCHS" \
    --batch-size "$BATCH_SIZE"

if [ $? -eq 0 ]; then
    log_success "Model training completed"
else
    log_error "Model training failed"
    exit 1
fi

# Step 2: Evaluate model
log_info "Step 2/5: Evaluating model..."
python -m sentient_core.coral.evaluate \
    --model "$OUTPUT_DIR/model.h5" \
    --data-dir "$DATA_DIR/test"

# Step 3: Convert to TFLite
log_info "Step 3/5: Converting to TensorFlow Lite..."
python -m sentient_core.coral.convert \
    --model "$OUTPUT_DIR/model.h5" \
    --output "$OUTPUT_DIR/model.tflite" \
    --quantize int8

if [ $? -eq 0 ]; then
    log_success "TFLite conversion completed"
else
    log_error "TFLite conversion failed"
    exit 1
fi

# Step 4: Compile for Edge TPU
log_info "Step 4/5: Compiling for Edge TPU..."
if command -v edgetpu_compiler &> /dev/null; then
    edgetpu_compiler "$OUTPUT_DIR/model.tflite" \
        --out_dir "$OUTPUT_DIR/edgetpu" \
        --show_operations

    if [ $? -eq 0 ]; then
        log_success "Edge TPU compilation completed"
    else
        log_error "Edge TPU compilation failed"
        exit 1
    fi
else
    log_warning "Edge TPU compiler not found. Skipping compilation."
    log_info "Install with: sudo apt-get install edgetpu-compiler"
fi

# Step 5: Validate model
log_info "Step 5/5: Validating model..."
python -m sentient_core.coral.validate \
    --tflite-model "$OUTPUT_DIR/model.tflite" \
    --edgetpu-model "$OUTPUT_DIR/edgetpu/model_edgetpu.tflite" \
    --test-data "$DATA_DIR/test"

# Generate report
log_info "Generating training report..."
python -m sentient_core.coral.report \
    --output-dir "$OUTPUT_DIR" \
    --report-file "$OUTPUT_DIR/training_report.pdf"

# Summary
log_success "===================================="
log_success "Training Pipeline Complete!"
log_success "===================================="
echo ""
log_info "Output files:"
echo "  - Keras model: $OUTPUT_DIR/model.h5"
echo "  - TFLite model: $OUTPUT_DIR/model.tflite"
echo "  - Edge TPU model: $OUTPUT_DIR/edgetpu/model_edgetpu.tflite"
echo "  - Training logs: $OUTPUT_DIR/logs/"
echo "  - Report: $OUTPUT_DIR/training_report.pdf"
echo ""

# Model information
if [ -f "$OUTPUT_DIR/edgetpu/model_edgetpu.tflite" ]; then
    MODEL_SIZE=$(ls -lh "$OUTPUT_DIR/edgetpu/model_edgetpu.tflite" | awk '{print $5}')
    log_info "Edge TPU model size: $MODEL_SIZE"
fi

log_info "Next steps:"
echo "  1. Test model: python -m sentient_core.coral.test --model $OUTPUT_DIR/edgetpu/model_edgetpu.tflite"
echo "  2. Deploy model: ./scripts/deploy-coral.sh --model $OUTPUT_DIR/edgetpu/model_edgetpu.tflite"
echo "  3. Benchmark: python -m sentient_core.coral.benchmark --model $OUTPUT_DIR/edgetpu/model_edgetpu.tflite"
