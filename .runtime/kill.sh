#!/bin/sh
pgrep -f "fastapi" | xargs kill >/dev/null 2>&1