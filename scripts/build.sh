#!/bin/sh
# Build only: does not contact a TV or change its Home button.
set -eu
BASE=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
command -v ares-package >/dev/null || { echo 'Install @webos-tools/cli and put ares-package on PATH' >&2; exit 1; }
node --check "$BASE/app/home.js"
umask 077
mkdir -p "$BASE/dist"
STAGE=$(mktemp -d "$BASE/dist/build.XXXXXX")
trap 'rm -rf "$STAGE"' EXIT
cp -R "$BASE/app/." "$STAGE/"
if [ -f "$BASE/app/config.local.js" ]; then cp "$BASE/app/config.local.js" "$STAGE/config.js"; rm -f "$STAGE/config.local.js"; fi
if [ -d "$BASE/private/generated/assets" ]; then cp -R "$BASE/private/generated/assets/." "$STAGE/assets/"; fi
if [ -f "$BASE/private/generated/seed.js" ]; then cp "$BASE/private/generated/seed.js" "$STAGE/seed.js"; fi
ares-package "$STAGE" -o "$BASE/dist"
