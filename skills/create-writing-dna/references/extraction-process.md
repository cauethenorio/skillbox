# Extraction process

The full workflow that turns a corpus into a portable voice skill. Passes 2-3 are interactive; quick mode runs Pass 1 only.

## Pass 0 — Corpus assembly
Follow `source-discovery.md`. Assemble the samples the user selects (target 10+ across 2+ media). Confirm every sample is the user's own, human-written content. Exclude AI-assisted text.

## Pass 1 — Analyze (automated)
1. Read every selected sample.
2. Extract the 8 dimensions (see `analysis-dimensions.md`).
3. Classify every pattern VOICE / PLATFORM / BORDERLINE. Keep VOICE, filter PLATFORM (document it), flag BORDERLINE for Pass 2.
4. Build the personalized ban-list: start from `llm-isms.md`, remove words the person genuinely uses (note the exception with context), add personal tics found in the corpus. Build an English list and a Portuguese list (or whatever languages apply).
5. Draft `writing-dna.md` from `templates/voice-skill/writing-dna.md.tmpl` — ban-lists first, every pattern citing evidence ("seen in N/M <channel>").

## Pass 2 — Human review
- Present the draft. The person marks items: **WRONG / OVERSTATED / MISSING / NEEDS_NUANCE**.
- Revise accordingly. On WRONG, defer to the person over the corpus ("you know your own writing better than the corpus shows"). Mark each change with a brief inline note so it's auditable.

## Pass 3 — Calibration
- Generate per-channel calibration samples (≥120 words each, no meta-commentary inside the samples — they should read as if the person wrote them). Include bilingual samples (one casual, one professional, one code-switching) if applicable. Label each sample with the patterns it tests.
- The person tags each sample **GOOD / CLOSE / OFF**, plus line-level labels: **TOO_FORMAL / TOO_CASUAL / WRONG_WORD / LLM_ISM / NOT_ME / MISSING_PATTERN**.
- Map labels to DNA sections and fold the feedback in:

  | Label | Fix in DNA section |
  |-------|--------------------|
  | TOO_FORMAL / TOO_CASUAL | §6 channel modes (and §5 language register) |
  | WRONG_WORD / LLM_ISM | §1 ban-list |
  | NOT_ME | §4 core voice patterns |
  | MISSING_PATTERN | add to §4 or §5 |

- Finalize the DNA file.

## Quick mode
Pass 1 only. Emit the DNA with metadata `readiness: minimum-viable`, skip Pass 2/3. Tell the user they can run the full passes later to upgrade the profile.

## Emit the voice skill (final step of every run)
1. Choose the person's kebab name (`{{name}}`) and display name (`{{Name}}`); note the languages and possessive.
2. Create the skill directory `~/.claude/skills/<name>-voice/` (or a user-chosen `skills/` dir).
3. Write `writing-dna.md` (finalized).
4. Copy `generating.md` **verbatim** from `templates/voice-skill/`.
5. Render `SKILL.md` from `SKILL.md.tmpl`, filling `{{name}}` / `{{Name}}` / `{{languages}}` / `{{their}}`.
6. Tell the user the folder is portable: copy it into any `skills/` directory and the voice works standalone, with no external dependency.

## Bilingual handling
One DNA file covers all languages. For a language with thin or no samples, write `INFERRED` patterns marked `<!-- INFERRED -->` (based on the primary-language voice plus standard conventions for the secondary language) and validate them in Pass 3.
