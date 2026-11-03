# ServiceApp for DreamOS

[Česky](README.cs.md)

Port of [ServiceApp](https://github.com/oe-mirrors/serviceapp) to **DreamOS 2.5**
(enigma2 4.3.3r3, Python 2.7). It adds the service type **5002** played by
[exteplayer3](https://github.com/Blacker91/exteplayer3-dreamos), the same way as on
OpenPLi / OpenATV, so plugins like ArchivCZSK can use exteplayer3 on a Dreambox.

## ⚠️ Warning
- **Use at your own risk.** Make a **backup of your image** before installing.
- Install only on **enigma2 4.3.3r3** (DreamOS 2.5, the last released unstable version),
  the version it was tested on. Check it on the box with `dpkg -l enigma2`.
- Tested on a DM520. The DM900/DM920 build is checked against the same enigma2
  version but has not been tested on the box yet.

## Supported boxes
| Box | Architecture |
|---|---|
| DM520, DM525 | mipsel |
| DM900, DM920 | armhf |

Packages are separate for mipsel and armhf, the installer picks the right one.

**Dreambox One / Two (DreamOS 2.6, enigma2 4.5.1r11)** – experimental `_arm64` package,
not tested on a box yet and not in the installer. There is no exteplayer3 for the One
yet (it needs the Amlogic video output), so ServiceApp has nothing to play with
unless an exteplayer3 for the One is installed in `/usr/bin`. Built with
`dreamos/fetch-sysroot.sh aarch64` (`ONE_IMAGE=` a Dreambox One image) and
`dreamos/build.sh aarch64`; the differences between enigma2 4.3.3r3 and 4.5.1r11
are listed in `dreamos/e2-451-headers.py`.

## Features
- service type 5002 (exteplayer3): HLS, DASH, CENC DRM keys, separate audio (YouTube)
- pause / seek in the InfoBar for videos (not in live streams)
- EPG for 5002 services
- subtitles: embedded text tracks, external .srt, WebVTT, graphic subtitles (PGS, DVB)
- optional: replace Dream's servicemp3 (4097) for streams, files, or both

## Install
On the box (ssh/telnet):
```sh
curl -fsSL https://raw.githubusercontent.com/Blacker91/serviceapp-dreamos/dreamos/installer.sh | sh
```
It installs ServiceApp and exteplayer3 (with ffmpeg), adds the apt feed and restarts enigma2.

## Updates
The installer adds this feed to `/etc/apt/sources.list.d/serviceapp-dreamos.list`:
```
deb [trusted=yes] https://raw.githubusercontent.com/Blacker91/serviceapp-dreamos/feed ./
```
New versions then come with the normal software update:
```sh
apt-get update && apt-get upgrade
```
Running the installer again also updates.

Needs `curl` (usually part of DreamOS). The BusyBox `wget` of DreamOS cannot download from GitHub.
If `curl` is missing: `apt-get update && apt-get install curl`.

Manually: download the `.deb` files for your box (`_mipsel` for DM520/DM525, `_armhf` for DM900/DM920) from
[Releases](https://github.com/Blacker91/serviceapp-dreamos/releases) and
[exteplayer3 Releases](https://github.com/Blacker91/exteplayer3-dreamos/releases), then
```sh
dpkg -i exteplayer3-dreamos_*.deb enigma2-plugin-systemplugins-serviceapp-dreamos_*.deb
systemctl restart enigma2
```
For updates via apt, add the feed line from [Updates](#updates) to `/etc/apt/sources.list.d/serviceapp-dreamos.list`.

## Settings
Menu → Plugins → ServiceApp.
- **Enigma2 playback system → serviceapp**: 4097 streams (e.g. IPTV bouquets) are played by exteplayer3.
  **Play with ServiceApp**: streams only (default), streams and files, or files from disk/NAS only.
- **Subtitles**: font size, colour, background, delay, display time, distance from the bottom.

## Contact
Bugs and suggestions: [Issues](https://github.com/Blacker91/serviceapp-dreamos/issues) or e-mail
**dreamosserviceapp@gmail.com**.
