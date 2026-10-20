#!/bin/bash
# Build serviceapp.so for DreamOS 2.5 (enigma2 4.3.3r3, Python 2.7).
#
#   dreamos/build.sh mipsel      DM520 / DM525
#   dreamos/build.sh arm         DM900 / DM920
#
# Needs: dreamos/fetch-sysroot.sh <arch> first, and on the build host
#   g++-12-mipsel-linux-gnu / g++-12-arm-linux-gnueabihf, cmake, git,
#   libboost-dev (headers only), python3
set -euo pipefail
ARCH="${1:-mipsel}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="${WORK:-$ROOT/.work}"
D="$WORK/$ARCH"; SR="$D/sysroot"; O="$D/build"
UCHARDET_REPO="https://github.com/BYVoid/uchardet.git"
UCHARDET_REV="4e685757780cb3c652fc6c9ec759f62888969ec9"

case "$ARCH" in
  mipsel) T=mipsel-linux-gnu;    TRIPLE=mipsel-oe-linux;     CPU="-march=mips32 -mabi=32 -mhard-float -mfp32 -mnan=legacy -mno-mips16" ;;
  arm)    T=arm-linux-gnueabihf; TRIPLE=arm-oe-linux-gnueabi; CPU="-mcpu=cortex-a15 -mfpu=neon-vfpv4 -mfloat-abi=hard -mthumb" ;;
  *) echo "usage: $0 mipsel|arm" >&2; exit 1 ;;
esac
[ -d "$SR/usr/include/enigma2" ] || { echo "run dreamos/fetch-sysroot.sh $ARCH first" >&2; exit 1; }
GCCINC="/usr/lib/gcc-cross/$T/12/include"
GCCLIB="$SR/usr/lib/$TRIPLE/5.3.0"

# Compile only against the box's glibc 2.23 / libstdc++ 5.3 headers, never the host's.
mkdir -p "$D/tc/boost" "$O"
ln -sfn /usr/include/boost "$D/tc/boost/boost"   # enigma2 headers need boost, nothing else from the host
COMMON="--sysroot=$SR -isystem $GCCINC -isystem $SR/usr/include $CPU -fPIC -U_TIME_BITS \
-fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -I$SR/usr/include/python2.7"
cat > "$D/tc/cc" <<EOF
#!/bin/sh
exec $T-gcc-12 -nostdinc $COMMON "\$@"
EOF
cat > "$D/tc/cxx" <<EOF
#!/bin/sh
exec $T-g++-12 -nostdinc -nostdinc++ -isystem $SR/usr/include/c++/5.3.0 -isystem $SR/usr/include/c++/5.3.0/$TRIPLE \
 -isystem $SR/usr/include/c++/5.3.0/backward $COMMON -std=gnu++14 -I$SR/usr/include/enigma2 \
 -I$SR/usr/include/sigc++-2.0 -I$SR/usr/lib/sigc++-2.0/include -idirafter $D/tc/boost "\$@"
EOF
chmod +x "$D/tc/cc" "$D/tc/cxx"

# uchardet (static)
UCH="$D/uchardet"
if [ ! -f "$UCH/inst/lib/libuchardet.a" ]; then
  [ -d "$UCH/src/.git" ] || git clone -q "$UCHARDET_REPO" "$UCH/src"
  git -C "$UCH/src" checkout -q "$UCHARDET_REV"
  cmake -S "$UCH/src" -B "$UCH/build" -DCMAKE_SYSTEM_NAME=Linux -DCMAKE_C_COMPILER="$D/tc/cc" \
    -DCMAKE_CXX_COMPILER="$D/tc/cxx" -DCMAKE_AR="$(command -v $T-ar)" -DCMAKE_RANLIB="$(command -v $T-ranlib)" \
    -DCMAKE_BUILD_TYPE=MinSizeRel -DBUILD_SHARED_LIBS=OFF -DBUILD_BINARY=OFF \
    -DCMAKE_POSITION_INDEPENDENT_CODE=ON -DCMAKE_INSTALL_PREFIX="$UCH/inst" -DCMAKE_INSTALL_LIBDIR=lib >/dev/null
  cmake --build "$UCH/build" -j"$(nproc)" >/dev/null
  cmake --install "$UCH/build" >/dev/null
fi

# serviceapp.so
S="$ROOT/src/serviceapp"
FLAGS="-Os -Wall -Wno-unused -DDEBUG -DDREAMOS -DHAVE_EPG -I$S -idirafter $ROOT/src/compat-dreamos -I$UCH/inst/include"
for f in serviceapp.cpp dreamos_servicecenter.cpp extplayer.cpp scriptrun.cpp myconsole.cpp wrappers.cpp m3u8.cpp \
         gstplayer.cpp exteplayer3.cpp common.cpp subtitles/subtitles.cpp subtitles/subrip.cpp; do
  "$D/tc/cxx" $FLAGS -include Python.h -c "$S/$f" -o "$O/$(basename "$f" .cpp).o"
done
"$D/tc/cc" -Os -I"$S" -c "$S/cJSON/cJSON.c" -o "$O/cJSON.o"
# link with the box's crt files, not the host's
$T-g++-12 --sysroot="$SR" -shared -nostartfiles -nodefaultlibs -o "$O/serviceapp.so" \
  "$SR/usr/lib/crti.o" "$GCCLIB/crtbeginS.o" "$O"/*.o "$UCH/inst/lib/libuchardet.a" \
  -L"$SR/usr/lib" -L"$SR/lib" -L"$GCCLIB" -lssl -lcrypto -lstdc++ -lm -lc -lgcc_s -lgcc \
  "$GCCLIB/crtendS.o" "$SR/usr/lib/crtn.o" -Wl,-soname,serviceapp.so
$T-strip --strip-unneeded "$O/serviceapp.so"
echo "built $O/serviceapp.so"

if [ -f "$SR/usr/bin/enigma2" ]; then
  python3 "$ROOT/dreamos/check-symbols.py" "$O/serviceapp.so" "$SR" "$T-nm"
else
  echo "symbol check skipped (no enigma2 binary in sysroot)"
fi
