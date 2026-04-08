#!/bin/bash
# Setup whisper.cpp and download the large-v3 model for audio transcription.
# Run this once before using transcribe-audio.sh.
#
# Usage: ./setup.sh [--shared | --local]
#   --shared: Install to ~/.whisper.cpp (reusable across projects)
#   --local:  Install to skill directory (default)
#
# Prerequisites: cmake, git, ffmpeg
#   brew install cmake ffmpeg

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
MODE="${1:---local}"

case "$MODE" in
    --shared)
        WHISPER_DIR="$HOME/.whisper.cpp"
        echo "=== Setting up whisper.cpp (shared: ~/.whisper.cpp) ==="
        ;;
    --local)
        WHISPER_DIR="$SKILL_DIR/whisper.cpp"
        echo "=== Setting up whisper.cpp (local: skill directory) ==="
        ;;
    *)
        echo "Usage: $0 [--shared | --local]"
        exit 1
        ;;
esac

# Step 1: Clone whisper.cpp if not present
if [ ! -d "$WHISPER_DIR" ]; then
    echo "Cloning whisper.cpp..."
    git clone https://github.com/ggerganov/whisper.cpp.git "$WHISPER_DIR"
else
    echo "whisper.cpp already cloned."
fi

# Step 2: Build whisper-cli
if [ ! -f "$WHISPER_DIR/build/bin/whisper-cli" ]; then
    echo "Building whisper-cli..."
    cd "$WHISPER_DIR"
    cmake -B build
    cmake --build build --config Release -j
    cd "$SKILL_DIR"
else
    echo "whisper-cli already built."
fi

# Step 3: Download model
MODEL="$WHISPER_DIR/models/ggml-large-v3.bin"

if [ ! -f "$MODEL" ]; then
    echo "Downloading large-v3 model (~3GB)..."
    cd "$WHISPER_DIR"
    bash models/download-ggml-model.sh large-v3
    cd "$SKILL_DIR"
else
    echo "Model already downloaded."
fi

echo ""
echo "=== Setup complete! ==="
echo "Binary: $WHISPER_DIR/build/bin/whisper-cli"
echo "Model:  $MODEL"
