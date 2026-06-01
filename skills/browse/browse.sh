#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# `--config` is only a valid option on the session-creating commands
# (`open`/`attach`). Every other subcommand attaches to the running session
# via `-s` and rejects `--config` as an unknown option. So inject it only for
# those commands. The subcommand is the first argument that isn't a flag
# (e.g. it follows an optional leading `-s=<session>`).
cmd=""
for a in "$@"; do
  case "$a" in
    -*) continue ;;
    *) cmd="$a"; break ;;
  esac
done

if [ "$cmd" = "open" ] || [ "$cmd" = "attach" ]; then
  exec npx @playwright/cli --config="$SCRIPT_DIR/cli.config.json" "$@"
else
  exec npx @playwright/cli "$@"
fi
