---
name: use-gmail
description: Use when needing to search, read, draft, send, download attachments from Gmail, or when any other skill requires Gmail operations
---

# Gmail via Google Workspace CLI — Quick Reference

Gmail operations use `npx @googleworkspace/cli gmail`. Auth is handled automatically via keyring.

## Helper Scripts

**Search emails** (shows subject, date, from, attachments for each result):
```bash
python ${CLAUDE_SKILL_DIR}/scripts/search-emails.py "from:nubank informe 2025"
python ${CLAUDE_SKILL_DIR}/scripts/search-emails.py "has:attachment after:2026/01/01" --max 20
```

**Download all attachments** from a message:
```bash
python ${CLAUDE_SKILL_DIR}/scripts/download-attachments.py <message-id> <output-dir>
```

**Create a draft:**
```bash
python ${CLAUDE_SKILL_DIR}/scripts/create-draft.py --to recipient@example.com --subject "Subject" --body "Body"
python ${CLAUDE_SKILL_DIR}/scripts/create-draft.py --to recipient@example.com --subject "Subject" --body "Body" --cc cc@example.com --html
```

## Searching Emails

```bash
npx @googleworkspace/cli gmail users messages list \
  --params '{"userId": "me", "q": "<gmail-search-query>", "maxResults": 10}'
```

Returns JSON with `messages` array containing `id` and `threadId`. Use the `id` for subsequent operations.

**Common query patterns:**

| Goal | Query |
|---|---|
| From a sender | `from:user@example.com` |
| With subject | `subject:invoice` |
| With attachment | `has:attachment` |
| Date range | `after:2026/01/01 before:2026/02/01` |
| Unread | `is:unread` |
| Combined | `from:noreply@example.com has:attachment after:2026/01/01` |

Full syntax: [Gmail search operators](https://support.google.com/mail/answer/7190).

## Reading an Email

**Helper (preferred — extracts body as plain text automatically):**

```bash
npx @googleworkspace/cli gmail +read --id <message-id>
npx @googleworkspace/cli gmail +read --id <message-id> --headers  # include From, To, Subject, Date
npx @googleworkspace/cli gmail +read --id <message-id> --format json | jq '.body'
```

**Raw API (when you need attachment metadata):**

```bash
npx @googleworkspace/cli gmail users messages get \
  --params '{"userId": "me", "id": "<message-id>"}'
```

Returns full message with headers, body, and attachment metadata in `payload.parts[]`. Each attachment part has an `attachmentId` in `body.attachmentId` and a `filename`.

## Downloading Attachments

**Script helper (preferred — downloads all attachments at once):**

```bash
python ${CLAUDE_SKILL_DIR}/scripts/download-attachments.py <message-id> <output-dir>
```

Example:
```bash
python ${CLAUDE_SKILL_DIR}/scripts/download-attachments.py 19d0344a57550efe ./dados/documentos/
```

The script finds all attachments, handles base64url decoding, and saves each file with its original name.

**Manual method (when you need a single attachment by ID):**

```bash
npx @googleworkspace/cli gmail users messages attachments get \
  --params '{"userId": "me", "messageId": "<message-id>", "id": "<attachment-id>"}' \
  2>/dev/null | jq -r '.data' | tr '_-' '/+' | base64 -d > /absolute/path/to/file.pdf
```

- `attachmentId` is in `payload.parts[N].body.attachmentId` from the message read
- Always use absolute paths for the output file
- The `tr '_-' '/+'` converts base64url to standard base64 before decoding

## Sending Email

**Helper (preferred):**

```bash
npx @googleworkspace/cli gmail +send \
  --to recipient@example.com \
  --subject "Subject" \
  --body "Body text here"
```

With attachments (up to 25MB combined):

```bash
npx @googleworkspace/cli gmail +send \
  --to recipient@example.com \
  --subject "Subject" \
  --body "Body text here" \
  -a /absolute/path/to/file1.pdf \
  -a /absolute/path/to/file2.pdf
```

Optional flags: `--cc`, `--bcc`, `--from`, `--html`, `--dry-run`.

## Drafts

**List drafts:**

```bash
npx @googleworkspace/cli gmail users drafts list \
  --params '{"userId": "me", "maxResults": 10}'
```

**Get a draft:**

```bash
npx @googleworkspace/cli gmail users drafts get \
  --params '{"userId": "me", "id": "<draft-id>"}'
```

**Create a draft:**

The draft API expects a raw RFC 2822 message encoded as base64url in the `message.raw` field:

```bash
RAW=$(printf 'To: recipient@example.com\r\nSubject: Draft subject\r\nContent-Type: text/plain; charset=utf-8\r\n\r\nDraft body here' | base64 | tr '+/' '-_' | tr -d '=')

npx @googleworkspace/cli gmail users drafts create \
  --params '{"userId": "me"}' \
  --json "{\"message\": {\"raw\": \"$RAW\"}}"
```

To include Cc/Bcc, add them as headers before the blank line:

```bash
RAW=$(printf 'To: recipient@example.com\r\nCc: cc@example.com\r\nBcc: bcc@example.com\r\nSubject: Draft subject\r\nContent-Type: text/plain; charset=utf-8\r\n\r\nDraft body here' | base64 | tr '+/' '-_' | tr -d '=')
```

**Update a draft:**

```bash
RAW=$(printf 'To: recipient@example.com\r\nSubject: Updated subject\r\nContent-Type: text/plain; charset=utf-8\r\n\r\nUpdated body' | base64 | tr '+/' '-_' | tr -d '=')

npx @googleworkspace/cli gmail users drafts update \
  --params '{"userId": "me", "id": "<draft-id>"}' \
  --json "{\"message\": {\"raw\": \"$RAW\"}}"
```

**Send a draft:**

```bash
npx @googleworkspace/cli gmail users drafts send \
  --params '{"userId": "me"}' \
  --json '{"id": "<draft-id>"}'
```

**Delete a draft** (permanent — not recoverable):

```bash
npx @googleworkspace/cli gmail users drafts delete \
  --params '{"userId": "me", "id": "<draft-id>"}'
```

## Forwarding Email

```bash
npx @googleworkspace/cli gmail +forward \
  --message-id <message-id> \
  --to recipient@example.com
```

Optional flags: `--body` (add message), `-a` (extra attachments), `--cc`, `--bcc`, `--html`, `--dry-run`.

## Labeling Emails

```bash
npx @googleworkspace/cli gmail users messages modify \
  --params '{"userId": "me", "id": "<message-id>"}' \
  --json '{"addLabelIds": ["<label-id>"]}'
```

## Listing Labels

```bash
npx @googleworkspace/cli gmail users labels list \
  --params '{"userId": "me"}'
```

## Discovering API Methods

```bash
npx @googleworkspace/cli gmail --help
npx @googleworkspace/cli gws schema gmail.<resource>.<method>
```

## Common Mistakes

- **Forgetting `2>/dev/null` on attachment download:** Without it, stderr output ("Using keyring backend: keyring") gets mixed into the binary file.
- **Not converting base64url:** Gmail uses URL-safe base64 (`_-` instead of `/+`). Always `tr '_-' '/+'` before `base64 -d`.
- **Forgetting `"userId": "me"`:** Required in all `--params` for Gmail API calls.
- **Large attachment output in terminal:** Always pipe attachment GET through `jq` and redirect to file — never let it print raw to stdout.
