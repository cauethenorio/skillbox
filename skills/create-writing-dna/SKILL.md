---
name: create-writing-dna
description: Use when someone wants to capture their personal writing voice/style so Claude can write as them — building a "writing DNA" from their past emails, chat, posts, and docs across multiple media, and generating a portable per-person voice skill. Also use to refresh or upgrade an existing voice profile.
---

# Create Writing DNA

## Overview
Extract a person's writing voice from their real samples across multiple media, then emit a **portable per-person voice skill** — a `<name>-voice/` folder containing `SKILL.md` (trigger), `writing-dna.md` (the voice profile), and `generating.md` (the generation workflow). The folder has zero external dependencies: copy it into any `skills/` directory and the voice works standalone.

## When to use
- "Help Claude write like me" / "in my voice" / "match my writing style"
- Building or refreshing a personal/teammate voice profile from past writing
- Bilingual writers who need code-switching captured (e.g. PT/EN)

**Not for:** one-off ghostwriting with no profile, or generic marketing copy.

## Workflow
1. **Assemble the corpus** — discover the user's own writing generically. See `references/source-discovery.md`.
2. **Run the passes** — Pass 0-3 (or quick mode). See `references/extraction-process.md`.
3. **Apply the 8 dimensions + VOICE/PLATFORM/BORDERLINE classification.** See `references/analysis-dimensions.md`.
4. **Personalize the ban-list** from the base list. See `references/llm-isms.md`.
5. **Emit the voice skill** from `templates/voice-skill/` (fill `SKILL.md.tmpl`, write `writing-dna.md`, copy `generating.md` verbatim). See the "Emit" section of `references/extraction-process.md`.

## Key rules
- **Ban-lists first** in the DNA file; earlier constraints bind hardest.
- **Cite evidence** for every pattern ("seen in N/M <channel>").
- **Only the user's own, human-written content** — never received text, never AI-assisted samples.
- **Never hard-code tool/skill/MCP names** — discover what's available at runtime.
- **One DNA file for all languages**, with language-specific subsections.

## Output
A portable `<name>-voice/` skill folder (default `~/.claude/skills/<name>-voice/`). This is personal output — it is not committed to this repo.
