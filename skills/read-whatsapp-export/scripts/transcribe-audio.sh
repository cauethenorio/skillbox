#!/bin/bash
# Transcribe a single audio file using whisper.cpp.
# Creates a .txt file in the same directory with the same name.
# Does nothing if the .txt file already exists.
#
# Usage: ./transcribe-audio.sh <audio-file> <language>
#   language: whisper language code (e.g. en, pt, es, fr, de)
#
# Prerequisites:
#   - ffmpeg installed (brew install ffmpeg)
#   - whisper.cpp installed (run setup.sh in this directory)

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Check shared install first, then local
if [ -f "$HOME/.whisper.cpp/build/bin/whisper-cli" ]; then
    WHISPER_DIR="$HOME/.whisper.cpp"
elif [ -f "$SKILL_DIR/whisper.cpp/build/bin/whisper-cli" ]; then
    WHISPER_DIR="$SKILL_DIR/whisper.cpp"
else
    echo "ERROR: whisper-cli not found."
    echo "Run setup.sh first: $SKILL_DIR/scripts/setup.sh [--shared | --local]"
    exit 1
fi

WHISPER="$WHISPER_DIR/build/bin/whisper-cli"
MODEL="$WHISPER_DIR/models/ggml-large-v3.bin"

if [ ! -f "$MODEL" ]; then
    echo "ERROR: model not found at $MODEL"
    echo "Run setup.sh first: $SKILL_DIR/scripts/setup.sh"
    exit 1
fi

if ! command -v ffmpeg &>/dev/null; then
    echo "ERROR: ffmpeg not found. Install with: brew install ffmpeg"
    exit 1
fi

AUDIO_FILE="${1:?Usage: $0 <audio-file> <language>}"
LANG="${2:?Usage: $0 <audio-file> <language>}"

if [ ! -f "$AUDIO_FILE" ]; then
    echo "ERROR: file not found: $AUDIO_FILE"
    exit 1
fi

# Output .txt path: same directory, same name, .txt extension
TXT_FILE="${AUDIO_FILE%.*}.txt"

if [ -f "$TXT_FILE" ]; then
    echo "Already transcribed: $(basename "$AUDIO_FILE")"
    exit 0
fi

echo "Transcribing: $(basename "$AUDIO_FILE")"

tmp_wav="${AUDIO_FILE%.*}.wav"
trap 'rm -f "$tmp_wav"' EXIT

ffmpeg -i "$AUDIO_FILE" -ar 16000 -ac 1 "$tmp_wav" -y -loglevel error

"$WHISPER" -m "$MODEL" -f "$tmp_wav" -l "$LANG" --no-timestamps -otxt 2>/dev/null

whisper_txt="${tmp_wav}.txt"
if [ -f "$whisper_txt" ]; then
    mv "$whisper_txt" "$TXT_FILE"
    echo "OK: $(basename "$TXT_FILE")"
else
    echo "ERROR: transcription not generated for $(basename "$AUDIO_FILE")"
    exit 1
fi
