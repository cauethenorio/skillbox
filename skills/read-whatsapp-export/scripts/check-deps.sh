#!/bin/bash
# Check dependencies for the read-whatsapp-export skill.
# Prints a summary of what's available and what needs setup.

echo "=== WhatsApp Export Skill — Dependency Check ==="
echo ""

ok=0
missing=0

check() {
    local name="$1"
    local found="$2"
    local install_hint="$3"
    if [ "$found" = "true" ]; then
        echo "  ✓ $name"
        ok=$((ok + 1))
    else
        echo "  ✗ $name — $install_hint"
        missing=$((missing + 1))
    fi
}

# --- Required for processing (always needed) ---
echo "Processing (required):"
check "python3" "$(command -v python3 &>/dev/null && echo true || echo false)" "install Python 3"
echo ""

# --- Required for transcription ---
echo "Transcription (needed for voice messages):"

# ffmpeg
check "ffmpeg" "$(command -v ffmpeg &>/dev/null && echo true || echo false)" "brew install ffmpeg"

# cmake (needed to build whisper.cpp)
check "cmake" "$(command -v cmake &>/dev/null && echo true || echo false)" "brew install cmake"

# whisper.cpp binary
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
if [ -f "$HOME/.whisper.cpp/build/bin/whisper-cli" ]; then
    WHISPER_LOCATION="shared (~/.whisper.cpp)"
    WHISPER_FOUND="true"
elif [ -f "$SKILL_DIR/whisper.cpp/build/bin/whisper-cli" ]; then
    WHISPER_LOCATION="local (skill directory)"
    WHISPER_FOUND="true"
else
    WHISPER_FOUND="false"
fi

if [ "$WHISPER_FOUND" = "true" ]; then
    check "whisper-cli ($WHISPER_LOCATION)" "true" ""
else
    check "whisper-cli" "false" "run setup.sh --shared or --local"
fi

# whisper model
if [ "$WHISPER_FOUND" = "true" ]; then
    if [ -f "$HOME/.whisper.cpp/models/ggml-large-v3.bin" ] || [ -f "$SKILL_DIR/whisper.cpp/models/ggml-large-v3.bin" ]; then
        check "whisper large-v3 model" "true" ""
    else
        check "whisper large-v3 model" "false" "run setup.sh to download (~3GB)"
    fi
fi

echo ""
echo "---"
if [ "$missing" -eq 0 ]; then
    echo "All dependencies available ($ok/$ok). Ready to process and transcribe."
else
    total=$((ok + missing))
    echo "$ok/$total available, $missing missing."
fi
