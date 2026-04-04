---
name: read-pdf
description: Use when needing to extract text, tables, or structured data from PDF files, as a fallback when the built-in Read tool cannot handle the PDF
---

## Overview

Extract text from PDF files using `uvx pdfplumber`. No package installation required — `uvx` runs directly from PyPI.

## First usage

Before running any command, verify `uvx` is available:

```bash
uvx --version
```

If not installed, install `uv` first: `curl -LsSf https://astral.sh/uv/install.sh | sh`

## Quick reference

```bash
# Text from all pages
uvx pdfplumber file.pdf --format text

# Specific pages (1-indexed)
uvx pdfplumber file.pdf --format text --pages 1 3 5

# Structured data (JSON with position of each character)
uvx pdfplumber file.pdf --format json --pages 1

# Document tree with text
uvx pdfplumber file.pdf --structure-text --pages 1
```

## Options

| Flag | Description |
|---|---|
| `--format text` | Plain text (best for general reading) |
| `--format json` | JSON with element attributes (position, font, size) |
| `--format csv` | CSV of elements |
| `--pages N [N ...]` | Specific pages, 1-indexed. No flag = all |
| `--structure-text` | Structural tree of the PDF with text (useful for tagged PDFs) |
| `--types char line rect` | Filter element types (for JSON/CSV) |

## When to use each format

- **`--format text`**: general reading, extracting data from reports, searching for values
- **`--format json`**: when you need exact element positions (e.g. poorly formatted tables)
- **`--structure-text`**: returns semantic tree (Div, H2, P) but without inline text — rarely useful in practice

## Common mistakes

- **File as second argument**: the file must come BEFORE flags (`uvx pdfplumber file.pdf --format text`, not `uvx pdfplumber --format text file.pdf --pages 1`)
- **0-indexed pages**: pages are 1-indexed, not 0-indexed. Page 0 returns empty
- **PDF without text**: scanned PDFs (images) return empty. In that case, use OCR
