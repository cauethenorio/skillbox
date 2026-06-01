# Generating in this voice

This file is copied verbatim into every voice skill. It is person-agnostic and refers to `writing-dna.md` as a sibling file in the same directory.

## 1. Load & gate
- Read the sibling `writing-dna.md`.
- **Missing or unreadable → STOP.** Tell the user to build a profile first with `create-writing-dna`. Do not improvise a voice.
- Readiness `minimum-viable` → proceed, but state the accuracy caveat up front.
- Metadata `created` date 6+ months old → flag staleness ("this profile is N months old; consider a refresh"), then proceed with awareness.

## 2. Scope the task
- Determine the target channel/format, audience, and language. Ask only if unclear.
- Select the matching channel mode (§6) and language section (§5) from the DNA. Name the mode you picked so the choice is auditable.

## 3. Optional content seed
- Offer to seed with a short snippet of the user's own prior text on the topic. Starting from their real words is the single most effective lever for sounding human. Optional — skip if none.

## 4. Draft
- Produce ONE polished draft in voice. Generate variants only if asked.

## 5. Two-pass self-review (mandatory — two SEPARATE passes)
- **Pass A — LLM-isms.** Check the draft against the DNA's ban-list (§1). Count before flagging; consolidate stacked tells into one; apply the em-dash rule.
- **Pass B — performative tells.** Remove anything trying too hard to sound like a character rather than the person. Cut announced narrative and inflated tics.
- Run both passes every time, even for a one-line message. **Violating the letter of the ban-list is violating the spirit** — don't skip a pass because the draft "looks fine."

## 6. Capture habit
- If the user edits the draft before using it, offer to append the (draft → their final) pair into the DNA's `## 7. Drafted vs Sent` section, with a one-line lesson. This is the only post-creation write to the DNA file, and it sharpens the voice over time.
