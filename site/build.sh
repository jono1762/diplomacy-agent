#!/usr/bin/env bash
# Builds the replay site from the web interface bundled with the diplomacy pip package.
#
#   site/build.sh          production build -> site/.build/build
#   site/build.sh start    local dev server on http://localhost:3000
#
# Steps: copy the upstream interface into site/.build, apply ui.patch, add the
# replay page and the generated games, then build with react-scripts.
set -euo pipefail

SITE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SITE_DIR")"
BUILD_DIR="$SITE_DIR/.build"

# Prefer the project venv, fall back to python3 (e.g. in CI)
PYTHON="${PYTHON:-$( [ -x "$ROOT_DIR/venv/bin/python" ] && echo "$ROOT_DIR/venv/bin/python" || echo python3 )}"
UPSTREAM="$("$PYTHON" -c 'import os, diplomacy; print(os.path.join(os.path.dirname(diplomacy.__file__), "web"))')"

# Fresh copy of the upstream sources (node_modules is kept between builds)
mkdir -p "$BUILD_DIR"
rm -rf "$BUILD_DIR/src" "$BUILD_DIR/public" "$BUILD_DIR/build"
cp -r "$UPSTREAM/src" "$UPSTREAM/public" "$UPSTREAM/package.json" "$UPSTREAM/package-lock.json" "$BUILD_DIR/"

patch --quiet -p1 -d "$BUILD_DIR" < "$SITE_DIR/ui.patch"
cp "$SITE_DIR/content_replays.jsx" "$SITE_DIR/content_replays.css" "$BUILD_DIR/src/gui/pages/"
cp "$SITE_DIR/saved_game.js" "$BUILD_DIR/src/gui/utils/"
cp -r "$SITE_DIR/games" "$BUILD_DIR/public/games"

cd "$BUILD_DIR"
[ -d node_modules ] || npm ci --no-audit --no-fund

# react-scripts 3 (webpack 4) needs the legacy OpenSSL provider on Node 17+
export NODE_OPTIONS=--openssl-legacy-provider
if [ "${1:-}" = "start" ]; then
    npm start
else
    npm run build
fi
