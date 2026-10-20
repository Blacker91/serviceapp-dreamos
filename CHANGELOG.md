# Changelog

## 0.5-dreamos7
- Subtitles: shown by ServiceApp's own overlay (DreamOS has no text subtitle
  page). Embedded text tracks, external .srt, WebVTT from streams.
  Font size, colour and position in the settings.
- Saving the settings keeps the "all" mode of `serviceapp_replaceservicemp3`.

## 0.5-dreamos6
- Fix possible crash on enigma2 shutdown with servicemp3 replaced.
- "Play with ServiceGstPlayer" is only offered when gstplayer is installed.

## 0.5-dreamos5
- Plugin icon.

## 0.5-dreamos4
- Replacing servicemp3 (4097) works and is verified at startup (logged).
- Default: only URLs are played by ServiceApp, local files and recordings stay
  with Dream's player. Write `all` into `/etc/enigma2/serviceapp_replaceservicemp3`
  to take every 4097 service.
- Pause/seek in the InfoBar also for 4097 services played by ServiceApp.
- exteplayer3 is the default player for replaced servicemp3.

## 0.5-dreamos3
- EPG in the channel list and InfoBar for 5002 services.

## 0.5-dreamos2
- Split packages: ServiceApp, exteplayer3, ffmpeg.

## 0.5-dreamos1
- Port to DreamOS 2.5 (enigma2 4.3.3r3, Python 2.7).
- Pause/seek in the live-TV InfoBar for 5001/5002 services.
- One package for mipsel (DM520/DM525) and armhf (DM900/DM920).
