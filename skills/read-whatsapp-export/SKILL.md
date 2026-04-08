---
name: read-whatsapp-export
description: Use when needing to process exported WhatsApp conversations — converts raw exports (zip or folder with _chat.txt) into clean markdown with transcribed voice messages
---

# Processing WhatsApp Exports

Converts raw WhatsApp exports into clean, chunked markdown files ready for reading. Fully offline.

## Workflow

1. **Process** — run `process-conversation.py`. Safe to re-run: it extracts into `exported/`, regenerates all chunks. A newer export just overwrites and regenerates.
2. **Check output** — the script prints a summary including pending audio transcriptions.
3. **Ask about transcription** — if there are pending audio messages, ask the user if they want them transcribed.
4. **Transcribe** (if yes) — run `transcribe-conversation-audios.py` (see below).
5. **Re-process** — run `process-conversation.py` again to regenerate chunks with transcriptions inline.
6. **Report** — tell the user the output location and summary.

## Running the processor

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/process-conversation.py "path/to/export.zip" --output-dir .
```

Always pass `--output-dir .` to create the conversation folder in the current project directory.

Options: `--output-dir DIR` (default: same parent as source), `--max-chunk-kb N` (default: 100).

Re-running with a newer export of the same conversation overwrites `exported/` and regenerates all chunks. Existing transcriptions (`.txt` files) are preserved if the audio files haven't changed.

## Transcribing Voice Messages

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/transcribe-conversation-audios.py "path/to/whatsapp-name-conversation" <language>
```

Transcribes all `.opus` files in `exported/` that don't have a `.txt` yet. Saves the language and transcription preference in `.processed`. After transcription, re-run `process-conversation.py` to regenerate chunks with inline transcriptions. On future re-runs, `process-conversation.py` auto-transcribes new audio files if `.processed` has `transcribe: true`.

**Language detection:** Read the first ~50 lines of the conversation to identify the language (`<attached:` = en, `<anexado:` = pt, `<archivo adjunto:` = es). Pass as whisper code: `en`, `pt`, `es`, etc.

## Output structure

```
whatsapp-name-conversation/
  .gitignore              # ignores exported/
  .processed              # metadata (transcription preference, language)
  chat-2024-01-01_2024-06-15.md
  chat-2024-06-16_2024-12-31.md
  exported/               # gitignored — full export contents
    _chat.txt
    00000001-PHOTO-*.jpg
    00000002-AUDIO-*.opus
    00000002-AUDIO-*.txt  # transcriptions live alongside audio
```

## Markdown format

```markdown
**John:**
[08/04/2026, 14:30:00] Hello there
[08/04/2026, 14:31:00] [Photo](exported/00000001-PHOTO-abc.jpg)
[08/04/2026, 14:32:00] 🎤 "Transcribed voice message text here"
> Audio: [exported/00000003-AUDIO-abc.opus](exported/00000003-AUDIO-abc.opus)
[08/04/2026, 14:33:00] [Document: contract.pdf](exported/00000005-DOC-contract.pdf)
[08/04/2026, 14:34:00] [Voice message](exported/00000004-AUDIO-def.opus)

**Jane:**
[08/04/2026, 14:35:00] Got it, thanks!
```

Messages are grouped by sender — the name only appears when the sender changes. Non-transcribed voice messages appear as `[Voice message](exported/AUDIO-xxx.opus)`.

## Reading processed conversations

- Chunk files are ~100KB each — read them sequentially or search with Grep
- `ls *.md` in the output folder shows date ranges at a glance
- **Images:** Read tool (multimodal — reads directly from exported/)
- **PDFs:** Read tool (native PDF support from exported/)
- **Videos:** Cannot be read — note and move on
- **Audio:** Read the transcription inline in the markdown, or read the `.txt` file in exported/

## Dependency Check

```bash
${CLAUDE_SKILL_DIR}/scripts/check-deps.sh
```

Run this before processing to verify all tools are available.

## Whisper Setup

Transcription uses **whisper.cpp** locally. Fully offline — no API keys needed.

**First-time setup** (requires `ffmpeg` and `cmake` — install with `brew install ffmpeg cmake`):

Check if whisper.cpp is already installed (`~/.whisper.cpp/build/bin/whisper-cli` or locally in the skill directory). If not found, ask the user whether to install **shared** (`~/.whisper.cpp`, reusable across projects) or **local** (inside the skill directory). Then run:

```bash
${CLAUDE_SKILL_DIR}/scripts/setup.sh --shared   # installs to ~/.whisper.cpp
${CLAUDE_SKILL_DIR}/scripts/setup.sh --local     # installs to skill directory
```

This clones whisper.cpp, builds it, and downloads the large-v3 model (~3GB). Guide the user through installation if prerequisites are missing.

**Performance:** ~2-10 seconds per voice message on Apple Silicon.

## Localization

The parser handles multiple languages for attachment markers:
- EN: `<attached: filename>`
- PT-BR: `<anexado: filename>`
- ES: `<archivo adjunto: filename>`

## Tips

- Payment receipts are usually photos (`PHOTO-`) sent right after messages mentioning amounts
- Photos can be documents — screenshots, photos of paper, receipts
- Financial information often appears in message text, not just in attachments
- Filenames may have corrupted accented characters — this is normal
