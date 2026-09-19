#!/usr/bin/env bash
# Development startup wrapper
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/run_app.sh" "$@"
