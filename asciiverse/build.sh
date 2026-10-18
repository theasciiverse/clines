#!/bin/sh
# Builds Console Lines into out/: the four sources in one compiler run
# (one process, so no parallel jobs to limit), with
# asciiverse/clines-config.h instead of configure. The compiler, flags and
# curses library come from the environment, so one script serves every
# target (see .github/workflows/release.yml):
#
#   asciiverse/build.sh                                       # Linux
#   GPM=1 asciiverse/build.sh                                 # Linux, with GPM
#   LDFLAGS="-static -s" asciiverse/build.sh                  # Alpine, static
#   CURSES_LIBS=-lncurses CFLAGS="-O2 -arch arm64" \
#     LDFLAGS="-arch arm64" asciiverse/build.sh               # macOS
#
# GPM, the Linux console mouse, is off unless GPM=1: it is a shared
# library and daemon, so it stays out of the static builds. Terminal mouse
# support through curses works without it.
set -eu
cd "$(dirname "$0")/.."
CC="${CC:-cc}"
CFLAGS="${CFLAGS:--O2}"
LDFLAGS="${LDFLAGS:-}"
CURSES_LIBS="${CURSES_LIBS:--lncursesw}"
GPM_FLAGS=""
if [ "${GPM:-0}" = 1 ]; then
  GPM_FLAGS="-DHAVE_GPM"
  CURSES_LIBS="$CURSES_LIBS -lgpm"
fi
cp asciiverse/clines-config.h clines-config.h
mkdir -p out
rm -f out/clines
# shellcheck disable=SC2086
nice -n 10 $CC -std=gnu99 -Wall $CFLAGS -DHAVE_CONFIG_H $GPM_FLAGS -I. -Isrc/include -o out/clines \
  src/board.c src/gameplay.c src/main.c src/render.c $CURSES_LIBS $LDFLAGS
cp clines.6 out/clines.6
echo "built clines"
