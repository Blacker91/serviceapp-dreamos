#!/bin/bash
# Sysroot for Dreambox One / Two (DreamOS 2.6, enigma2 4.5.1r11, aarch64).
# Called by dreamos/fetch-sysroot.sh aarch64. Nothing from Dream is stored in
# this repository; everything is assembled in $WORK/aarch64/sysroot.
#
#   ONE_IMAGE=f   Dreambox One/Two image (dreambox-image-dreamone-*.tar.xz from
#                 dreambox.de, or a box backup / extracted rootfs directory).
#                 Runtime libraries, enigma2 (symbol check) and pyconfig.h come
#                 from it, so the .so links against exactly what the box has.
#   DEBS_DIR=dir  already downloaded enigma2-dev 4.3.3r3, python-dev and
#                 libdvbsi++-dev .deb files (otherwise from the DreamOS 2.5 feed)
#
# Headers:
#  - enigma2: enigma2-dev 4.3.3r3 changed to 4.5.1r11 by e2-451-headers.py
#    (getLength64, eServiceReference and iSubtitleTrackInfo layout, enums;
#    all read from the One image).
#  - glibc 2.23, libstdc++/libgcc 6.4 (the box has glibc 2.25 and gcc 6.4),
#    sigc++ 2.10 and OpenSSL 1.0.2n (same versions as the box): Ubuntu packages.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="${WORK:-$ROOT/.work}"
D="$WORK/aarch64"; DEBS="$D/debs"; SR="$D/sysroot"
UBU="http://archive.ubuntu.com/ubuntu/pool"
UBU_DEBS="
main/c/cross-toolchain-base/libc6-dev-arm64-cross_2.23-0ubuntu3cross1_all.deb 87af621994725c363da4c62e76dbbc48bfda58de3af36c596f2130812c8533b9
main/c/cross-toolchain-base/linux-libc-dev-arm64-cross_4.4.0-18.34cross1_all.deb ae81100caad16193a07439168855b999d6bf16aa5837eb2aeb4d04147fb84bdd
universe/g/gcc-6-cross/libstdc++-6-dev-arm64-cross_6.4.0-17ubuntu1cross1_all.deb 209d60f8074c652fb04680c00755d675b81ca095fe4323573b0d058f173d1cd7
universe/g/gcc-6-cross/libgcc-6-dev-arm64-cross_6.4.0-17ubuntu1cross1_all.deb b6fa82f3af4bbe6b9bc41f19a74ac8244741f067200c2597aac13431d59f5a2e
main/libs/libsigc++-2.0/libsigc++-2.0-dev_2.10.0-2_amd64.deb c0ceffe89621f5e76b896f0a6a6947d890656b799b3b318126fcc3cd63815724
main/o/openssl1.0/libssl1.0-dev_1.0.2n-1ubuntu5_amd64.deb f45b03e9b95ce9ce62cd8229068c4d297e34745e11904610e66593597a3ce619"
DREAM_FEED="http://dreamboxupdate.com/opendreambox/2.5/unstable/r0/dm520/deb/mips32el"
DREAM_PKGS="enigma2-dev python-dev libdvbsi++-dev"

[ -n "${ONE_IMAGE:-}" ] || { echo "set ONE_IMAGE=<Dreambox One image .tar.xz or rootfs dir>" >&2; exit 1; }
mkdir -p "$DEBS/ubuntu" "$DEBS/dream"

echo "$UBU_DEBS" | while read -r p sum; do
  [ -n "$p" ] || continue
  f="$DEBS/ubuntu/$(basename "$p")"
  [ -f "$f" ] || curl -sf -o "$f" "$UBU/$p" || { echo "download failed: $p" >&2; exit 1; }
  echo "$sum  $f" | sha256sum -c --quiet - || { rm -f "$f"; exit 1; }
done

if [ -n "${DEBS_DIR:-}" ]; then
  for p in $DREAM_PKGS; do cp "$DEBS_DIR"/${p}_*.deb "$DEBS/dream/"; done
else
  curl -sf "$DREAM_FEED/Packages.gz" | gunzip > "$D/Packages_headers" || { echo "DreamOS 2.5 feed unreachable, use DEBS_DIR" >&2; exit 1; }
  for p in $DREAM_PKGS; do
    f=$(awk -v p="$p" '/^Package: /{n=$2} /^Filename: /{if(n==p){sub(/^\.\//,"",$2); print $2; exit}}' "$D/Packages_headers")
    curl -sf -o "$DEBS/dream/$(basename "$f")" "$DREAM_FEED/$f"
  done
fi

rm -rf "$SR" "$D/x"; mkdir -p "$SR/usr/lib" "$D/x"
# runtime libraries + enigma2 from the image
if [ -d "$ONE_IMAGE" ]; then IMG="$ONE_IMAGE"; else
  IMG="$D/image"; rm -rf "$IMG"; mkdir -p "$IMG"
  tar -xf "$ONE_IMAGE" -C "$IMG" --exclude='./dev/*' --exclude='dev/*' 2>/dev/null || true
  [ -f "$IMG/usr/bin/enigma2" ] || { echo "no usr/bin/enigma2 in $ONE_IMAGE" >&2; exit 1; }
fi
grep -q "^Version: 4.5.1" <(awk '/^Package: enigma2$/{p=1} p&&/^Version:/{print;exit}' "$IMG/var/lib/dpkg/status" 2>/dev/null) || \
  echo "warning: image enigma2 is not 4.5.1r11 (or no dpkg status in the image)"
cp -a "$IMG/lib" "$SR/"
for l in libstdc++.so.6* libsigc-2.0.so.0* libssl.so.1.0.2 libcrypto.so.1.0.2 libpython2.7.so.1.0; do cp -a "$IMG"/usr/lib/$l "$SR/usr/lib/"; done
mkdir -p "$SR/usr/bin"; cp "$IMG/usr/bin/enigma2" "$SR/usr/bin/enigma2"

# headers
for deb in "$DEBS"/dream/*.deb; do dpkg-deb -x "$deb" "$D/x/dream"; done
for deb in "$DEBS"/ubuntu/*.deb; do dpkg-deb -x "$deb" "$D/x/ubuntu"; done
U="$D/x/ubuntu"
cp -a "$U/usr/aarch64-linux-gnu/include" "$SR/usr/"
cp -a "$U/usr/aarch64-linux-gnu/lib/"{crt1.o,crti.o,crtn.o,libc_nonshared.a,libpthread_nonshared.a} "$SR/usr/lib/"
mkdir -p "$SR/usr/lib/gcc/aarch64-linux-gnu"
cp -a "$U/usr/lib/gcc-cross/aarch64-linux-gnu/6" "$SR/usr/lib/gcc/aarch64-linux-gnu/6"
rm -f "$SR/usr/lib/gcc/aarch64-linux-gnu/6/libstdc++.so" "$SR/usr/lib/gcc/aarch64-linux-gnu/6/libgcc_s.so"
cp -a "$U/usr/include/sigc++-2.0" "$SR/usr/include/"
cp "$U/usr/lib/x86_64-linux-gnu/sigc++-2.0/include/sigc++config.h" "$SR/usr/include/sigc++-2.0/"
cp -a "$U/usr/include/openssl" "$SR/usr/include/"
cp "$U/usr/include/x86_64-linux-gnu/openssl/opensslconf.h" "$SR/usr/include/openssl/"   # LP64, same as aarch64
cp -a "$D/x/dream/usr/include/"{enigma2,python2.7,dvbsi++} "$SR/usr/include/"
cp "$IMG/usr/include/python2.7/"pyconfig*.h "$SR/usr/include/python2.7/"

# libraries the linker sees (glibc's libc.so script, unversioned names)
cat > "$SR/usr/lib/libc.so" <<'EOF'
OUTPUT_FORMAT(elf64-littleaarch64)
GROUP ( /lib/libc.so.6 /usr/lib/libc_nonshared.a AS_NEEDED ( /lib/ld-linux-aarch64.so.1 ) )
EOF
ln -sf libstdc++.so.6 "$SR/usr/lib/libstdc++.so"
ln -sf libssl.so.1.0.2 "$SR/usr/lib/libssl.so"
ln -sf libcrypto.so.1.0.2 "$SR/usr/lib/libcrypto.so"
ln -sf ../../lib/libm.so.6 "$SR/usr/lib/libm.so"
ln -sf ../../lib/libgcc_s.so.1 "$SR/usr/lib/libgcc_s.so"

# enigma2 4.5.1r11 interface changes (see dreamos/e2-451-headers.py)
python3 "$ROOT/dreamos/e2-451-headers.py" "$SR/usr/include/enigma2"
rm -rf "$D/x"
echo "sysroot ready: $SR"
