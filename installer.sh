#!/bin/sh
# ServiceApp + exteplayer3 + ffmpeg for DreamOS 2.5 (DM520/DM525/DM900/DM920)
#   curl -fsSL https://raw.githubusercontent.com/Blacker91/serviceapp-dreamos/dreamos/installer.sh | sh
SERVICEAPP=0.5-dreamos11
EXTEPLAYER3=183-dreamos9

command -v dpkg >/dev/null 2>&1 || { echo "This installer is for DreamOS (.deb) only."; exit 1; }
ARCH="$(dpkg --print-architecture 2>/dev/null)"
case "$ARCH" in
	mipsel|armhf) ;;
	*) echo "Unsupported box (architecture '$ARCH'), only DM520/DM525/DM900/DM920."; exit 1 ;;
esac

GH=https://github.com/Blacker91
PKGS="$GH/exteplayer3-dreamos/releases/download/v$EXTEPLAYER3/exteplayer3-dreamos_${EXTEPLAYER3}_$ARCH.deb
$GH/serviceapp-dreamos/releases/download/v$SERVICEAPP/enigma2-plugin-systemplugins-serviceapp-dreamos_${SERVICEAPP}_$ARCH.deb"

# BusyBox wget on DreamOS cannot download from GitHub, curl is needed
command -v curl >/dev/null 2>&1 || {
	echo "curl is missing, install it first:  apt-get update && apt-get install curl"
	exit 1
}

download() { # <url> <file>
	curl -fsSL -o "$2" "$1" || curl -kfsSL -o "$2" "$1"
}

TMP=/tmp/serviceapp-dreamos
rm -rf "$TMP"; mkdir -p "$TMP"
for url in $PKGS; do
	f="$TMP/$(basename "$url")"
	echo "Downloading $(basename "$url")"
	download "$url" "$f" && [ -s "$f" ] || { echo "Download failed: $url"; rm -rf "$TMP"; exit 1; }
done

dpkg -i "$TMP"/*.deb || { echo "Installation failed"; rm -rf "$TMP"; exit 1; }
rm -rf "$TMP"
echo "Done. Restarting enigma2..."
sleep 2
systemctl restart enigma2
