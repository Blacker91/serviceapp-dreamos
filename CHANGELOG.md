# Changelog

## 0.5-dreamos15
- Picons in the infobar for 5001/5002 channels with every skin: the reference
  reported to skins (sServiceref) is 4097, like Dream's player, because skin
  picon code only maps 4097 stream references to satellite picon names.
- No more "listDir(http://...) - error" messages: no subtitle file search for streams.

## 0.5-dreamos14
- DreamOS playback events evPlay, evPause and evSeek, like Dream's servicemp3.
  PlexDream waits for evPlay: number key seeking, resume from the last
  position and the Plex timeline (watched status) now work with exteplayer3.
- PlexDream player: hold << / >> to skip by an entered number of minutes
  (added at start, the PlexDream files are not changed).

## 0.5-dreamos12
- "Play with ServiceApp": new choice "files only". Files from disk/NAS are
  played by ServiceApp (exteplayer3), streams stay with Dream's player.
- Settings: "MP3 software decoding" changed the DTS setting instead of MP3.
- From upstream ServiceApp (oe-mirrors, 2024-2026): exteplayer3 options are
  passed as separate arguments ("-a" "0" instead of "-a 0"), string options
  from the play URL (e.g. #sapp_ffmpeg_option=) are no longer ignored, new
  options -b and -5/-6/-7 (DASH CENC keys) and sapp_args, HLS master
  playlists: correct relative variant URLs and audio of separate renditions,
  getInfo(sServiceref) fix, translated section titles in the settings.

## 0.5-dreamos11
- Separate packages for mipsel and armhf, `serviceapp.so` is no longer
  moved by postinst.
- Needs exteplayer3-dreamos 183-dreamos9 (exteplayer3 and ffmpeg in one package).

## 0.5-dreamos10
- Setting "Play with ServiceApp": streams only, or streams and files (disk, NAS).
- Subtitles: "Delay" setting, 2.3 s by default (the DM520 decoder reports its
  position ahead of the picture), "Display time" keeps them longer on screen.

## 0.5-dreamos8
- Subtitles: black box behind the text (setting: black / semi-transparent / outline).
- No pause in live streams (and no timeshift message), pause stays for videos.

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
