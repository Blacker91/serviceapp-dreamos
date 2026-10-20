#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import json


from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.Console import Console
from Components.config import config, ConfigSubsection, ConfigSelection, ConfigBoolean, getConfigListEntry, ConfigSubDict, ConfigInteger, ConfigNothing
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from Plugins.Plugin import PluginDescriptor
from Screens.InfoBar import InfoBar, MoviePlayer
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.BoundFunction import boundFunction
from enigma import eEnv, eServiceReference

from . import _
from . import serviceapp_client

try:
    from Components.SystemInfo import BoxInfo
    IMAGEDISTRO = BoxInfo.getItem("distro")
except Exception:
    try:
        from boxbranding import getImageDistro
        IMAGEDISTRO = getImageDistro()
    except Exception:
        # DreamOS has neither BoxInfo nor boxbranding
        IMAGEDISTRO = "dreamos"

SINKS_DEFAULT = ("", "")
SINKS_EXPERIMENTAL = ("dvbvideosinkexp", "dvbaudiosinkexp")

sink_choices = []
if (os.path.isfile(eEnv.resolve("$libdir/gstreamer-1.0/libgstdvbvideosink.so")) and
        os.path.isfile(eEnv.resolve("$libdir/gstreamer-1.0/libgstdvbaudiosink.so"))):
    sink_choices.append(("original", _("original")))
if (os.path.isfile(eEnv.resolve("$libdir/gstreamer-1.0/libgstdvbvideosinkexp.so")) and
        os.path.isfile(eEnv.resolve("$libdir/gstreamer-1.0/libgstdvbaudiosinkexp.so"))):
    sink_choices.append(("experimental", _("experimental")))

player_choices = [("gstplayer", _("gstplayer")), ("exteplayer3", _("exteplayer3"))]
SERVICEMP3_PLAYER_DEFAULT = "gstplayer"
# no gstplayer (DreamOS): offer exteplayer3 only
if not serviceapp_client.isGstPlayerAvailable() and serviceapp_client.isExtEplayer3Available():
    player_choices = [("exteplayer3", _("exteplayer3"))]
    SERVICEMP3_PLAYER_DEFAULT = "exteplayer3"
GSTPLAYER_VERSION = None
EXTEPLAYER3_VERSION = None

config.plugins.serviceapp = ConfigSubsection()
config_serviceapp = config.plugins.serviceapp

config_serviceapp.servicemp3 = ConfigSubsection()
config_serviceapp.servicemp3.replace = ConfigBoolean(default=False, descriptions={0: _("original"), 1: _("serviceapp")})
config_serviceapp.servicemp3.replace.value = serviceapp_client.isServiceMP3Replaced()
# which 4097 services ServiceApp plays when servicemp3 is replaced (DreamOS)
config_serviceapp.servicemp3.mode = ConfigSelection(default="urls",
    choices=[("urls", _("streams only")), ("all", _("streams and files"))])
config_serviceapp.servicemp3.mode.value = "all" if serviceapp_client.isServiceMP3ReplaceAll() else "urls"
config_serviceapp.servicemp3.player = ConfigSelection(default=SERVICEMP3_PLAYER_DEFAULT, choices=player_choices)

# DreamOS subtitle overlay
config_serviceapp.subtitles = ConfigSubsection()
config_serviceapp.subtitles.font_size = ConfigSelection(default="normal",
    choices=[("small", _("small")), ("normal", _("normal")), ("large", _("large")), ("xlarge", _("extra large"))])
config_serviceapp.subtitles.color = ConfigSelection(default="#ffffff",
    choices=[("#ffffff", _("white")), ("#ffff00", _("yellow")), ("#d0d0d0", _("light grey"))])
config_serviceapp.subtitles.background = ConfigSelection(default="black",
    choices=[("black", _("black")), ("semi", _("semi-transparent")), ("none", _("none (outline)"))])
config_serviceapp.subtitles.delay = ConfigSelection(default="0",
    choices=[(str(ms), "%+.1f s" % (ms / 1000.0) if ms else "0") for ms in range(-2000, 5001, 100)])
config_serviceapp.subtitles.position = ConfigSelection(default="6",
    choices=[(str(x), "%d %%" % x) for x in (2, 4, 6, 8, 10, 13, 16, 20, 25)])

config_serviceapp.options = ConfigSubDict()
config_serviceapp.options["servicemp3"] = ConfigSubsection()
config_serviceapp.options["servicegstplayer"] = ConfigSubsection()
config_serviceapp.options["serviceexteplayer3"] = ConfigSubsection()
for key in list(config_serviceapp.options.keys()):
    config_serviceapp.options[key].hls_explorer = ConfigBoolean(default=True, descriptions={False: _("false"), True: _("true")})
    config_serviceapp.options[key].autoselect_stream = ConfigBoolean(default=True, descriptions={False: _("false"), True: _("true")})
    config_serviceapp.options[key].connection_speed_kb = ConfigInteger(9999999, limits=(0, 9999999))
    config_serviceapp.options[key].autoturnon_subtitles = ConfigBoolean(default=True, descriptions={False: _("false"), True: _("true")})

config_serviceapp.gstplayer = ConfigSubDict()
config_serviceapp.gstplayer["servicemp3"] = ConfigSubsection()
config_serviceapp.gstplayer["servicegstplayer"] = ConfigSubsection()
for key in list(config_serviceapp.gstplayer.keys()):
    config_serviceapp.gstplayer[key].sink = ConfigSelection(default="original", choices=sink_choices)
    config_serviceapp.gstplayer[key].buffer_size = ConfigInteger(8192, (1024, 1024 * 64))
    config_serviceapp.gstplayer[key].buffer_duration = ConfigInteger(0, (0, 100))
    config_serviceapp.gstplayer[key].subtitle_enabled = ConfigBoolean(default=True, descriptions={False: _("false"), True: _("true")})

config_serviceapp.exteplayer3 = ConfigSubDict()
config_serviceapp.exteplayer3["servicemp3"] = ConfigSubsection()
config_serviceapp.exteplayer3["serviceexteplayer3"] = ConfigSubsection()
for key in list(config_serviceapp.exteplayer3.keys()):
    config_serviceapp.exteplayer3[key].aac_swdecoding = ConfigSelection(default="0", choices=[("0", _("off")), ("1", _("To AAC ADTS")), ("2", _("To AAC LATM"))])
    config_serviceapp.exteplayer3[key].eac3_swdecoding = ConfigBoolean(default=False, descriptions={False: _("false"), True: _("true")})
    config_serviceapp.exteplayer3[key].ac3_swdecoding = ConfigBoolean(default=False, descriptions={False: _("false"), True: _("true")})
    config_serviceapp.exteplayer3[key].dts_swdecoding = ConfigBoolean(default=False, descriptions={False: _("false"), True: _("true")})
    config_serviceapp.exteplayer3[key].mp3_swdecoding = ConfigBoolean(default=False, descriptions={False: _("false"), True: _("true")})
    config_serviceapp.exteplayer3[key].wma_swdecoding = ConfigBoolean(default=False, descriptions={False: _("false"), True: _("true")})
    config_serviceapp.exteplayer3[key].lpcm_injecion = ConfigBoolean(default=False, descriptions={False: _("false"), True: _("true")})
    config_serviceapp.exteplayer3[key].downmix = ConfigBoolean(default=False, descriptions={False: _("false"), True: _("true")})
    config_serviceapp.exteplayer3[key].rtmp_protocol = ConfigSelection(default="auto", choices=["auto", "ffmpeg", "librtmp"])


def key_to_setting_id(key):
    setting_id = None
    if key == "servicemp3":
        setting_id = serviceapp_client.OPTIONS_SERVICEMP3
    elif key == "serviceexteplayer3":
        setting_id = serviceapp_client.OPTIONS_SERVICEEXTEPLAYER3
    elif key == "servicegstplayer":
        setting_id = serviceapp_client.OPTIONS_SERVICEGSTPLAYER
    return setting_id


def init_serviceapp_settings():
    for key in list(config_serviceapp.options.keys()):
        setting_id = key_to_setting_id(key)
        serviceapp_cfg = config_serviceapp.options[key]

        serviceapp_client.setServiceAppSettings(setting_id,
                serviceapp_cfg.hls_explorer.value,
                serviceapp_cfg.autoselect_stream.value,
                serviceapp_cfg.connection_speed_kb.value,
                serviceapp_cfg.autoturnon_subtitles.value)

    for key in list(config_serviceapp.gstplayer.keys()):
        setting_id = key_to_setting_id(key)
        player_cfg = config_serviceapp.gstplayer[key]

        if player_cfg.sink.value == "original":
            video_sink, audio_sink = SINKS_DEFAULT
        elif player_cfg.sink.value == "experimental":
            video_sink, audio_sink = SINKS_EXPERIMENTAL
        else:
            continue

        serviceapp_client.setGstreamerPlayerSettings(setting_id,
                video_sink,
                audio_sink,
                player_cfg.subtitle_enabled.value,
                player_cfg.buffer_size.value,
                player_cfg.buffer_duration.value)

    for key in list(config_serviceapp.exteplayer3.keys()):
        setting_id = key_to_setting_id(key)
        player_cfg = config_serviceapp.exteplayer3[key]

        rtmp_proto_val = 0
        rtmp_proto_cfg_val = player_cfg.rtmp_protocol.value
        if rtmp_proto_cfg_val == "librtmp":
            rtmp_proto_val = 2
        elif rtmp_proto_cfg_val == "ffmpeg":
            rtmp_proto_val = 1
        else:
            rtmp_proto_val = 0
        serviceapp_client.setExtEplayer3Settings(setting_id,
                int(player_cfg.aac_swdecoding.value),
                player_cfg.dts_swdecoding.value,
                player_cfg.wma_swdecoding.value,
                player_cfg.lpcm_injecion.value,
                player_cfg.downmix.value,
                player_cfg.ac3_swdecoding.value,
                player_cfg.eac3_swdecoding.value,
                player_cfg.mp3_swdecoding.value,
                rtmp_proto_val)

    if config_serviceapp.servicemp3.player.value == "gstplayer":
        serviceapp_client.setServiceMP3GstPlayer()
    elif config_serviceapp.servicemp3.player.value == "exteplayer3":
        serviceapp_client.setServiceMP3ExtEplayer3()


init_serviceapp_settings()


class ServiceAppSettings(ConfigListScreen, Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.skinName = ["ServiceAppSettings", "Setup"]
        ConfigListScreen.__init__(self, [], session)
        self.setup_title = "ServiceApp - DreamOS port by Blacker91"
        self.onLayoutFinish.append(self.init_configlist)
        self.onClose.append(self.deinit_config)
        self["key_red"] = StaticText(_("Cancel"))
        self["key_green"] = StaticText(_("Ok"))
        self["description"] = Label("")
        self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
            {
                "cancel": self.keyCancel,
                "red": self.keyCancel,
                "ok": self.keyOk,
                "green": self.keyOk,
            }, -2)

    def init_configlist(self):
        self.setTitle(self.setup_title)
        config_serviceapp.servicemp3.player.addNotifier(
                lambda x: self.build_configlist(), initial_call=False)
        config_serviceapp.servicemp3.replace.addNotifier(
                lambda x: self.build_configlist(), initial_call=False)
        self.build_configlist()

    def deinit_config(self):
        del config_serviceapp.servicemp3.player.notifiers[:]
        del config_serviceapp.servicemp3.replace.notifiers[:]

    def gstplayer_options(self, gstplayer_options_cfg):
        config_list = []
        config_list.append(getConfigListEntry("  " + _("Sink"),
            gstplayer_options_cfg.sink, _("Select sink which you want to use.")))
        config_list.append(getConfigListEntry("  " + _("Embedded subtitles"),
            gstplayer_options_cfg.subtitle_enabled, _("Turn on the embedded subtitles support.")))
        config_list.append(getConfigListEntry("  " + _("Buffer size"),
            gstplayer_options_cfg.buffer_size, _("Set buffer size in kilobytes.")))
        config_list.append(getConfigListEntry("  " + _("Buffer duration"),
            gstplayer_options_cfg.buffer_duration, _("Set buffer duration in seconds.")))
        return config_list

    def exteplayer3_options(self, exteplayer3_options_cfg):
        config_list = []
        config_list.append(getConfigListEntry("  " + _("AAC software decoding"),
            exteplayer3_options_cfg.aac_swdecoding, _("Turn on AAC software decoding.")))
        config_list.append(getConfigListEntry("  " + _("EAC3 software decoding"),
            exteplayer3_options_cfg.eac3_swdecoding, _("Turn on EAC3 software decoding.")))
        config_list.append(getConfigListEntry("  " + _("AC3 software decoding"),
            exteplayer3_options_cfg.ac3_swdecoding, _("Turn on AC3 software decoding.")))
        config_list.append(getConfigListEntry("  " + _("DTS software decoding"),
            exteplayer3_options_cfg.dts_swdecoding, _("Turn on DTS software decoding.")))
        config_list.append(getConfigListEntry("  " + _("MP3 software decoding"),
            exteplayer3_options_cfg.dts_swdecoding, _("Turn on MP3 software decoding.")))
        config_list.append(getConfigListEntry("  " + _("WMA software decoding"),
            exteplayer3_options_cfg.wma_swdecoding, _("Turn on WMA1, WMA2, WMA/PRO software decoding.")))
        config_list.append(getConfigListEntry("  " + _("Stereo downmix"),
            exteplayer3_options_cfg.downmix, _("Turn on downmix to stereo, when software decoding is in use")))
        config_list.append(getConfigListEntry("  " + _("LPCM injection"),
            exteplayer3_options_cfg.lpcm_injecion, _("Software decoder use LPCM for injection (otherwise wav PCM will be used)")))
        config_list.append(getConfigListEntry("  " + _("RTMP protocol implementation"),
            exteplayer3_options_cfg.rtmp_protocol, _("Set which RTMP protocol implementation will be used for playback of RTMP streams")))
        return config_list

    def serviceapp_options(self, serviceapp_options_cfg):
        config_list = []
        config_list.append(getConfigListEntry("  " + _("Auto turn on subtitles"),
            serviceapp_options_cfg.autoturnon_subtitles, _("Automatically turn on subtitles if available.")))
        config_list.append(getConfigListEntry("  " + _("HLS Explorer"),
            serviceapp_options_cfg.hls_explorer, _("Turn on explorer to retrieve different quality streams from HLS variant playlist and select them via subservices.")))
        config_list.append(getConfigListEntry("  " + _("Auto select stream"),
            serviceapp_options_cfg.autoselect_stream, _("Turn on auto-selection of streams according to set Connection speed.")))
        config_list.append(getConfigListEntry("  " + _("Connection speed"),
            serviceapp_options_cfg.connection_speed_kb, _("Set connection speed in kb/s, according to which you want to have streams auto-selected")))
        return config_list

    def player_options(self, player_type, service_type):
        config_list = []
        player_cfg = getattr(config_serviceapp, player_type)[service_type]
        serviceapp_cfg = config_serviceapp.options[service_type]
        if player_type == "exteplayer3":
            config_list.append(getConfigListEntry("  " + _("ExtEplayer3"),
                ConfigSelection([EXTEPLAYER3_VERSION or "not installed"], EXTEPLAYER3_VERSION or _("not installed"))))
            if EXTEPLAYER3_VERSION:
                config_list += self.exteplayer3_options(player_cfg)
                config_list += self.serviceapp_options(serviceapp_cfg)
        if player_type == "gstplayer":
            config_list.append(getConfigListEntry("  " + _("GstPlayer"),
                ConfigSelection([GSTPLAYER_VERSION or "not installed"], GSTPLAYER_VERSION or _("not installed"))))
            if GSTPLAYER_VERSION:
                config_list += self.gstplayer_options(player_cfg)
                config_list += self.serviceapp_options(serviceapp_cfg)
        return config_list

    def build_configlist(self):
        config_list = [getConfigListEntry(_("Enigma2 playback system"),
            config_serviceapp.servicemp3.replace, _("Select the player which will be used for Enigma2 playback."))]
        if config_serviceapp.servicemp3.replace.value:
            if IMAGEDISTRO == "dreamos":
                config_list.append(getConfigListEntry(_("Play with ServiceApp"),
                    config_serviceapp.servicemp3.mode, _("Streams only, or also files from disk and network (NAS).")))
            config_list.append(getConfigListEntry(_("Player"),
                config_serviceapp.servicemp3.player, _("Select the player which will be used in serviceapp for Enigma2 playback.")))
            configlist_servicemp3 = [getConfigListEntry("", ConfigNothing())]
            configlist_servicemp3.append(getConfigListEntry(_("ServiceMp3 (%s)" % str(serviceapp_client.ID_SERVICEMP3)), ConfigNothing()))
            if config_serviceapp.servicemp3.player.value == "gstplayer":
                config_list += configlist_servicemp3 + self.player_options("gstplayer", "servicemp3")
            elif config_serviceapp.servicemp3.player.value == "exteplayer3":
                config_list += configlist_servicemp3 + self.player_options("exteplayer3", "servicemp3")
            else:
                config_list += configlist_servicemp3
        config_list.append(getConfigListEntry("", ConfigNothing()))
        config_list.append(getConfigListEntry(_("ServiceGstPlayer (%s)" % str(serviceapp_client.ID_SERVICEGSTPLAYER)), ConfigNothing()))
        config_list += self.player_options("gstplayer", "servicegstplayer")
        config_list.append(getConfigListEntry("", ConfigNothing()))
        config_list.append(getConfigListEntry(_("ServiceExtEplayer3 (%s)" % str(serviceapp_client.ID_SERVICEEXTEPLAYER3)), ConfigNothing()))
        config_list += self.player_options("exteplayer3", "serviceexteplayer3")
        if IMAGEDISTRO == "dreamos":
            config_list.append(getConfigListEntry("", ConfigNothing()))
            config_list.append(getConfigListEntry(_("Subtitles"), ConfigNothing()))
            config_list.append(getConfigListEntry("  " + _("Font size"),
                config_serviceapp.subtitles.font_size, _("Size of ServiceApp subtitles.")))
            config_list.append(getConfigListEntry("  " + _("Color"),
                config_serviceapp.subtitles.color, _("Color of ServiceApp subtitles.")))
            config_list.append(getConfigListEntry("  " + _("Background"),
                config_serviceapp.subtitles.background, _("Background behind ServiceApp subtitles.")))
            config_list.append(getConfigListEntry("  " + _("Delay"),
                config_serviceapp.subtitles.delay, _("Positive values show subtitles later.")))
            config_list.append(getConfigListEntry("  " + _("Distance from bottom"),
                config_serviceapp.subtitles.position, _("Distance of subtitles from the bottom edge of the screen.")))
        self["config"].list = config_list
        self["config"].l.setList(config_list)

    def keyOk(self):
        if config_serviceapp.servicemp3.replace.isChanged() or \
                (config_serviceapp.servicemp3.replace.value and config_serviceapp.servicemp3.mode.isChanged()):
            self.session.openWithCallback(self.save_settings_and_close,
                    MessageBox, _("Enigma2 playback system was changed and Enigma2 should be restarted\n\nDo you want to restart it now?"),
                    type=MessageBox.TYPE_YESNO)
        else:
            self.save_settings_and_close()

    def save_settings_and_close(self, callback=False):
        init_serviceapp_settings()
        if config_serviceapp.servicemp3.replace.value:
            serviceapp_client.setServiceMP3Replace(True, config_serviceapp.servicemp3.mode.value == "all")
        else:
            serviceapp_client.setServiceMP3Replace(False)
        self.saveAll()
        self.close(callback)


class ServiceAppPlayer(MoviePlayer):
    def __init__(self, session, service):
        MoviePlayer.__init__(self, session, service)
        self.skinName = ["ServiceAppPlayer", "MoviePlayer"]
        self.servicelist = InfoBar.instance and InfoBar.instance.servicelist

    def handleLeave(self, how):
        if how == "ask":
            self.session.openWithCallback(self.leavePlayerConfirmed,
                    MessageBox, _("Stop playing this movie?"))
        else:
            self.close()

    def leavePlayerConfirmed(self, answer):
        if answer:
            self.close()


class ServiceAppDetectPlayers(Screen):
    skin = """
        <screen position="center,center" size="500,340" title="ServiceApp - player check">
            <widget name="text" position="10,10" size="490,325" font="Regular;28" halign="center" valign="center" />
        </screen>
                """

    def __init__(self, session):
        Screen.__init__(self, session)
        self["text"] = Label()
        self.players_iter = iter(
                [("gstplayer_gst-1.0",
                    _("Detecting gstreamer player ..."),
                    self.detect_gstplayer),
                 ("exteplayer3",
                     _("Detecting exteplayer3 player ..."),
                     self.detect_exteplayer3)
                 ])
        self.onLayoutFinish.append(self.detect_next_player)

    def detect_next_player(self):
        player = next(self.players_iter, None)
        if player is not None:
            self["text"].setText(player[1])
            self.console = Console()
            self.console.ePopen(player[0], boundFunction(self.detect_player_cb, player[2]))
        else:
            self.close()

    def detect_player_cb(self, datafnc, data, retval, extra_args):
        datafnc(data, retval, extra_args)
        self.detect_next_player()

    def _get_first_json_data_from_string(self, data):
        jsondata = None
        for line in data.splitlines():
            try:
                jsondata = json.loads(line)
                break
            except ValueError as e:
                pass
        return jsondata

    def detect_gstplayer(self, data, retval, extra_args):
        global GSTPLAYER_VERSION
        GSTPLAYER_VERSION = None
        jsondata = self._get_first_json_data_from_string(data)
        if jsondata is None:
            print("[ServiceApp] cannot detect gstplayer version(1)!")
            return
        try:
            GSTPLAYER_VERSION = jsondata["GSTPLAYER_EXTENDED"]["version"]
        except KeyError:
            print("[ServiceApp] cannot detect gstplayer version(2)!")
        else:
            print("[ServiceApp] found gstplayer - %d version" % GSTPLAYER_VERSION)

    def detect_exteplayer3(self, data, retval, extra_args):
        global EXTEPLAYER3_VERSION
        EXTEPLAYER3_VERSION = None
        jsondata = self._get_first_json_data_from_string(data)
        if jsondata is None:
            print("[ServiceApp] cannot detect exteplayer3 version(1)!")
            return
        try:
            EXTEPLAYER3_VERSION = jsondata["EPLAYER3_EXTENDED"]["version"]
        except KeyError:
            print("[ServiceApp] cannot detect exteplayer3 version(2)!")
        else:
            print("[ServiceApp] found exteplayer3 - %d version" % EXTEPLAYER3_VERSION)


def main(session, **kwargs):

    def restart_enigma2(restart=False):
        if restart:
            from Screens.Standby import TryQuitMainloop
            session.open(TryQuitMainloop, 3)

    def open_serviceapp_settings(callback=None):
        session.openWithCallback(restart_enigma2, ServiceAppSettings)

    session.openWithCallback(open_serviceapp_settings, ServiceAppDetectPlayers)


def menu(menuid, **kwargs):
    if IMAGEDISTRO in ("openhdf", "teamblue"):
        if menuid == "system":
            return [(_("ServiceApp"), main, "serviceapp_setup", None)]
    else:
        if menuid == "rec":
            return [(_("ServiceApp"), main, "serviceapp_setup", None)]
    return []


def play_exteplayer3(session, service, **kwargs):
    ref = eServiceReference(5002, 0, service.getPath())
    session.open(ServiceAppPlayer, service=ref)


def play_gstplayer(session, service, **kwargs):
    ref = eServiceReference(5001, 0, service.getPath())
    session.open(ServiceAppPlayer, service=ref)


# DreamOS: the live-TV InfoBar only allows pause/seek while timeshift runs.
# Allow it for videos played by ServiceApp; live streams keep no pause.
SERVICEAPP_TYPES = (serviceapp_client.ID_SERVICEGSTPLAYER, serviceapp_client.ID_SERVICEEXTEPLAYER3)


def _servicemp3State():
    # 0 - 4097 not handled by ServiceApp, 1 - only 4097 URLs, 2 - all 4097 refs
    try:
        return serviceapp_client.serviceapp.servicemp3_replaced()
    except Exception:
        return 0


def _isServiceAppPlaying(screen):
    try:
        ref = screen.session.nav.getCurrentlyPlayingServiceReference()
        if ref is None:
            return False
        if ref.type in SERVICEAPP_TYPES:
            return True
        if ref.type == serviceapp_client.ID_SERVICEMP3:
            state = _servicemp3State()
            if state == 2:
                return True
            if state == 1:
                path = ref.getPath()
                return "://" in path and not path.startswith("file://")
        return False
    except Exception:
        return False


def _isLive(screen):
    # live stream = no known length; no pause there (and no timeshift message)
    try:
        service = screen.session.nav.getCurrentService()
        seek = service and service.seek()
        if seek is None:
            return True
        length = seek.getLength()
        if isinstance(length, (list, tuple)):
            return length[0] != 0 or length[1] <= 0
        return length <= 0
    except Exception:
        return False


def _takeOverServiceMP3(reason):
    # DreamOS: take 4097 again once everything is up
    if not serviceapp_client.isServiceMP3Replaced():
        return
    try:
        ret = serviceapp_client.serviceapp.servicemp3_takeover()
        state = _servicemp3State()
        print("[ServiceApp] %s: servicemp3 (4097) takeover %s, mode %s" % (reason,
            "OK" if ret == 0 else "FAILED", {0: "none", 1: "URLs only", 2: "all"}.get(state, state)))
    except Exception as e:
        print("[ServiceApp] %s: servicemp3 takeover error: %s" % (reason, e))


def _patchDreamOSInfoBar():
    try:
        from Screens.InfoBarGenerics import InfoBarSeek, InfoBarTimeshift
    except Exception as e:
        print("[ServiceApp] DreamOS InfoBar patch skipped:", e)
        return
    if getattr(InfoBarSeek, "_serviceapp_patched", False):
        return
    if not hasattr(InfoBarSeek, "isSeekable") or not hasattr(InfoBarTimeshift, "startTimeshift"):
        print("[ServiceApp] DreamOS InfoBar patch skipped: unexpected InfoBar API")
        return

    orig_isSeekable = InfoBarSeek.isSeekable

    def isSeekable(self):
        if _isServiceAppPlaying(self) and not _isLive(self):
            try:
                return self.getSeek() is not None
            except Exception:
                pass
        return orig_isSeekable(self)

    orig_startTimeshift = InfoBarTimeshift.startTimeshift

    def startTimeshift(self):
        if _isServiceAppPlaying(self) and hasattr(self, "playpauseService"):
            if not _isLive(self):
                self.playpauseService()
            return 0
        return orig_startTimeshift(self)

    InfoBarSeek.isSeekable = isSeekable
    InfoBarTimeshift.startTimeshift = startTimeshift
    InfoBarSeek._serviceapp_patched = True

    # DreamOS ActionMap drops timeshiftStart when recording is not allowed
    try:
        from Components.ActionMap import ActionMap
        if not getattr(ActionMap, "_serviceapp_patched", False):
            orig_action = ActionMap.action

            def action(self, context, act_name):
                if act_name == "timeshiftStart":
                    try:
                        func = self.actions.get(act_name)
                        screen = getattr(func, "im_self", None) or getattr(func, "__self__", None)
                        if screen is not None and _isServiceAppPlaying(screen) and hasattr(screen, "playpauseService"):
                            if _isLive(screen):
                                print("action -> ", context, act_name, "(ServiceApp: live, ignored)")
                            else:
                                print("action -> ", context, act_name, "(ServiceApp: play/pause)")
                                screen.playpauseService()
                            return 1
                    except Exception as e:
                        print("[ServiceApp] ActionMap hook error:", e)
                return orig_action(self, context, act_name)

            ActionMap.action = action
            ActionMap._serviceapp_patched = True
    except Exception as e:
        print("[ServiceApp] ActionMap patch skipped:", e)
    print("[ServiceApp] DreamOS InfoBar patched: pause/seek for service types", SERVICEAPP_TYPES,
        "+ 4097 (when servicemp3 is replaced: URLs only unless 'all')")


if IMAGEDISTRO == "dreamos":
    try:
        _patchDreamOSInfoBar()
    except Exception as e:
        print("[ServiceApp] DreamOS InfoBar patch failed:", e)
    _takeOverServiceMP3("plugin load")


# DreamOS subtitles: eSubtitleWidget has no text page, show them ourselves
import re as _re
_TAG_RE = _re.compile(r"<[^>]*>")


def _plainSubtitleText(text):
    # strip markup, unescape entities
    text = _TAG_RE.sub("", text)
    for a, b in (("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'), ("&apos;", "'"), ("&nbsp;", " "), ("&amp;", "&")):
        text = text.replace(a, b)
    return text.strip()


class ServiceAppSubtitles(Screen):
    OUTLINE = ((-1, -1), (1, -1), (-1, 1), (1, 1), (0, -1), (0, 1), (-1, 0), (1, 0))
    BACKGROUND = {"black": "#000000", "semi": "#50000000"}

    def __init__(self, session):
        from enigma import getDesktop
        size = getDesktop(0).size()
        w, h = size.width(), size.height()
        cfg = config_serviceapp.subtitles
        scale = {"small": 0.8, "normal": 1.0, "large": 1.25, "xlarge": 1.5}.get(cfg.font_size.value, 1.0)
        fs = max(16, int(h / 20.0 * scale))
        self._bh = int(fs * 1.3) * 3 + 10
        self._bx = int(w * 0.05)
        self._bw = w - 2 * self._bx
        self._by = h - int(h * int(cfg.position.value) / 100.0) - self._bh
        self._pad = (max(8, fs // 3), max(2, fs // 10))
        self._bg = self.BACKGROUND.get(cfg.background.value)
        widget = '<widget name="%s" position="%d,%d" size="%d,%d" font="Regular;%d" halign="center" valign="%s" ' \
                 'foregroundColor="%s" backgroundColor="%s" transparent="%d" zPosition="%d" />'
        box = (self._bx, self._by, self._bw, self._bh, fs)
        widgets = []
        if self._bg:
            # black box sized to the text, see _layout()
            widgets.append(widget % (("background",) + box + ("center", "#000000", self._bg, 0, 1)))
            widgets.append(widget % (("text",) + box + ("center", cfg.color.value, "#ff000000", 1, 2)))
            self.outlines = 0
        else:
            o = max(2, fs // 18)
            for i, (dx, dy) in enumerate(self.OUTLINE):
                widgets.append(widget % ("outline%d" % i, self._bx + dx * o, self._by + dy * o, self._bw, self._bh, fs,
                                         "bottom", "#000000", "#ff000000", 1, 1))
            widgets.append(widget % (("text",) + box + ("bottom", cfg.color.value, "#ff000000", 1, 2)))
            self.outlines = len(self.OUTLINE)
        self.skin = '<screen name="ServiceAppSubtitles" position="0,0" size="%d,%d" flags="wfNoBorder" ' \
                    'backgroundColor="#ff000000" zPosition="-1">%s</screen>' % (w, h, "".join(widgets))
        Screen.__init__(self, session)
        self["text"] = Label("")
        if self._bg:
            self["background"] = Label("")
        for i in range(self.outlines):
            self["outline%d" % i] = Label("")
        self._last = None
        from enigma import eTimer
        self._timer = eTimer()
        try:
            self._timer_conn = self._timer.timeout.connect(self._poll)   # DreamOS
        except AttributeError:
            self._timer.callback.append(self._poll)
        self._timer.start(100, False)

    def _layout(self):
        # shrink text and background to the size of the text, centred at the bottom
        from enigma import eSize, ePoint
        text = self["text"].instance
        if text is None:
            return
        text.resize(eSize(self._bw, self._bh))
        size = text.calculateSize()
        w = min(self._bw, size.width() + 2 * self._pad[0])
        h = min(self._bh, size.height() + 2 * self._pad[1])
        pos = ePoint(self._bx + (self._bw - w) // 2, self._by + self._bh - h)
        for name in ("background", "text"):
            self[name].instance.resize(eSize(w, h))
            self[name].instance.move(pos)

    def _poll(self):
        try:
            active, seq, text = serviceapp_client.serviceapp.subtitle_get()
        except Exception:
            return
        text = _plainSubtitleText(text) if text else ""
        if text == self._last:
            return
        self._last = text
        self["text"].setText(text)
        for i in range(self.outlines):
            self["outline%d" % i].setText(text)
        if text:
            if self._bg:
                self._layout()
            self.show()
        else:
            self.hide()


_subtitleOverlay = None
_subtitleSession = None


def _createSubtitleOverlay(*args):
    global _subtitleOverlay
    if _subtitleSession is None:
        return
    if _subtitleOverlay is not None:
        try:
            _subtitleOverlay._timer.stop()
            _subtitleSession.deleteDialog(_subtitleOverlay)
        except Exception as e:
            print("[ServiceApp] subtitle overlay delete error:", e)
        _subtitleOverlay = None
    try:
        _subtitleOverlay = _subtitleSession.instantiateDialog(ServiceAppSubtitles)
        _subtitleOverlay.hide()
        print("[ServiceApp] DreamOS subtitle overlay ready")
    except Exception as e:
        print("[ServiceApp] DreamOS subtitle overlay failed:", e)


def sessionstart(reason, **kwargs):
    global _subtitleSession
    if reason == 0 and IMAGEDISTRO == "dreamos":
        _takeOverServiceMP3("session start")
        _subtitleSession = kwargs.get("session")
        _createSubtitleOverlay()
        for c in (config_serviceapp.subtitles.font_size, config_serviceapp.subtitles.color,
                  config_serviceapp.subtitles.background, config_serviceapp.subtitles.position):
            c.addNotifier(_createSubtitleOverlay, initial_call=False)


def Plugins(**kwargs):
    return [
            PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=sessionstart),
            PluginDescriptor(name=_("ServiceApp"), description=_("setup player framework"),
                where=PluginDescriptor.WHERE_PLUGINMENU, icon="plugin.png", needsRestart=False, fnc=main),
            PluginDescriptor(name=_("ServiceApp"), description=_("setup player framework"),
                where=PluginDescriptor.WHERE_MENU, needsRestart=False, fnc=menu),
            PluginDescriptor(name=_("ServiceApp"), description=_("Play with ServiceExtEplayer3"),
                where=PluginDescriptor.WHERE_MOVIELIST, needsRestart=False, fnc=play_exteplayer3),
            ] + ([PluginDescriptor(name=_("ServiceApp"), description=_("Play with ServiceGstPlayer"),
                where=PluginDescriptor.WHERE_MOVIELIST, needsRestart=False, fnc=play_gstplayer)]
                if serviceapp_client.isGstPlayerAvailable() else [])
