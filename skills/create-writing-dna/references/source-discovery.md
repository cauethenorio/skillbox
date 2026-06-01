# Source discovery (generic)

**CRITICAL:** Do NOT hard-code tool, skill, or MCP names. They differ from person to person and change over time. Discover what is available at runtime and use whatever fits. The names mentioned below are **illustrative examples only**, never a fixed or required list.

## Discovery strategy

1. **Inspect what's available.** Look at the skills and MCP tools present in the current environment (the harness lists them). Identify any that can read or fetch text the user produced.
2. **Classify usable sources by content kind**, not by tool name. Kinds of user-authored content worth gathering:
   - sent email
   - chat / messaging the user wrote
   - documents the user authored
   - code-review / pull-request text the user wrote
   - published posts or articles
   - exported archives the user provides
   *(Illustrative tool shapes that might surface these — an email tool, a chat-export reader, a docs/drive tool, a git-host CLI, a browser tool. Treat as examples; match to whatever actually exists.)*
3. **Retrieve candidates.** For each usable source, pull a batch of samples **authored by the user** (sent / written by them — never received).
4. **Let the user pick.** Present candidates grouped by channel; the user selects which to include in the corpus.
5. **Fallback.** If no suitable tool exists for a channel, tell the user to drop files into `corpus/<channel>/` by hand.

## Guardrails

- **Only the user's own authored content.** Never received messages, never other people's text.
- **Exclude AI-assisted writing** — it poisons the extraction by reflecting model patterns back. Ask the user to confirm samples are human-written; when in doubt, exclude.
- **Redact PII/secrets** before analysis. Keep the corpus local.

## Coverage target

10+ samples across 2+ media, recent (~last 2 years), a mix of short and long. Minimum viable: 5 documents across 2 content types (lower confidence — lean harder on Pass 2/3 review).
