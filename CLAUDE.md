## What This Repo Is

A collection of reusable foundational Claude Code skills.
Each skill lives in its own directory under `skills/` and consists of a `SKILL.md` (frontmatter + instructions) and supporting scripts.

## Structure

- `skills/<skill-name>/SKILL.md` — Skill definition with YAML frontmatter (`name`, `description`) and usage instructions
- `skills/<skill-name>/` — Supporting scripts and files for that skill

## Adding a New Skill

1. Create `skills/<skill-name>/SKILL.md` with frontmatter (`name`, `description`) and usage docs
2. Add any supporting scripts in the same directory
3. Skills are activated by copying/symlinking into `~/.claude/skills/`
