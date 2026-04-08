#!/usr/bin/env python3
"""Download all attachments from a Gmail message.

Usage:
    python download-attachments.py <message-id> <output-dir>

Example:
    python download-attachments.py 19d0344a57550efe ./dados/documentos/
"""

import base64
import json
import os
import subprocess
import sys


def run_gmail_cli(*args):
    """Run a @googleworkspace/cli gmail command and return parsed JSON."""
    cmd = ["npx", "@googleworkspace/cli", "gmail", *args]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"CLI error: {result.stderr}")
    return json.loads(result.stdout)


def find_attachments(parts):
    """Recursively find all attachments in message parts."""
    attachments = []
    for part in parts:
        filename = part.get("filename")
        attachment_id = part.get("body", {}).get("attachmentId")
        if filename and attachment_id:
            attachments.append({"filename": filename, "attachmentId": attachment_id})
        if "parts" in part:
            attachments.extend(find_attachments(part["parts"]))
    return attachments


def download_attachment(message_id, attachment_id, output_path):
    """Download and decode a single attachment."""
    data = run_gmail_cli(
        "users", "messages", "attachments", "get",
        "--params", json.dumps({
            "userId": "me",
            "messageId": message_id,
            "id": attachment_id,
        }),
    )
    # Gmail uses base64url encoding — convert to standard base64
    b64_data = data["data"].replace("-", "+").replace("_", "/")
    padding = 4 - len(b64_data) % 4
    if padding != 4:
        b64_data += "=" * padding
    raw = base64.b64decode(b64_data)
    with open(output_path, "wb") as f:
        f.write(raw)


def main():
    if len(sys.argv) < 3:
        print(__doc__.strip())
        sys.exit(1)

    message_id = sys.argv[1]
    output_dir = os.path.abspath(sys.argv[2])
    os.makedirs(output_dir, exist_ok=True)

    # Get message to find attachments
    msg = run_gmail_cli(
        "users", "messages", "get",
        "--params", json.dumps({"userId": "me", "id": message_id}),
    )

    parts = msg.get("payload", {}).get("parts", [])
    attachments = find_attachments(parts)

    if not attachments:
        print("No attachments found.")
        sys.exit(0)

    print(f"Found {len(attachments)} attachment(s):")
    for att in attachments:
        output_path = os.path.join(output_dir, att["filename"])
        print(f"  Downloading: {att['filename']}")
        download_attachment(message_id, att["attachmentId"], output_path)
        print(f"  Saved to: {output_path}")

    print("Done.")


if __name__ == "__main__":
    main()
