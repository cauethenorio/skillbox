#!/usr/bin/env python3
"""Transcribe voice messages in a processed WhatsApp conversation.

Usage:
    python3 transcribe-conversation-audios.py <conversation-folder> <language>

Finds untranscribed .opus files in exported/, transcribes them in parallel,
then regenerates the conversation chunks with inline transcriptions.
"""

import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TRANSCRIBE_SH = os.path.join(SCRIPT_DIR, "transcribe-audio.sh")

MAX_WORKERS = 2

AUDIO_EXTENSIONS = {".opus", ".mp3", ".m4a", ".ogg"}


def find_untranscribed(exported_dir: str) -> list[str]:
    """Find audio files in exported/ that don't have a .txt transcription."""
    results = []
    for fname in sorted(os.listdir(exported_dir)):
        lower = fname.lower()
        if any(lower.endswith(ext) for ext in AUDIO_EXTENSIONS):
            txt_file = os.path.splitext(fname)[0] + ".txt"
            if not os.path.exists(os.path.join(exported_dir, txt_file)):
                results.append(fname)
    return results


def transcribe_one(audio_path: str, language: str) -> tuple[str, bool]:
    """Transcribe a single audio file. Returns (audio_path, success)."""
    basename = os.path.basename(audio_path)
    result = subprocess.run(
        [TRANSCRIBE_SH, audio_path, language],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"  FAILED: {basename}")
        return (audio_path, False)
    print(f"  OK: {basename}")
    return (audio_path, True)


def update_processed(conversation_dir: str, language: str):
    """Update .processed to record transcription preference."""
    path = os.path.join(conversation_dir, ".processed")
    data = {}
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
    data["transcribe"] = True
    data["language"] = language
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 transcribe-conversation-audios.py <conversation-folder> <language>")
        sys.exit(1)

    conversation_dir = os.path.abspath(sys.argv[1])
    language = sys.argv[2]

    exported_dir = os.path.join(conversation_dir, "exported")
    if not os.path.isdir(exported_dir):
        print(f"ERROR: No exported/ folder found in {conversation_dir}", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(TRANSCRIBE_SH):
        print(f"ERROR: transcribe-audio.sh not found at {TRANSCRIBE_SH}", file=sys.stderr)
        sys.exit(1)

    # Find untranscribed audio files
    untranscribed = find_untranscribed(exported_dir)
    if not untranscribed:
        print("No untranscribed voice messages found.")
        return

    print(f"Found {len(untranscribed)} untranscribed voice message(s)")
    print(f"Transcribing with {MAX_WORKERS} parallel workers...\n")

    total = len(untranscribed)
    completed = 0
    failed = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {}
        for opus_filename in untranscribed:
            audio_path = os.path.join(exported_dir, opus_filename)
            future = executor.submit(transcribe_one, audio_path, language)
            futures[future] = opus_filename

        for future in as_completed(futures):
            _, success = future.result()
            if success:
                completed += 1
            else:
                failed += 1

    print(f"\nTranscribed {completed}/{total} voice messages", end="")
    if failed:
        print(f" ({failed} failed)")
    else:
        print()

    # Update .processed with transcription preference
    update_processed(conversation_dir, language)

    if completed > 0:
        print("\nRe-run process-conversation.py to regenerate chunks with transcriptions.")


if __name__ == "__main__":
    main()
