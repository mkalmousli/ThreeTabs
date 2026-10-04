#!/usr/bin/env bash
# Builds dist/threetabs.zip, loadable in Chrome/Edge/Brave (unpacked) and Firefox (as .xpi).
set -euo pipefail
cd "$(dirname "$0")/../extension"
mkdir -p ../dist
rm -f ../dist/threetabs.zip
zip -r ../dist/threetabs.zip . -x "icons/icon.svg" >/dev/null
echo "dist/threetabs.zip built"
