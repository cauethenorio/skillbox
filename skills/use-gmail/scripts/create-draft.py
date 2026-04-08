#!/usr/bin/env python3
"""Create a Gmail draft.

Usage:
    python create-draft.py --to recipient@example.com --subject "Subject" --body "Body"
    python create-draft.py --to recipient@example.com --subject "Subject" --body "Body" --cc cc@example.com --bcc bcc@example.com

Examples:
    python create-draft.py --to alice@example.com --subject "Meeting notes" --body "Here are the notes from today."
    python create-draft.py --to bob@example.com --subject "Report" --body "<h1>Report</h1><p>See attached.</p>" --html
"""

import argparse
import base64
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


def build_raw_message(to, subject, body, cc=None, bcc=None, html=False):
    """Build an RFC 2822 message and return it as base64url."""
    content_type = "text/html" if html else "text/plain"
    headers = [
        f"To: {to}",
        f"Subject: {subject}",
        f"Content-Type: {content_type}; charset=utf-8",
    ]
    if cc:
        headers.append(f"Cc: {cc}")
    if bcc:
        headers.append(f"Bcc: {bcc}")

    message = "\r\n".join(headers) + "\r\n\r\n" + body
    raw = base64.urlsafe_b64encode(message.encode("utf-8")).decode("ascii")
    return raw.rstrip("=")


def main():
    parser = argparse.ArgumentParser(description="Create a Gmail draft")
    parser.add_argument("--to", required=True, help="Recipient email address")
    parser.add_argument("--subject", required=True, help="Email subject")
    parser.add_argument("--body", required=True, help="Email body")
    parser.add_argument("--cc", help="CC recipient(s)")
    parser.add_argument("--bcc", help="BCC recipient(s)")
    parser.add_argument("--html", action="store_true", help="Treat body as HTML")
    args = parser.parse_args()

    raw = build_raw_message(
        to=args.to,
        subject=args.subject,
        body=args.body,
        cc=args.cc,
        bcc=args.bcc,
        html=args.html,
    )

    result = run_gmail_cli(
        "users", "drafts", "create",
        "--params", json.dumps({"userId": "me"}),
        "--json", json.dumps({"message": {"raw": raw}}),
    )

    draft_id = result.get("id", "unknown")
    msg_id = result.get("message", {}).get("id", "unknown")
    print(f"Draft created successfully.")
    print(f"  Draft ID:   {draft_id}")
    print(f"  Message ID: {msg_id}")


if __name__ == "__main__":
    main()
