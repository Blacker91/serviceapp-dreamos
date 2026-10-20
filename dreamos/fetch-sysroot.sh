#!/bin/bash
# Download the DreamOS 2.5 packages needed to build ServiceApp and unpack them
# into a sysroot. Nothing from Dream is stored in this repository.
#
#   dreamos/fetch-sysroot.sh mipsel      DM520 / DM525
#   dreamos/fetch-sysroot.sh arm         DM900 / DM920
#
#   DEBS_DIR=dir   use already downloaded .deb files instead of the feed
#   E2_BINARY=f    enigma2 binary used for the symbol check (e.g. /usr/bin/enigma2
#                  copied from your box); default: enigma2 package from the feed
set -euo pipefail
ARCH="${1:-mipsel}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="${WORK:-$ROOT/.work}"
OEVER="${OEVER:-2.5}"
FEED="http://dreamboxupdate.com/opendreambox/$OEVER/unstable/r0"
case "$ARCH" in
  mipsel) MACHINE=dm520; SUBDIRS="all dm520 mips32el" ;;
  arm)    MACHINE=dm900; SUBDIRS="all dm900 cortexa15hf-neon-vfpv4" ;;
  *) echo "usage: $0 mipsel|arm" >&2; exit 1 ;;
esac
# enigma2-dev headers are architecture independent; 4.3.3r3 is taken from the
# DM520 feed for both architectures (it matches the released 2.5 images)
HEADERS_FEED="$FEED/dm520/deb/mips32el"
PKGS="enigma2 libc6 libc6-dev linux-libc-headers-dev libgcc1 libgcc-s-dev libstdc++6 libstdc++-dev
      libsigc-2.0-0 libsigc-2.0-dev python-core python-dev libpython2.7-1.0 libdvbsi++1 libdvbsi++-dev
      openssl-dev libssl1.0.0 libcrypto1.0.0 libglib-2.0-dev libfreetype-dev"

D="$WORK/$ARCH"; DEBS="$D/debs"; SR="$D/sysroot"
mkdir -p "$DEBS"

fetch_index() { # <url> <out>
  curl -sf "$1/Packages.gz" | gunzip > "$2" 2>/dev/null || curl -sf "$1/Packages" -o "$2" || rm -f "$2"
}
pick() { # <index> <package> -> Filename
  awk -v p="$2" '/^Package: /{n=$2} /^Filename: /{if(n==p){sub(/^\.\//,"",$2); print $2; exit}}' "$1"
}

if [ -n "${DEBS_DIR:-}" ]; then
  cp -n "$DEBS_DIR"/*.deb "$DEBS"/
else
  for s in $SUBDIRS; do fetch_index "$FEED/$MACHINE/deb/$s" "$D/Packages_$s"; done
  for p in $PKGS; do
    got=""
    for s in $SUBDIRS; do
      [ -f "$D/Packages_$s" ] || continue
      f=$(pick "$D/Packages_$s" "$p"); [ -n "$f" ] || continue
      curl -sf -o "$DEBS/$(basename "$f")" "$FEED/$MACHINE/deb/$s/$f" && got=1 && break
    done
    [ -n "$got" ] && echo "  $p" || echo "  $p: not in feed"
  done
  fetch_index "$HEADERS_FEED" "$D/Packages_headers"
  f=$(pick "$D/Packages_headers" enigma2-dev)
  [ -n "$f" ] || { echo "enigma2-dev not found in $HEADERS_FEED" >&2; exit 1; }
  curl -sf -o "$DEBS/$(basename "$f")" "$HEADERS_FEED/$f"
  echo "  enigma2-dev ($(basename "$f"))"
fi

rm -rf "$SR"; mkdir -p "$SR"
for deb in "$DEBS"/*.deb; do dpkg-deb -x "$deb" "$SR"; done
[ -d "$SR/usr/include/enigma2" ] || { echo "enigma2-dev headers missing" >&2; exit 1; }
if [ -n "${E2_BINARY:-}" ]; then cp "$E2_BINARY" "$SR/usr/bin/enigma2"; fi
[ -f "$SR/usr/bin/enigma2" ] || echo "warning: no enigma2 binary, the symbol check will be skipped"
echo "sysroot ready: $SR"
