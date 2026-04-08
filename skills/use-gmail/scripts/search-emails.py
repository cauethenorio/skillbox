#!/usr/bin/env python3
"""Search Gmail and display results with subject, date, and attachment info.

Usage:
    python search-emails.py <query> [--max N]

Examples:
    python search-emails.py "from:nubank informe 2025"
    python search-emails.py "has:attachment after:2026/01/01" --max 20
    python search-emails.py "from:itau informe rendimentos"
"""

import json
import subprocess
import sys


def run_gmail_cli(*args):
    """Run a @googleworkspace/cli gmail command and return parsed JSON."""
    cmd = ["npx", "@googleworkspace/cli", "gmail", *args]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"CLI error: {result.stderr}")
    return json.loads(result.stdout)


def get_header(headers, name):
    """Extract a header value by name."""
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def has_attachments(payload):
    """Check if message has file attachments."""
    parts = payload.get("parts", [])
    for part in parts:
        if part.get("filename"):
            return True
        if "parts" in part:
            if has_attachments(part):
                return True
    return False


def list_attachments(payload):
    """List all attachment filenames."""
    names = []
    parts = payload.get("parts", [])
    for part in parts:
        if part.get("filename"):
            names.append(part["filename"])
        if "parts" in part:
            names.extend(list_attachments(part))
    return names


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__.strip())
        sys.exit(0)

    query = sys.argv[1]
    max_results = 10

    if "--max" in sys.argv:
        idx = sys.argv.index("--max")
        max_results = int(sys.argv[idx + 1])

    # Search
    result = run_gmail_cli(
        "users", "messages", "list",
        "--params", json.dumps({
            "userId": "me",
            "q": query,
            "maxResults": max_results,
        }),
    )

    messages = result.get("messages", [])
    if not messages:
        print(f"No results for: {query}")
        sys.exit(0)

    print(f"Found {len(messages)} message(s) for: {query}\n")

    # Get details for each message (single fetch per message)
    for msg in messages:
        msg_id = msg["id"]
        full = run_gmail_cli(
            "users", "messages", "get",
            "--params", json.dumps({"userId": "me", "id": msg_id}),
        )

        headers = full.get("payload", {}).get("headers", [])
        subject = get_header(headers, "Subject")
        from_addr = get_header(headers, "From")
        date = get_header(headers, "Date")
        attachments = list_attachments(full.get("payload", {}))

        print(f"ID: {msg_id}")
        print(f"  From:    {from_addr}")
        print(f"  Date:    {date}")
        print(f"  Subject: {subject}")
        if attachments:
            print(f"  Attachments: {', '.join(attachments)}")
        else:
            print(f"  Attachments: (none)")
        print()


if __name__ == "__main__":
    main()
