#!/usr/bin/env python3
# Turn the enigma2-dev 4.3.3r3 headers into enigma2 4.5.1r11 (DreamOS 2.6)
# for everything ServiceApp uses. There is no 4.5.1r11 dev package at hand, so
# each change below was read from the Dreambox One image (enigma2 4.5.1r11-r0.0,
# aarch64): SWIG wrappers in enigma.py, vtables and the machine code of the
# functions that use the members. Everything else ServiceApp touches was
# compared the same way and is unchanged (vtables of all service interfaces,
# eServiceCenter maps, eServiceEvent, iAudioTrackInfo, eThread, eTimer,
# eSocketNotifier, eMainloop_native, eMessagePump).
#   e2-451-headers.py <sysroot>/usr/include/enigma2
import sys

h = sys.argv[1] + "/lib/service/iservice.h"
s = open(h).read()


def sub(old, new):
    global s
    if new in s:
        return
    if s.count(old) != 1:
        sys.exit("%s: expected text not found once: %r" % (h, old))
    s = s.replace(old, new)


# iStaticServiceInformation: new virtual after getLength (vtable slot 9)
sub("\tvirtual int getLength(const eServiceReference &ref);\n",
    "\tvirtual int getLength(const eServiceReference &ref);\n"
    "\tvirtual int64_t getLength64(const eServiceReference &ref);\n")

# eServiceReference: a second map follows transportHeaders (offset 216 on
# aarch64, sizeof 264); it holds std::string -> boost::any. Name unknown.
sub("\tstringMap transportHeaders;\n",
    "\tstringMap transportHeaders;\n"
    "\tstd::map<std::string, boost::any> dreamos26_properties;\n")
if "#include <boost/any.hpp>" not in s:
    sub("#include <lib/base/object.h>\n", "#include <lib/base/object.h>\n#include <boost/any.hpp>\n")

# iSubtitleTrackInfo: m_filter is a plain int (offset 64, m_gst_subtype 68,
# sizeof 72) instead of a malloc'ed int*
sub("\tint *m_filter;\n", "\tint m_filter;\n")
sub("m_forced(false), m_filter(NULL), m_gst_subtype(0)", "m_forced(false), m_filter(0), m_gst_subtype(0)")
sub("\t\t\tm_filter = (int*)malloc(sizeof(int));\n\t\t\t*m_filter = filter;\n", "\t\t\tm_filter = filter;\n")
sub("\t\tif (m_filter)\n\t\t\tfree (m_filter);\n", "")
sub("int getFilter() { return *m_filter; }", "int getFilter() { return m_filter; }")
sub("void setFilter(int filter) { *m_filter = filter; }", "void setFilter(int filter) { m_filter = filter; }")

# enums: new values (atUnknown stays -1)
sub("atFLAC, atWMA, atUnknown=-1", "atFLAC, atWMA, atTRUEHD, atUnknown=-1")
sub("\tenum { NONE, DVB, TTX, DVD, GST };", "\tenum { NONE, DVB, TTX, DVD, GST, TXT };")

open(h, "w").write(s)
print("enigma2 headers adapted to 4.5.1r11")
