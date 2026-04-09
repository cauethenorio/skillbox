---
name: dedup-files
description: Find and deduplicate files in a project using jdupes. Use this skill whenever the user mentions duplicate files, file deduplication, saving disk space by removing copies, finding identical files, or cleaning up repeated documents in a repo — even if they don't mention jdupes specifically. Especially relevant for documentation-heavy repos with PDFs or other large binary files that may have been copied around.
---

## Overview

Find duplicate files in a project and replace them with symlinks using `jdupes`. This preserves all file paths (nothing disappears) while reclaiming disk space. The original file is kept; copies become symlinks pointing to it.

The workflow is always: **scan first, confirm with the user, then act**. Never modify the filesystem without explicit approval.

## Prerequisites

`jdupes` must be installed. Check with:

```bash
jdupes --version
```

If not installed:
- macOS: `brew install jdupes`
- Debian/Ubuntu: `apt install jdupes`

## Workflow

### Step 1: Build the exclusion list

Start by assembling jdupes flags to skip irrelevant directories. Always include these baseline exclusions:

```bash
-A               # skip hidden files/dirs (covers .git, .DS_Store, etc.)
-X nostr:node_modules/
```

Then check if a `.gitignore` exists in the target directory. If it does, parse it for additional directory patterns and add them as `-X nostr:` flags. Focus on directory-level ignores (lines ending in `/` or common build output dirs like `dist/`, `build/`, `__pycache__/`). Skip complex glob patterns — the goal is to avoid scanning obvious junk, not to replicate gitignore semantics perfectly.

### Step 2: Scan for duplicates (dry run)

Run jdupes in preview mode — no action flags, just list what it finds:

```bash
jdupes -r -S -A -X nostr:node_modules/ [other -X flags] <target-dir>
```

Flags:
- `-r` — recurse into subdirectories
- `-S` — show file sizes (helps the user understand the impact)
- `-A` — skip hidden files

This prints groups of duplicate files separated by blank lines. Parse the output and present a clear summary to the user:

- How many duplicate groups were found
- Total space that would be saved
- For each group: the file size and the list of paths

If no duplicates are found, say so and stop.

### Step 3: Confirm with the user

Present the duplicate groups and explain what will happen: for each group, one file will be kept as-is and the others will be replaced with symlinks pointing to it. All paths will continue to work — nothing is deleted.

Ask the user to confirm before proceeding. If they want to exclude specific groups or files, adjust accordingly.

### Step 4: Replace duplicates with symlinks

Once confirmed, run jdupes with the symlink flag:

```bash
jdupes -r -l -A -X nostr:node_modules/ [other -X flags] <target-dir>
```

The `-l` (lowercase L) flag replaces duplicates with soft symlinks. jdupes keeps the first file in each group as the original and symlinks the rest to it.

#### Controlling which file is kept as the original

By default jdupes picks the original by filename sort order. Use these flags to control it:

- **`-O` (param-order)** — the directory listed first on the command line gets priority. If the user says "keep the files in `docs/` as originals", list `docs/` first:
  ```bash
  jdupes -r -l -O -A docs/ other-dir/
  ```
- **`-o time`** — keep the oldest file as the original (by modification time)
- **`-oi time`** — keep the newest file (reverse/invert sort)

If the user specifies which file or directory should be the source of truth, always use `-O` with that directory listed first. Never fall back to `ln -s` manually — jdupes handles symlinking correctly and atomically.

### Step 5: Report results

After symlinking, report:
- How many files were symlinked
- How much space was saved
- Remind the user that all original paths still work via symlinks

If the project is a git repo, mention that they should run `git status` to review the changes before committing — git will show the symlinked files as modified.

## Important notes

- **Never use `-d` (delete mode).** Always use `-l` (symlink) to preserve all file paths.
- **Always preview before acting.** The scan step (no action flags) must come first.
- **Always get user confirmation** between the scan and the symlink step.
- If the user asks to deduplicate a specific subdirectory, scope the scan to that directory rather than the whole project.
- If jdupes is not installed, guide the user through installation before proceeding.
