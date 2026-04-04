#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec npx @playwright/cli --config="$SCRIPT_DIR/cli.config.json" "$@"
