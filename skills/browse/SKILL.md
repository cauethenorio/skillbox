---
name: browse
description: Use when needing to automate browser interactions, navigate websites, fill forms, take screenshots, extract data from web pages, or manage browser sessions via Playwright
allowed-tools: Bash(**/browse.sh*:*)
---

# Browser Automation with @playwright/cli

All commands use `browse.sh` — a wrapper script bundled with this skill that calls `npx @playwright/cli` with the correct config. The config enables headed mode, persistent sessions, and stores all data in the project's `.playwright/data/` directory.

## Project conventions

- Use `browse.sh` from this skill's base directory (shown as `Base directory for this skill:` when loaded) for all commands:
  ```bash
  <skill-base-dir>/browse.sh open <url>
  ```
- Session data is stored in `.playwright/data/session/` and snapshots in `.playwright/data/output/` relative to the working directory.

Check `## Browser testing` in CLAUDE.md for project-specific overrides (base URL, browser choice, dev server instructions).

## Quick start

```bash
# Open browser
<skill-base-dir>/browse.sh open
# Open browser and navigate
<skill-base-dir>/browse.sh open https://example.com
# Interact with elements using refs from the snapshot
<skill-base-dir>/browse.sh click e15
<skill-base-dir>/browse.sh fill e5 "search query"
<skill-base-dir>/browse.sh press Enter
# Take a snapshot to see current state
<skill-base-dir>/browse.sh snapshot
# Close the browser
<skill-base-dir>/browse.sh close
```

## Commands

### Core

```bash
browse.sh open
browse.sh open https://example.com/
browse.sh goto https://playwright.dev
browse.sh type "search query"
browse.sh click e3
browse.sh dblclick e7
browse.sh fill e5 "user@example.com"
browse.sh drag e2 e8
browse.sh hover e4
browse.sh select e9 "option-value"
browse.sh upload ./document.pdf
browse.sh check e12
browse.sh uncheck e12
browse.sh snapshot
browse.sh snapshot --filename=after-click.yaml
browse.sh eval "document.title"
browse.sh eval "el => el.textContent" e5
browse.sh dialog-accept
browse.sh dialog-accept "confirmation text"
browse.sh dialog-dismiss
browse.sh resize 1920 1080
browse.sh close
```

### Navigation

```bash
browse.sh go-back
browse.sh go-forward
browse.sh reload
```

### Keyboard

```bash
browse.sh press Enter
browse.sh press ArrowDown
browse.sh keydown Shift
browse.sh keyup Shift
```

### Mouse

```bash
browse.sh mousemove 150 300
browse.sh mousedown
browse.sh mousedown right
browse.sh mouseup
browse.sh mouseup right
browse.sh mousewheel 0 100
```

### Save as

Always save screenshots to `.playwright/data/screenshots/`.

```bash
browse.sh screenshot --filename=.playwright/data/screenshots/page.png
browse.sh screenshot e5 --filename=.playwright/data/screenshots/element.png
browse.sh pdf --filename=page.pdf
```

### Tabs

```bash
browse.sh tab-list
browse.sh tab-new
browse.sh tab-new https://example.com/page
browse.sh tab-close
browse.sh tab-close 2
browse.sh tab-select 0
```

### Storage

```bash
browse.sh state-save
browse.sh state-save auth.json
browse.sh state-load auth.json

# Cookies
browse.sh cookie-list
browse.sh cookie-list --domain=example.com
browse.sh cookie-get session_id
browse.sh cookie-set session_id abc123
browse.sh cookie-set session_id abc123 --domain=example.com --httpOnly --secure
browse.sh cookie-delete session_id
browse.sh cookie-clear

# LocalStorage
browse.sh localstorage-list
browse.sh localstorage-get theme
browse.sh localstorage-set theme dark
browse.sh localstorage-delete theme
browse.sh localstorage-clear

# SessionStorage
browse.sh sessionstorage-list
browse.sh sessionstorage-get step
browse.sh sessionstorage-set step 3
browse.sh sessionstorage-delete step
browse.sh sessionstorage-clear
```

### Network

```bash
browse.sh route "**/*.jpg" --status=404
browse.sh route "https://api.example.com/**" --body='{"mock": true}'
browse.sh route-list
browse.sh unroute "**/*.jpg"
browse.sh unroute
```

### DevTools

```bash
browse.sh console
browse.sh console warning
browse.sh network
browse.sh run-code "async page => await page.context().grantPermissions(['geolocation'])"
browse.sh tracing-start
browse.sh tracing-stop
browse.sh video-start
browse.sh video-stop video.webm
```

## Open parameters

```bash
# Use specific browser when creating session
browse.sh open --browser=chrome
browse.sh open --browser=firefox
browse.sh open --browser=webkit
browse.sh open --browser=msedge
# Connect to browser via extension
browse.sh open --extension

# Delete user data for the default session
browse.sh delete-data
```

## Snapshots

After each command, a snapshot of the current browser state is provided.

```bash
> browse.sh goto https://example.com
### Page
- Page URL: https://example.com/
- Page Title: Example Domain
### Snapshot
[Snapshot](.playwright/data/output/page-2026-02-14T19-22-42-679Z.yml)
```

You can also take a snapshot on demand using `browse.sh snapshot`.

If `--filename` is not provided, a new snapshot file is created with a timestamp. Default to automatic file naming, use `--filename=` when artifact is a part of the workflow result.

## Browser Sessions

```bash
# create new browser session named "mysession"
browse.sh -s=mysession open example.com
browse.sh -s=mysession click e6
browse.sh -s=mysession close
browse.sh -s=mysession delete-data

browse.sh list
# Close all browsers
browse.sh close-all
# Forcefully kill all browser processes
browse.sh kill-all
```

## Example: Form submission

```bash
browse.sh open https://example.com/form
browse.sh snapshot

browse.sh fill e1 "user@example.com"
browse.sh fill e2 "password123"
browse.sh click e3
browse.sh snapshot
browse.sh close
```

## Example: Multi-tab workflow

```bash
browse.sh open https://example.com
browse.sh tab-new https://example.com/other
browse.sh tab-list
browse.sh tab-select 0
browse.sh snapshot
browse.sh close
```

## Example: Debugging with DevTools

```bash
browse.sh open https://example.com
browse.sh click e4
browse.sh fill e7 "test"
browse.sh console
browse.sh network
browse.sh close
```

```bash
browse.sh open https://example.com
browse.sh tracing-start
browse.sh click e4
browse.sh fill e7 "test"
browse.sh tracing-stop
browse.sh close
```

## Specific tasks

- **Browser session management** [references/session-management.md](references/session-management.md)
- **Request mocking** [references/request-mocking.md](references/request-mocking.md)
- **Running Playwright code** [references/running-code.md](references/running-code.md)
- **Storage state (cookies, localStorage)** [references/storage-state.md](references/storage-state.md)
- **Test generation** [references/test-generation.md](references/test-generation.md)
- **Tracing** [references/tracing.md](references/tracing.md)
- **Video recording** [references/video-recording.md](references/video-recording.md)
