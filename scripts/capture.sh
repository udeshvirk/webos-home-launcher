#!/bin/sh
set -eu
BASE=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
NAME=${1:-capture}
case "$NAME" in ''|*[!a-zA-Z0-9_-]*) echo 'Use a simple screenshot name' >&2; exit 1;; esac
umask 077
mkdir -p "$BASE/private/screenshots"
"$BASE/scripts/tv-ssh" --tty "luna-send -w 5000 -n 1 -f luna://com.webos.service.tv.capture/executeOneShot '{\"path\":\"/tmp/webos-home-capture.png\",\"method\":\"DISPLAY\",\"format\":\"PNG\"}'"
"$BASE/scripts/tv-ssh" 'cat /tmp/webos-home-capture.png' > "$BASE/private/screenshots/$NAME.png"
python3 - "$BASE/private/screenshots/$NAME.png" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1]);assert p.read_bytes()[:8]==b'\x89PNG\r\n\x1a\n','Capture did not return a PNG'
print(p)
PY
