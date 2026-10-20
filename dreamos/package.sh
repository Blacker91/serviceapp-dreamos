#!/bin/bash
# Build the universal .deb (mipsel + armhf) from the serviceapp.so files made by
# dreamos/build.sh mipsel and dreamos/build.sh arm. postinst installs the one
# matching the box and removes the other.
#   dreamos/package.sh [version]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="${WORK:-$ROOT/.work}"
VER="${1:-$(sed -n 's/^## \([^ ]*\).*/\1/p' "$ROOT/CHANGELOG.md" | head -n 1)}"
N=enigma2-plugin-systemplugins-serviceapp-dreamos
P="$WORK/pkg"; PD="$P/usr/lib/enigma2/python/Plugins/SystemPlugins/ServiceApp"; SH="$P/usr/share/$N"
rm -rf "$P"; mkdir -p "$P/DEBIAN" "$PD" "$SH/mipsel" "$SH/armhf" "$P/usr/share/doc/$N"
for a in mipsel:mipsel arm:armhf; do
  so="$WORK/${a%%:*}/build/serviceapp.so"
  [ -f "$so" ] || { echo "missing $so - run dreamos/build.sh ${a%%:*}" >&2; exit 1; }
  install -m 755 "$so" "$SH/${a##*:}/serviceapp.so"
done
cp "$ROOT"/src/plugin/{__init__.py,plugin.py,serviceapp_client.py,plugin.png} "$PD/"
cp "$ROOT/CHANGELOG.md" "$P/usr/share/doc/$N/changelog"
cp "$ROOT/COPYING" "$P/usr/share/doc/$N/copyright"

cat > "$P/DEBIAN/control" <<EOF
Package: $N
Version: $VER
Architecture: all
Maintainer: Blacker91
Installed-Size: $(du -sk "$P" --exclude=DEBIAN | cut -f1)
Depends: enigma2 (>= 4.3.3r3-r0.0), enigma2 (<< 4.3.3r4), exteplayer3-dreamos, libssl1.0.0, libcrypto1.0.0, libstdc++6, python-core
Suggests: ffmpeg-exteplayer3-dreamos
Section: extra
Priority: optional
Homepage: https://github.com/Blacker91/serviceapp-dreamos
Description: ServiceApp for DreamOS 2.5 (DM520/DM525/DM900/DM920)
 ServiceApp (service type 5002, exteplayer3) for DreamOS 2.5 / enigma2 4.3.3r3.
 Pause/seek in the InfoBar, EPG for 5002 services, subtitles, optional
 replacement of servicemp3 (4097) for URLs.
EOF

cat > "$P/DEBIAN/postinst" <<'EOF'
#!/bin/sh
set -e
SH="${DPKG_ROOT:-}/usr/share/enigma2-plugin-systemplugins-serviceapp-dreamos"
PD="${DPKG_ROOT:-}/usr/lib/enigma2/python/Plugins/SystemPlugins/ServiceApp"
A="$(dpkg --print-architecture 2>/dev/null || true)"
case "$A" in
  mipsel|armhf) ;;
  *) case "$(uname -m)" in mips*) A=mipsel ;; arm*) A=armhf ;; *) A="" ;; esac ;;
esac
[ -n "$A" ] && [ -f "$SH/$A/serviceapp.so" ] || { echo "ServiceApp: unsupported box ($(uname -m))" >&2; exit 1; }
mv -f "$SH/$A/serviceapp.so" "$PD/serviceapp.so"
rm -rf "$SH/mipsel" "$SH/armhf"
echo "ServiceApp installed ($A), restart enigma2: systemctl restart enigma2"
EOF
cat > "$P/DEBIAN/postrm" <<'EOF'
#!/bin/sh
case "$1" in
  remove|purge)
    rm -f "${DPKG_ROOT:-}/usr/lib/enigma2/python/Plugins/SystemPlugins/ServiceApp/serviceapp.so"
    rm -rf "${DPKG_ROOT:-}/usr/share/enigma2-plugin-systemplugins-serviceapp-dreamos" ;;
esac
exit 0
EOF
chmod 755 "$P/DEBIAN/postinst" "$P/DEBIAN/postrm"
mkdir -p "$WORK/out"
dpkg-deb -Zgzip --root-owner-group -b "$P" "$WORK/out/${N}_${VER}_all.deb" >/dev/null
echo "$WORK/out/${N}_${VER}_all.deb"
