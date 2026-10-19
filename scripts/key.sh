#!/bin/sh
set -eu
BASE=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
case "${1:-}" in
 UP) CODE=103;; DOWN) CODE=108;; LEFT) CODE=105;; RIGHT) CODE=106;;
 OK) CODE=28;; BACK) CODE=412;; HOME) CODE=125;;
 RED) CODE=398;; GREEN) CODE=399;; YELLOW) CODE=400;; BLUE) CODE=401;;
 *) echo 'Use UP DOWN LEFT RIGHT OK BACK HOME RED GREEN YELLOW BLUE' >&2; exit 1;;
esac
"$BASE/scripts/tv-ssh" --tty "luna-send -w 5000 -n 1 -f luna://com.webos.service.networkinput/test/sendKeyCode '{\"keyCode\":$CODE}'"
