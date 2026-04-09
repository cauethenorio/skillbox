# Skillbox

A collection of foundational [Claude Code](https://claude.ai/code) skills — general-purpose building blocks that other skills and workflows can build on.

## Skills

| Skill | Description |
|-------|-------------|
| [browse](skills/browse/) | Browser automation via Playwright — navigate websites, fill forms, take screenshots, and extract data. |
| [clean-commit](skills/clean-commit/) | Clean, atomic commits following project conventions with secret detection. |
| [dedup-files](skills/dedup-files/) | Find and deduplicate files in a project — replaces copies with symlinks, respects .gitignore and common exclusions. |
| [managing-todos](skills/managing-todos/) | Lightweight todo tracking using markdown files. Captures things noticed during a session to tackle later. |
| [read-pdf](skills/read-pdf/) | Extract text, tables, and structured data from PDF files using pdfplumber. |
| [read-whatsapp-export](skills/read-whatsapp-export/) | Process exported WhatsApp conversations into clean markdown with transcribed voice messages. Fully offline. |
| [use-gmail](skills/use-gmail/) | Search, read, draft, send, and download attachments from Gmail via Google Workspace CLI. |

## Installation

```bash
npx skills add https://github.com/cauethenorio/skillbox
```
