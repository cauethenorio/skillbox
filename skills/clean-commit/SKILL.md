---
name: clean-commit
description: Create clean, atomic commits following project conventions. Use when committing code changes, staging files, or writing commit messages.
---

# Clean Commit

Create clean, atomic commits that follow the project's conventions. One logical change per commit.

Do not include references to Claude or AI in commit messages. Do not add Co-Authored-By lines or AI attribution signatures.

## Commit Format

Use the project's commit format if defined under `## Commit conventions` in CLAUDE.md.

If no project format is specified, use conventional commits:

```
<type>(<scope>): <short description>

<optional body explaining why>

<optional footer with ticket references>
```

Types: `feat`, `fix`, `ref`, `docs`, `test`, `chore`

- Title 50 characters or less
- Imperative mood ("Add feature" not "Added feature")
- Focus on the "why", not the "what" -- the diff shows the what
- Reference tickets when applicable (`Refs PROJ-1234`)

## Security Check

Before staging any file, check for potential secrets.

**File patterns to block:**

- `.env`, `.env.*`
- `credentials.*`, `secrets.*`
- `*_key.pem`, `*.p12`

**Content patterns to detect:**

- `API_KEY=`, `SECRET_KEY=`, `PASSWORD=`, `TOKEN=`
- `-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----`
- AWS access keys (`AKIA...`)
- GitHub tokens (`ghp_...`, `gho_...`)
- Stripe keys (`sk_live_...`)
- Database connection strings with embedded passwords
- High-entropy strings that look like credentials

**If potential secrets are found:**

1. **Do NOT stage the file**
2. Explain what was detected and why it's risky
3. Suggest adding the file or pattern to `.gitignore`
4. Ask the developer how to proceed

## Process

### 1. Review changes

- Run `git status` to see all changed files
- Run `git diff` to see staged and unstaged changes
- Understand what changed and why
- If changes span multiple unrelated concerns, ask the developer if they should be separate commits

### 2. Stage files

- `git add <specific files>` -- never `git add .`
- Group files by logical change
- Run the Security Check on every file before staging
- If changes span multiple logical units, split into multiple commits

### 3. Draft commit message

- Follow the Commit Format section above
- Reference tickets when applicable (e.g., `Refs PROJ-1234`)
- Keep the body concise -- avoid long paragraphs

### 4. Confirm with the developer

- Show the staged files and proposed commit message
- Wait for approval before executing
- Never commit without confirmation

### 5. Execute and verify

- Create the commit
- Run `git log -1` to confirm the commit was created
- Run `git status` to verify clean state

## Examples

### Feature Commit

```
feat(auth): add password reset flow

Implements forgot password functionality with email verification.
Users can now request a password reset link sent to their email.

Refs PROJ-1234
```

### Bug Fix Commit

```
fix(api): handle null response in user endpoint

The user endpoint could return null for soft-deleted accounts,
causing dashboard crashes when accessing user properties.

Fixes PROJ-5678
```

### Refactor Commit

```
ref: extract validation logic to shared module

Moves duplicate validation code into a shared validator class.
No behavior change.
```

## Key Principles

- **Atomic** -- one logical change per commit
- **Never commit secrets** -- check for .env, credentials, API keys
- **No AI references** -- do not mention Claude or AI in commit messages, no Co-Authored-By
- **Confirm first** -- always show the developer what you're about to commit
- **Message explains why** -- the diff shows what changed, the message explains the reason
- **Project conventions win** -- if CLAUDE.md specifies a format, use it
