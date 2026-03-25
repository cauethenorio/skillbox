#!/usr/bin/env bash
set -euo pipefail

# Todo manager — validates and manages markdown todo files
# Reads config from CLAUDE.md if present (## Todos section)

# Defaults
TODO_DIR="docs/todos"
DONE_DIR="docs/todos/done"
VALID_STATUSES="open in-progress done"
VALID_PRIORITIES="low medium high"

# Try to read config from CLAUDE.md
load_config() {
  local claude_md=""
  for f in CLAUDE.md claude.md; do
    if [[ -f "$f" ]]; then
      claude_md="$f"
      break
    fi
  done
  [[ -z "$claude_md" ]] && return

  local in_todos=false
  while IFS= read -r line; do
    if [[ "$line" =~ ^##[[:space:]]+Todos ]]; then
      in_todos=true
      continue
    fi
    if $in_todos && [[ "$line" =~ ^## ]]; then
      break
    fi
    if $in_todos; then
      if [[ "$line" =~ ^-[[:space:]]*directory:[[:space:]]*(.*) ]]; then
        TODO_DIR="${BASH_REMATCH[1]%/}"
        DONE_DIR="${TODO_DIR}/done"
      fi
      if [[ "$line" =~ ^-[[:space:]]*statuses:[[:space:]]*(.*) ]]; then
        VALID_STATUSES="${BASH_REMATCH[1]//,/ }"
      fi
    fi
  done < "$claude_md"
}

load_config

usage() {
  cat <<EOF
Usage: todo.sh <command> [options]

Commands:
  create  -t <title> [-p priority] [-s status] [--tags tag1,tag2] [-d description]
  list    [-s status] [-p priority] [--tag tag]
  update  <file> [-s status] [-p priority] [--tags tag1,tag2]
  archive <file>

Defaults:
  directory:  $TODO_DIR
  statuses:   $VALID_STATUSES
  priorities: $VALID_PRIORITIES
EOF
  exit 1
}

validate_status() {
  local status="$1"
  for s in $VALID_STATUSES; do
    [[ "$s" == "$status" ]] && return 0
  done
  echo "Error: invalid status '$status'. Valid: $VALID_STATUSES" >&2
  exit 1
}

validate_priority() {
  local priority="$1"
  for p in $VALID_PRIORITIES; do
    [[ "$p" == "$priority" ]] && return 0
  done
  echo "Error: invalid priority '$priority'. Valid: $VALID_PRIORITIES" >&2
  exit 1
}

slugify() {
  echo "$1" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//' | cut -c1-50
}

cmd_create() {
  local title="" priority="medium" status="open" tags="" description=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -t) title="$2"; shift 2 ;;
      -p) priority="$2"; shift 2 ;;
      -s) status="$2"; shift 2 ;;
      --tags) tags="$2"; shift 2 ;;
      -d) description="$2"; shift 2 ;;
      *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
  done

  [[ -z "$title" ]] && { echo "Error: -t <title> is required" >&2; exit 1; }
  validate_status "$status"
  validate_priority "$priority"

  local today
  today=$(date +%Y-%m-%d)
  local slug
  slug=$(slugify "$title")
  local filename="${today}-${slug}.md"

  mkdir -p "$TODO_DIR"

  local tags_yaml="[]"
  if [[ -n "$tags" ]]; then
    tags_yaml="[$(echo "$tags" | sed 's/,/, /g')]"
  fi

  local body="${description:-$title}"

  cat > "${TODO_DIR}/${filename}" <<EOF
---
status: ${status}
priority: ${priority}
created: ${today}
tags: ${tags_yaml}
---

# ${title}

${body}
EOF

  echo "Created: ${TODO_DIR}/${filename}"
}

cmd_list() {
  local filter_status="" filter_priority="" filter_tag=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -s) filter_status="$2"; shift 2 ;;
      -p) filter_priority="$2"; shift 2 ;;
      --tag) filter_tag="$2"; shift 2 ;;
      *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
  done

  [[ -n "$filter_status" ]] && validate_status "$filter_status"
  [[ -n "$filter_priority" ]] && validate_priority "$filter_priority"

  if [[ ! -d "$TODO_DIR" ]]; then
    echo "No todos directory found at $TODO_DIR"
    exit 0
  fi

  local count=0
  local output=""

  for file in "$TODO_DIR"/*.md; do
    [[ ! -f "$file" ]] && continue

    local status="" priority="" created="" tags="" heading=""
    local in_frontmatter=false
    local frontmatter_done=false

    while IFS= read -r line; do
      if [[ "$line" == "---" ]] && ! $in_frontmatter; then
        in_frontmatter=true
        continue
      fi
      if [[ "$line" == "---" ]] && $in_frontmatter; then
        frontmatter_done=true
        continue
      fi
      if $in_frontmatter && ! $frontmatter_done; then
        if [[ "$line" =~ ^status:[[:space:]]*(.*) ]]; then
          status="${BASH_REMATCH[1]}"
        elif [[ "$line" =~ ^priority:[[:space:]]*(.*) ]]; then
          priority="${BASH_REMATCH[1]}"
        elif [[ "$line" =~ ^created:[[:space:]]*(.*) ]]; then
          created="${BASH_REMATCH[1]}"
        elif [[ "$line" =~ ^tags:[[:space:]]*(.*) ]]; then
          tags="${BASH_REMATCH[1]}"
          tags="${tags#\[}"
          tags="${tags%\]}"
        fi
      fi
      if $frontmatter_done && [[ "$line" =~ ^#[[:space:]]+(.*) ]] && [[ -z "$heading" ]]; then
        heading="${BASH_REMATCH[1]}"
      fi
    done < "$file"

    # Apply filters
    [[ -n "$filter_status" && "$status" != "$filter_status" ]] && continue
    [[ -n "$filter_priority" && "$priority" != "$filter_priority" ]] && continue
    [[ -n "$filter_tag" && "$tags" != *"$filter_tag"* ]] && continue

    # Get first non-heading, non-empty line after frontmatter as summary
    local summary=""
    local past_heading=false
    while IFS= read -r line; do
      if [[ "$line" =~ ^---$ ]]; then continue; fi
      if $frontmatter_done && [[ "$line" =~ ^#[[:space:]] ]]; then
        past_heading=true
        continue
      fi
      if $past_heading && [[ -n "$line" ]]; then
        summary="$line"
        break
      fi
    done < "$file"

    output+="**[${priority}] ${heading:-$(basename "$file" .md)}** (${created}) — ${tags}"$'\n'
    [[ -n "$summary" ]] && output+="  ${summary}"$'\n'
    output+=$'\n'
    ((count++))
  done

  if [[ $count -eq 0 ]]; then
    echo "No todos found matching criteria."
  else
    local label="Todos"
    [[ -n "$filter_status" ]] && label="$(echo "$filter_status" | awk '{print toupper(substr($0,1,1)) substr($0,2)}') Todos"
    echo "## ${label} (${count})"
    echo ""
    echo -n "$output"
  fi
}

cmd_update() {
  local file="$1"; shift
  local new_status="" new_priority="" new_tags=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      -s) new_status="$2"; shift 2 ;;
      -p) new_priority="$2"; shift 2 ;;
      --tags) new_tags="$2"; shift 2 ;;
      *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
  done

  # Resolve file path — accept partial name match
  local resolved=""
  if [[ -f "$file" ]]; then
    resolved="$file"
  elif [[ -f "${TODO_DIR}/${file}" ]]; then
    resolved="${TODO_DIR}/${file}"
  else
    for f in "$TODO_DIR"/*"$file"*; do
      if [[ -f "$f" ]]; then
        resolved="$f"
        break
      fi
    done
  fi

  [[ -z "$resolved" ]] && { echo "Error: no todo matching '$file'" >&2; exit 1; }

  [[ -n "$new_status" ]] && validate_status "$new_status"
  [[ -n "$new_priority" ]] && validate_priority "$new_priority"

  if [[ -n "$new_status" ]]; then
    sed -i '' "s/^status:.*$/status: ${new_status}/" "$resolved"
  fi
  if [[ -n "$new_priority" ]]; then
    sed -i '' "s/^priority:.*$/priority: ${new_priority}/" "$resolved"
  fi
  if [[ -n "$new_tags" ]]; then
    local tags_yaml="[$(echo "$new_tags" | sed 's/,/, /g')]"
    sed -i '' "s/^tags:.*$/tags: ${tags_yaml}/" "$resolved"
  fi

  echo "Updated: $resolved"
}

cmd_archive() {
  local file="$1"

  # Resolve file path
  local resolved=""
  if [[ -f "$file" ]]; then
    resolved="$file"
  elif [[ -f "${TODO_DIR}/${file}" ]]; then
    resolved="${TODO_DIR}/${file}"
  else
    for f in "$TODO_DIR"/*"$file"*; do
      if [[ -f "$f" ]]; then
        resolved="$f"
        break
      fi
    done
  fi

  [[ -z "$resolved" ]] && { echo "Error: no todo matching '$file'" >&2; exit 1; }

  # Set status to done
  sed -i '' "s/^status:.*$/status: done/" "$resolved"

  # Move to done/
  mkdir -p "$DONE_DIR"
  mv "$resolved" "$DONE_DIR/"

  echo "Archived: ${DONE_DIR}/$(basename "$resolved")"
}

# Main
[[ $# -eq 0 ]] && usage

command="$1"; shift
case "$command" in
  create)  cmd_create "$@" ;;
  list)    cmd_list "$@" ;;
  update)  cmd_update "$@" ;;
  archive) cmd_archive "$@" ;;
  *)       echo "Unknown command: $command" >&2; usage ;;
esac
