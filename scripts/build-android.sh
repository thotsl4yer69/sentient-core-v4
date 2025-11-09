#!/bin/bash
# Sentient Core v4 - Android APK Build Script

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
BUILD_TYPE="debug"
BUILD_AAB=false
RUN_TESTS=true
UPLOAD_TO_PLAY=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --release)
            BUILD_TYPE="release"
            shift
            ;;
        --aab)
            BUILD_AAB=true
            shift
            ;;
        --no-tests)
            RUN_TESTS=false
            shift
            ;;
        --upload)
            UPLOAD_TO_PLAY=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--release] [--aab] [--no-tests] [--upload]"
            exit 1
            ;;
    esac
done

log_info "Starting Android build pipeline..."
log_info "Build type: $BUILD_TYPE"

# Check Android environment
if [ -z "$ANDROID_HOME" ]; then
    log_error "ANDROID_HOME not set"
    log_info "Please set ANDROID_HOME environment variable"
    exit 1
fi

log_success "Android SDK found at $ANDROID_HOME"

# Navigate to Android project
if [ ! -d "android" ]; then
    log_error "Android project directory not found"
    exit 1
fi

cd android

# Make gradlew executable
chmod +x gradlew

# Clean previous builds
log_info "Cleaning previous builds..."
./gradlew clean

# Run linting
log_info "Running linter..."
./gradlew lint || log_warning "Linting found issues"

# Run unit tests
if [ "$RUN_TESTS" = true ]; then
    log_info "Running unit tests..."
    ./gradlew test || {
        log_error "Unit tests failed"
        exit 1
    }
    log_success "Unit tests passed"

    # Run instrumented tests (if devices available)
    if adb devices | grep -q "device$"; then
        log_info "Running instrumented tests..."
        ./gradlew connectedAndroidTest || log_warning "Instrumented tests failed"
    else
        log_warning "No Android devices connected. Skipping instrumented tests."
    fi
fi

# Build based on type
if [ "$BUILD_TYPE" = "release" ]; then
    log_info "Building release APK/AAB..."

    # Check for signing configuration
    if [ -z "$SENTIENT_KEYSTORE_FILE" ]; then
        log_error "SENTIENT_KEYSTORE_FILE not set for release build"
        log_info "Please set the following environment variables:"
        echo "  - SENTIENT_KEYSTORE_FILE"
        echo "  - SENTIENT_KEYSTORE_PASSWORD"
        echo "  - SENTIENT_KEY_ALIAS"
        echo "  - SENTIENT_KEY_PASSWORD"
        exit 1
    fi

    if [ "$BUILD_AAB" = true ]; then
        # Build App Bundle
        log_info "Building Android App Bundle..."
        ./gradlew bundleRelease

        AAB_PATH="app/build/outputs/bundle/release/app-release.aab"
        if [ -f "$AAB_PATH" ]; then
            AAB_SIZE=$(ls -lh "$AAB_PATH" | awk '{print $5}')
            log_success "App Bundle built successfully ($AAB_SIZE)"
            log_info "Location: $AAB_PATH"
        else
            log_error "App Bundle build failed"
            exit 1
        fi
    else
        # Build APK
        log_info "Building release APK..."
        ./gradlew assembleRelease

        APK_PATH="app/build/outputs/apk/release/app-release.apk"
        if [ -f "$APK_PATH" ]; then
            APK_SIZE=$(ls -lh "$APK_PATH" | awk '{print $5}')
            log_success "Release APK built successfully ($APK_SIZE)"
            log_info "Location: $APK_PATH"
        else
            log_error "Release APK build failed"
            exit 1
        fi
    fi

else
    # Build debug APK
    log_info "Building debug APK..."
    ./gradlew assembleDebug

    APK_PATH="app/build/outputs/apk/debug/app-debug.apk"
    if [ -f "$APK_PATH" ]; then
        APK_SIZE=$(ls -lh "$APK_PATH" | awk '{print $5}')
        log_success "Debug APK built successfully ($APK_SIZE)"
        log_info "Location: $APK_PATH"
    else
        log_error "Debug APK build failed"
        exit 1
    fi
fi

# Generate signing report
log_info "Generating signing report..."
./gradlew signingReport > build_signing_report.txt

# Install on connected device
if adb devices | grep -q "device$"; then
    read -p "Install APK on connected device? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Installing APK..."
        adb install -r "$APK_PATH"
        log_success "APK installed"

        # Launch app
        read -p "Launch app? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            adb shell am start -n ai.sentientcore.android/.MainActivity
        fi
    fi
fi

# Upload to Google Play
if [ "$UPLOAD_TO_PLAY" = true ] && [ "$BUILD_TYPE" = "release" ] && [ "$BUILD_AAB" = true ]; then
    log_info "Uploading to Google Play..."

    cd ..  # Back to root

    if [ -f "scripts/upload-to-play.py" ]; then
        python scripts/upload-to-play.py \
            --package ai.sentientcore.android \
            --aab "android/$AAB_PATH" \
            --track internal

        log_success "Uploaded to Google Play internal track"
    else
        log_error "Upload script not found"
    fi
fi

# Summary
echo ""
log_success "===================================="
log_success "Build Pipeline Complete!"
log_success "===================================="
echo ""
log_info "Build artifacts:"
if [ "$BUILD_TYPE" = "release" ]; then
    if [ "$BUILD_AAB" = true ]; then
        echo "  - App Bundle: android/$AAB_PATH"
    else
        echo "  - Release APK: android/$APK_PATH"
    fi
else
    echo "  - Debug APK: android/$APK_PATH"
fi
echo "  - Build reports: android/app/build/reports/"
echo "  - Signing report: android/build_signing_report.txt"
echo ""

log_info "Next steps:"
if [ "$BUILD_TYPE" = "debug" ]; then
    echo "  1. Test APK: adb install -r android/$APK_PATH"
    echo "  2. Build release: ./scripts/build-android.sh --release --aab"
else
    echo "  1. Upload to internal: ./scripts/build-android.sh --release --aab --upload"
    echo "  2. Promote to production: gcloud alpha app-bundles promote ..."
fi
