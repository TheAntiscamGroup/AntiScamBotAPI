#!/bin/sh
set -e pipefail
pgrep -f "fastapi" | xargs kill >/dev/null 2>&1 | return 0