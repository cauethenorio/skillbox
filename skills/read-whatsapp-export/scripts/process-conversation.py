#!/usr/bin/env python3
"""Process a WhatsApp export into clean, chunked markdown files.

Usage:
    python3 process-conversation.py <path-to-export-zip-or-folder> [--output-dir DIR] [--max-chunk-kb N]

Extracts export into exported/, parses _chat.txt, formats as markdown, splits
into ~100KB chunks named by date range. Re-running with a newer export overwrites
exported/ and regenerates chunks.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
import zipfile
from datetime import date, datetime
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Parsing ---

MESSAGE_RE = re.compile(
    r"^\[(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}:\d{2})\]\s(.+?):\s(.*)"
)

ATTACHMENT_RE = re.compile(
    r"<(?:attached|anexado|archivo adjunto):\s*(.+?)>"
)

ZERO_WIDTH_RE = re.compile(r"[\u200e\u200f\u200b\u200c\u200d\u2068\u2069\ufeff]")

AUDIO_EXTENSIONS = {".opus", ".mp3", ".m4a", ".ogg"}

# Date field order: (field1, field2, year)
DMY = "dmy"  # DD/MM/YY or DD/MM/YYYY
MDY = "mdy"  # MM/DD/YY or MM/DD/YYYY


def _try_parse_date(d1: int, d2: int, yr: int, order: str) -> date | None:
    """Try to parse a date with the given field order. Returns None if invalid."""
    if yr < 100:
        yr += 2000
    try:
        if order == DMY:
            return date(yr, d2, d1)
        else:
            return date(yr, d1, d2)
    except ValueError:
        return None


def detect_date_format(lines: list[str]) -> str:
    """Detect date format by trying DMY and MDY on all dates in the file.

    Returns the format where all dates are valid. If both work (ambiguous),
    defaults to DMY.
    """
    dates = []
    for line in lines:
        line = line.rstrip("\r\n")
        cleaned = ZERO_WIDTH_RE.sub("", line)
        match = MESSAGE_RE.match(cleaned)
        if match:
            parts = match.group(1).split("/")
            dates.append((int(parts[0]), int(parts[1]), int(parts[2])))

    if not dates:
        return DMY

    dmy_valid = all(_try_parse_date(d1, d2, yr, DMY) is not None for d1, d2, yr in dates)
    mdy_valid = all(_try_parse_date(d1, d2, yr, MDY) is not None for d1, d2, yr in dates)

    if dmy_valid and not mdy_valid:
        return DMY
    if mdy_valid and not dmy_valid:
        return MDY
    # Both valid (all ambiguous) — default to DMY
    return DMY


def parse_messages(lines: list[str], date_format: str | None = None) -> list[dict]:
    """Parse WhatsApp _chat.txt lines into structured message dicts."""
    if date_format is None:
        date_format = detect_date_format(lines)

    messages = []
    current = None

    for line in lines:
        line = line.rstrip("\r\n")
        cleaned_line = ZERO_WIDTH_RE.sub("", line)
        match = MESSAGE_RE.match(cleaned_line)

        if match:
            if current:
                messages.append(current)

            date_str, time_str, sender, text = match.groups()
            sender = sender.strip()
            text = text.strip()

            parts = date_str.split("/")
            d1, d2, yr = int(parts[0]), int(parts[1]), int(parts[2])
            msg_date = _try_parse_date(d1, d2, yr, date_format)

            att_match = ATTACHMENT_RE.search(text)
            attachment = att_match.group(1) if att_match else None

            current = {
                "date": msg_date,
                "time": time_str,
                "date_display": date_str,
                "sender": sender,
                "text": text,
                "attachment": attachment,
            }
        elif current:
            current["text"] += "\n" + cleaned_line

    if current:
        messages.append(current)

    return messages


# --- Formatting ---

def classify_attachment(filename: str) -> str:
    lower = filename.lower()
    if any(lower.endswith(ext) for ext in AUDIO_EXTENSIONS):
        return "audio"
    if "STICKER-" in filename:
        return "sticker"
    if lower.endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")):
        return "photo"
    if lower.endswith((".mp4", ".3gp", ".mov")):
        return "video"
    return "document"


def friendly_name(filename: str) -> str:
    """'00000005-DOC-contract.pdf' -> 'contract.pdf'"""
    parts = filename.split("-", 2)
    if len(parts) >= 3 and parts[0].isdigit():
        return parts[2]
    return filename


def format_message(msg: dict, transcriptions: dict) -> str:
    prefix = f"[{msg['date_display']}, {msg['time']}]"
    attachment = msg.get("attachment")

    if not attachment:
        return f"{prefix} {msg['text']}"

    kind = classify_attachment(attachment)

    if kind == "audio":
        if attachment in transcriptions:
            text = transcriptions[attachment]
            return (
                f'{prefix} 🎤 "{text}"\n'
                f"> Audio: [exported/{attachment}](exported/{attachment})"
            )
        return f"{prefix} [Voice message](exported/{attachment})"

    if kind == "photo":
        return f"{prefix} [Photo](exported/{attachment})"
    if kind == "video":
        return f"{prefix} [Video](exported/{attachment})"
    if kind == "sticker":
        return f"{prefix} [Sticker](exported/{attachment})"

    name = friendly_name(attachment)
    return f"{prefix} [Document: {name}](exported/{attachment})"


# --- Chunking ---

def chunk_messages(messages: list[dict], transcriptions: dict, max_bytes: int) -> list[dict]:
    if not messages:
        return []

    chunks = []
    current_msgs = []
    current_lines = []
    current_size = 0

    for msg in messages:
        line = format_message(msg, transcriptions)
        line_bytes = len(line.encode("utf-8")) + 2

        if current_msgs and current_size + line_bytes > max_bytes:
            chunks.append({
                "start_date": current_msgs[0]["date"],
                "end_date": current_msgs[-1]["date"],
                "lines": current_lines,
                "messages": current_msgs,
            })
            current_msgs = []
            current_lines = []
            current_size = 0

        current_msgs.append(msg)
        current_lines.append(line)
        current_size += line_bytes

    if current_msgs:
        chunks.append({
            "start_date": current_msgs[0]["date"],
            "end_date": current_msgs[-1]["date"],
            "lines": current_lines,
            "messages": current_msgs,
        })

    return chunks


# --- File organization ---

def extract_contact_name(source_name: str) -> str:
    """'WhatsApp Chat - John Smith.zip' -> 'john-smith'"""
    name = source_name
    if name.lower().endswith(".zip"):
        name = name[:-4]
    if " - " in name:
        name = name.split(" - ", 1)[1]
    name = name.strip()
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_name = nfkd.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_name).strip("-").lower()
    return slug


def load_transcriptions(folder: str) -> dict[str, str]:
    """Load .txt files sitting alongside .opus files."""
    transcriptions = {}
    for opus_file in Path(folder).glob("*.opus"):
        txt_file = opus_file.with_suffix(".txt")
        if txt_file.exists():
            text = txt_file.read_text(encoding="utf-8").strip()
            if text:
                transcriptions[opus_file.name] = text
    return transcriptions


def find_chat_file(folder: str) -> str | None:
    for name in os.listdir(folder):
        if name == "_chat.txt":
            return os.path.join(folder, name)
    return None


def read_processed(output_dir: str) -> dict | None:
    path = os.path.join(output_dir, ".processed")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


def write_processed(output_dir: str, messages: list[dict], transcribe: bool | None = None, language: str | None = None):
    path = os.path.join(output_dir, ".processed")
    existing = read_processed(output_dir) or {}
    data = {
        "last_processed": datetime.now().isoformat(timespec="seconds"),
        "message_count": len(messages),
        "transcribe": transcribe if transcribe is not None else existing.get("transcribe"),
        "language": language if language is not None else existing.get("language"),
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def process_export(
    source_path: str,
    output_parent: str | None = None,
    max_chunk_bytes: int = 100_000,
) -> str:
    source_path = os.path.abspath(source_path)
    is_zip = os.path.isfile(source_path) and zipfile.is_zipfile(source_path)

    source_name = os.path.basename(source_path)

    # Output directory
    contact_slug = extract_contact_name(source_name)
    output_dir_name = f"whatsapp-{contact_slug}-conversation"
    if output_parent is None:
        output_parent = os.path.dirname(source_path)
    output_dir = os.path.join(output_parent, output_dir_name)
    exported_dir = os.path.join(output_dir, "exported")

    os.makedirs(output_dir, exist_ok=True)

    # Extract/copy export into exported/
    if is_zip:
        # Extract zip contents into exported/
        with zipfile.ZipFile(source_path, "r") as zf:
            # Check if zip has a single subdirectory
            top_dirs = {name.split("/")[0] for name in zf.namelist() if "/" in name}
            names = zf.namelist()

            if len(top_dirs) == 1:
                # Extract contents of subdirectory directly into exported/
                subdir = top_dirs.pop() + "/"
                os.makedirs(exported_dir, exist_ok=True)
                for member in names:
                    if member.startswith(subdir) and member != subdir:
                        # Strip the subdirectory prefix
                        rel_path = member[len(subdir):]
                        if not rel_path:
                            continue
                        target = os.path.join(exported_dir, rel_path)
                        if member.endswith("/"):
                            os.makedirs(target, exist_ok=True)
                        else:
                            os.makedirs(os.path.dirname(target), exist_ok=True)
                            with zf.open(member) as src, open(target, "wb") as dst:
                                shutil.copyfileobj(src, dst)
            else:
                # Extract directly into exported/
                zf.extractall(exported_dir)
    else:
        # Copy folder contents into exported/
        if os.path.abspath(source_path) != os.path.abspath(exported_dir):
            if os.path.exists(exported_dir):
                # Overwrite: copy new files over existing
                for fname in os.listdir(source_path):
                    src = os.path.join(source_path, fname)
                    dst = os.path.join(exported_dir, fname)
                    if os.path.isfile(src):
                        shutil.copy2(src, dst)
            else:
                shutil.copytree(source_path, exported_dir)

    # Find _chat.txt
    chat_file = find_chat_file(exported_dir)
    if not chat_file:
        print(f"ERROR: No _chat.txt found in {exported_dir}", file=sys.stderr)
        sys.exit(1)

    # .gitignore
    gitignore_path = os.path.join(output_dir, ".gitignore")
    with open(gitignore_path, "w") as f:
        f.write("exported/\n")

    # Auto-transcribe if .processed says so
    processed = read_processed(output_dir)
    if processed and processed.get("transcribe") and processed.get("language"):
        transcribe_sh = os.path.join(SCRIPT_DIR, "transcribe-audio.sh")
        if os.path.isfile(transcribe_sh):
            language = processed["language"]
            untranscribed = [
                f for f in sorted(os.listdir(exported_dir))
                if any(f.lower().endswith(ext) for ext in AUDIO_EXTENSIONS)
                and not os.path.exists(os.path.join(exported_dir, os.path.splitext(f)[0] + ".txt"))
            ]
            if untranscribed:
                print(f"Auto-transcribing {len(untranscribed)} audio file(s) (language: {language})...")
                for fname in untranscribed:
                    audio_path = os.path.join(exported_dir, fname)
                    subprocess.run([transcribe_sh, audio_path, language])

    # Load transcriptions from exported/
    transcriptions = load_transcriptions(exported_dir)

    # Parse
    with open(chat_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    messages = parse_messages(lines)

    # Remove old chunk files before regenerating
    for fname in os.listdir(output_dir):
        if fname.startswith("chat-") and fname.endswith(".md"):
            os.remove(os.path.join(output_dir, fname))

    # Chunk and write
    chunks = chunk_messages(messages, transcriptions, max_chunk_bytes)
    chunk_filenames = []
    pad = len(str(len(chunks)))
    for i, chunk in enumerate(chunks, 1):
        start_ym = chunk['start_date'].strftime("%Y-%m")
        end_ym = chunk['end_date'].strftime("%Y-%m")
        filename = f"chat-{i:0{pad}d}-from-{start_ym}-to-{end_ym}.md"
        chunk_filenames.append(filename)
        chunk_path = os.path.join(output_dir, filename)
        with open(chunk_path, "w", encoding="utf-8") as f:
            current_sender = None
            for msg, line in zip(chunk["messages"], chunk["lines"]):
                if msg["sender"] != current_sender:
                    if current_sender is not None:
                        f.write("\n")
                    f.write(f"**{msg['sender']}:**\n")
                    current_sender = msg["sender"]
                f.write(line + "\n")

    # Write .processed metadata
    write_processed(output_dir, messages)

    # --- Summary ---
    print(f"\n=== Processing Complete ===")
    print(f"Output: {output_dir}")

    # Messages
    print(f"\nMessages: {len(messages)}")
    if messages:
        first = messages[0]
        last = messages[-1]
        print(f"Period: {first['date_display']} {first['time']} — {last['date_display']} {last['time']}")

    # Participants
    senders = sorted(set(m["sender"] for m in messages))
    print(f"Participants: {', '.join(senders)}")

    # Audio stats
    audio_files = [f for f in os.listdir(exported_dir) if any(f.lower().endswith(ext) for ext in AUDIO_EXTENSIONS)]
    transcribed = [f for f in audio_files if os.path.exists(os.path.join(exported_dir, os.path.splitext(f)[0] + ".txt"))]
    untranscribed_count = len(audio_files) - len(transcribed)
    if audio_files:
        print(f"Audio messages: {len(audio_files)} ({len(transcribed)} transcribed, {untranscribed_count} pending)")
    else:
        print(f"Audio messages: 0")

    # Files in exported/ by extension
    ext_counts: dict[str, int] = {}
    for fname in os.listdir(exported_dir):
        if os.path.isfile(os.path.join(exported_dir, fname)):
            ext = os.path.splitext(fname)[1].lower() or "(no ext)"
            ext_counts[ext] = ext_counts.get(ext, 0) + 1
    ext_summary = ", ".join(f"{ext}: {count}" for ext, count in sorted(ext_counts.items()))
    print(f"Exported files: {sum(ext_counts.values())} ({ext_summary})")

    # Chunks
    print(f"Chunks: {len(chunk_filenames)}")
    for name in chunk_filenames:
        print(f"  {name}")

    # .processed status
    proc = read_processed(output_dir)
    if proc and proc.get("transcribe"):
        print(f"Auto-transcribe: enabled (language: {proc.get('language')})")
    else:
        print(f"Auto-transcribe: not configured")

    return output_dir


def main():
    parser = argparse.ArgumentParser(
        description="Process a WhatsApp export into chunked markdown."
    )
    parser.add_argument("source", help="Path to export zip or folder")
    parser.add_argument("--output-dir", help="Parent directory for output (default: same as source)")
    parser.add_argument("--max-chunk-kb", type=int, default=100, help="Max chunk size in KB (default: 100)")
    args = parser.parse_args()

    process_export(
        args.source,
        output_parent=args.output_dir,
        max_chunk_bytes=args.max_chunk_kb * 1024,
    )


if __name__ == "__main__":
    main()
