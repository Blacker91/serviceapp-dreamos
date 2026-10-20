# ServiceApp for DreamOS

[Česky](README.cs.md)

Port of [ServiceApp](https://github.com/oe-mirrors/serviceapp) to **DreamOS 2.5**
(enigma2 4.3.3r3, Python 2.7). It adds the service type **5002** played by
[exteplayer3](https://github.com/Blacker91/exteplayer3-dreamos), the same way as on
OpenPLi / OpenATV, so plugins like ArchivCZSK can use exteplayer3 on a Dreambox.

## Supported boxes
| Box | Architecture |
|---|---|
| DM520, DM525 | mipsel |
| DM900, DM920 | armhf |

One package for all of them. DreamOS 2.6 (Dreambox One/Two) is not supported.

## Features
- service type 5002 (exteplayer3): HLS, DASH, CENC DRM keys, separate audio (YouTube)
- pause / seek in the live-TV InfoBar
- EPG for 5002 services
- subtitles (embedded text tracks, external .srt, WebVTT)
- optional: replace Dream's servicemp3 (4097) for URLs, local files stay with Dream's player

## Install
On the box (ssh/telnet):
```sh
wget -qO- https://raw.githubusercontent.com/Blacker91/serviceapp-dreamos/dreamos/installer.sh | sh
```
It installs ServiceApp, exteplayer3 and ffmpeg and restarts enigma2.

Manually: download the `.deb` files from
[Releases](https://github.com/Blacker91/serviceapp-dreamos/releases) and
[exteplayer3 Releases](https://github.com/Blacker91/exteplayer3-dreamos/releases), then
```sh
dpkg -i exteplayer3-dreamos_*.deb ffmpeg-exteplayer3-dreamos_*.deb enigma2-plugin-systemplugins-serviceapp-dreamos_*.deb
systemctl restart enigma2
```
Do not run `apt-get -f install` afterwards, the packages are not in Dream's feed and apt would remove them.

## Settings
Menu → Plugins → ServiceApp.
- **Enigma2 playback system → serviceapp**: 4097 streams (e.g. IPTV bouquets) are played by exteplayer3.
  Only URLs by default; write `all` into `/etc/enigma2/serviceapp_replaceservicemp3` to take every 4097 service.
- **Subtitles**: font size, colour, distance from the bottom.

## Build
On Debian/Ubuntu:
```sh
sudo apt install g++-12-mipsel-linux-gnu g++-12-arm-linux-gnueabihf cmake git libboost-dev python3 curl
dreamos/fetch-sysroot.sh mipsel && dreamos/build.sh mipsel
dreamos/fetch-sysroot.sh arm    && dreamos/build.sh arm
dreamos/package.sh
```
`fetch-sysroot.sh` downloads the DreamOS headers and libraries from Dream's feed
(nothing from Dream is stored here). `build.sh` checks that every symbol the plugin needs
exists in enigma2 on the box. For DM900/DM920 use the enigma2 binary from your box:
`E2_BINARY=/path/to/enigma2 dreamos/fetch-sysroot.sh arm`.

## License
GPLv2, see [COPYING](COPYING). ServiceApp by mx3L and contributors
([oe-mirrors/serviceapp](https://github.com/oe-mirrors/serviceapp)), DreamOS port by Blacker91.
uchardet (MPL 1.1 / GPL 2 / LGPL 2.1) is linked statically.
