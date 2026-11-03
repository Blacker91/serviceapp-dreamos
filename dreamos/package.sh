#!/bin/bash
# Build the .deb packages (one per architecture) from the serviceapp.so files
# made by dreamos/build.sh mipsel, arm and aarch64.
#   dreamos/package.sh [version]
#   ARCHS="mipsel arm" dreamos/package.sh     only some architectures
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="${WORK:-$ROOT/.work}"
VER="${1:-$(sed -n 's/^## \([^ ]*\).*/\1/p' "$ROOT/CHANGELOG.md" | head -n 1)}"
N=enigma2-plugin-systemplugins-serviceapp-dreamos
mkdir -p "$WORK/out"

for b in ${ARCHS:-mipsel arm aarch64}; do
  case "$b" in
    mipsel)  ARCH=mipsel; BOXES="DM520/DM525" ;;
    arm)     ARCH=armhf;  BOXES="DM900/DM920" ;;
    aarch64) ARCH=arm64;  BOXES="Dreambox One/Two" ;;
    *) echo "unknown architecture $b" >&2; exit 1 ;;
  esac
  so="$WORK/$b/build/serviceapp.so"
  [ -f "$so" ] || { echo "missing $so - run dreamos/build.sh $b" >&2; exit 1; }
  if [ "$b" = aarch64 ]; then
    # DreamOS 2.6. No exteplayer3-dreamos for the One yet (needs the Amlogic
    # output), so any exteplayer3 is only recommended.
    OS="DreamOS 2.6 / enigma2 4.5.1r11"
    DEPS="enigma2 (>= 4.5.1r11-r0.0), enigma2 (<< 4.5.1r12), libssl1.0.2, libcrypto1.0.2, libstdc++6, python-core
Recommends: exteplayer3"
  else
    OS="DreamOS 2.5 / enigma2 4.3.3r3"
    DEPS="enigma2 (>= 4.3.3r3-r0.0), enigma2 (<< 4.3.3r4), exteplayer3-dreamos (>= 184-dreamos3), libssl1.0.0, libcrypto1.0.0, libstdc++6, python-core"
  fi
  P="$WORK/pkg-$ARCH"; PD="$P/usr/lib/enigma2/python/Plugins/SystemPlugins/ServiceApp"
  rm -rf "$P"; mkdir -p "$P/DEBIAN" "$PD" "$P/usr/share/doc/$N"
  install -m 755 "$so" "$PD/serviceapp.so"
  cp "$ROOT"/src/plugin/{__init__.py,plugin.py,serviceapp_client.py,plugin.png,keymap_plexdream.xml} "$PD/"
  cp "$ROOT/CHANGELOG.md" "$P/usr/share/doc/$N/changelog"
  cp "$ROOT/COPYING" "$P/usr/share/doc/$N/copyright"
  cat > "$P/DEBIAN/control" <<EOF
Package: $N
Version: $VER
Architecture: $ARCH
Maintainer: Blacker91
Installed-Size: $(du -sk "$P" --exclude=DEBIAN | cut -f1)
Depends: $DEPS
Section: extra
Priority: optional
Homepage: https://github.com/Blacker91/serviceapp-dreamos
Description: ServiceApp for ${OS%% /*} ($BOXES)
 ServiceApp (service type 5002, exteplayer3) for $OS.
 Pause/seek in the InfoBar, EPG for 5002 services, subtitles, optional
 replacement of servicemp3 (4097) for streams and files.
EOF
  dpkg-deb -Zgzip --root-owner-group -b "$P" "$WORK/out/${N}_${VER}_${ARCH}.deb" >/dev/null
  echo "$WORK/out/${N}_${VER}_${ARCH}.deb"
done
