# Analysis dimensions & pattern classification

## The 8 analysis dimensions

Extract each dimension from the corpus:

- **A. Sentence patterns** — average length, variation/burstiness, use of short punchy sentences vs long explanatory ones, fragments, parenthetical asides, how lists are handled.
- **B. Opening patterns** — how each format starts (blog, chat, email, doc). First-sentence structure. Greeting vs jump-straight-in vs context-set-first.
- **C. Vocabulary fingerprint** — recurring words/phrases, technical-term handling (explain jargon or assume it?), informal language, code-switching between languages.
- **D. Structural patterns** — how information is organized (chronological, importance-first, problem-solution), use of headers, bullets, numbered lists.
- **E. Tone markers** — formality level per content type, humor, directness, how disagreement is handled, how uncertainty is expressed.
- **F. Formatting habits** — bold usage, caps, emoji, punctuation quirks (Oxford comma? em-dash vs colon?), code blocks.
- **G. Language-specific patterns** — does the person code-switch? Which words stay in the other language? Does formality differ between languages? Greeting/closing conventions per language.
- **H. LLM-ism presence** — flag any patterns that look AI-generated. These may indicate AI-assisted samples (exclude them) or be false positives from common business language. Note, don't filter yet.

## Classification — VOICE / PLATFORM / BORDERLINE

Classify every extracted pattern:

- **VOICE** — appears across multiple content types, OR deviates from the platform norm for that type. Genuine personal voice. → **KEEP**.
- **PLATFORM** — appears in only one content type AND matches that platform's standard convention (short Slack messages, formal email greetings, lowercase chat). Not voice, just the platform. → **FILTER OUT** (but document for transparency).
- **BORDERLINE** — mostly one content type but seems a deliberate choice rather than a convention (unusually formal Slack, emoji in technical docs, first-name-only email sign-off). → **FLAG** for human review in Pass 2.

## Evidence rule

Every retained pattern must cite corpus evidence, e.g. "seen in 8/12 blog posts" or "seen in 3/3 samples". No evidence → don't assert it.

## Why this matters

Separating genuine voice from platform convention is what makes multi-media extraction work. Without it, you bake each platform's conventions in as if they were the person — and the generated voice writes every channel like the channel it came from, not like the person.
