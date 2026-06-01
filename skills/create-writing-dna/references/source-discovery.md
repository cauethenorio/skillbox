# Source discovery (generic)

**CRITICAL:** Do NOT hard-code tool, skill, or MCP names. They differ from person to person and change over time. Discover what is available at runtime and use whatever fits. The names mentioned below are **illustrative examples only**, never a fixed or required list.

## Discovery strategy

1. **Inspect what's available.** Look at the skills and MCP tools present in the current environment (the harness lists them). Identify any that can read or fetch text the user produced.
2. **Classify usable sources by content kind**, not by tool name. Kinds of user-authored content worth gathering, **most-to-least valuable for voice**:
   - **chat / messaging the user wrote — the PRIMARY source.** Real-time DMs/messages are the least-edited, most natural writing a person produces; they carry tone, slang, code-switching, and humor that polished channels strip out. Lead with it whenever a chat source exists, and weight it heaviest in analysis.
   - sent email
   - code-review / pull-request text the user wrote
   - documents the user authored
   - published posts or articles
   - exported archives the user provides
   *(Illustrative tool shapes that might surface these — a chat/messaging tool, an email tool, a docs/drive tool, a git-host CLI, a browser tool. Treat as examples; match to whatever actually exists, and never hard-code a product name.)*
3. **Retrieve candidates.** For each usable source, pull a batch of samples **authored by the user** (sent / written by them — never received).
4. **Let the user pick.** Present candidates grouped by channel; the user selects which to include in the corpus.
5. **Fallback.** If no suitable tool exists for a channel, tell the user to drop files into the working corpus dir by hand, under a `<channel>/` subfolder (see "Where the corpus lives" below).

## Where the corpus lives

The working corpus is **sensitive, transient scratch data** — it contains the user's real private writing (personal finances, addresses, family/work messages). Store it accordingly:

- Use a **throwaway temp/scratch directory** (e.g. under the OS temp dir), one `<channel>/` subfolder per source. **Never** put it in the user's home root, the Desktop, or inside a git repository (it can get committed, and the skill's own `corpus/` path is NOT a repo subdir).
- **Delete the working corpus at the end of the run** — this is a required final step. The only durable output is the portable `<name>-voice/` skill.
- If the user wants it kept for auditability, get explicit confirmation and leave it in the temp dir; still never the repo or home root.

## Guardrails

- **Only the user's own authored content.** Never received messages, never other people's text.
- **Exclude AI-assisted writing** — it poisons the extraction by reflecting model patterns back. Ask the user to confirm samples are human-written; when in doubt, exclude.
- **Redact PII/secrets** before analysis, and keep the corpus local (see "Where the corpus lives").

## Coverage target

10+ samples across 2+ media, recent (~last 2 years), a mix of short and long. Minimum viable: 5 documents across 2 content types (lower confidence — lean harder on Pass 2/3 review).
