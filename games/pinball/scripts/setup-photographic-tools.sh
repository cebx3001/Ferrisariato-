#!/usr/bin/env bash
# Local, pinned render-only tools; no global installation or TLS changes.
set -euo pipefail
photo_cache="${PINBALL_TOOL_CACHE:-/workspace/.cache}"
mkdir -p "$photo_cache"
archive="$photo_cache/oidn-2.3.3.tar.gz"
if [[ ! -f "$archive" ]]; then
  curl --fail --location --retry 2 \
    https://github.com/RenderKit/oidn/releases/download/v2.3.3/oidn-2.3.3.x86_64.linux.tar.gz \
    --output "$archive"
fi
printf '%s  %s\n' '3c385230d9e6f63527ba72f2229594dbac5051674219d72e0044b5d0b841796f' "$archive" | sha256sum --check
tar -xzf "$archive" -C "$photo_cache"
python3 -m pip install --no-cache-dir --target "$photo_cache/ferrisariato-python" \
  OpenEXR==3.5.2 numpy==2.5.4
"$photo_cache/oidn-2.3.3.x86_64.linux/bin/oidnDenoise" --list_devices
