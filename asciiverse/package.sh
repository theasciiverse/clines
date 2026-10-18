#!/bin/sh
# Packs the build into dist/clines-<target>.tar.gz for av: the binary at
# the top, with the man page, README, COPYING and PATCHES.md.
#
#   asciiverse/package.sh x86_64-unknown-linux-musl
set -eu
cd "$(dirname "$0")/.."
target="$1"
stage=stage/clines
rm -rf "$stage" && mkdir -p "$stage" dist
cp out/clines out/clines.6 README COPYING PATCHES.md "$stage/"
tar -czf "dist/clines-$target.tar.gz" -C "$stage" .
ls dist
