#!/usr/bin/env python3
# Check that every undefined symbol of serviceapp.so is provided by enigma2 or
# a library on the box, so the plugin cannot fail to load with "undefined symbol".
#   check-symbols.py <serviceapp.so> <sysroot> <nm>
import os
import subprocess
import sys

so, sr, nm = sys.argv[1:4]
libs = ["usr/bin/enigma2", "lib/libc.so.6", "lib/libm.so.6", "lib/libpthread.so.0", "lib/libdl.so.2",
        "lib/libgcc_s.so.1", "usr/lib/libstdc++.so.6", "usr/lib/libpython2.7.so.1.0", "usr/lib/libsigc-2.0.so.0"]
# OpenSSL is 1.0.0 (soname) on DreamOS 2.5 and 1.0.2 on DreamOS 2.6
ssl = "1.0.2" if os.path.exists(os.path.join(sr, "usr/lib/libssl.so.1.0.2")) else "1.0.0"
libs += ["usr/lib/libssl.so." + ssl, "usr/lib/libcrypto.so." + ssl]
libs += [l for l in ("lib/ld.so.1", "lib/ld-linux-armhf.so.3", "lib/ld-linux-aarch64.so.1")
         if os.path.exists(os.path.join(sr, l))]


def syms(path, defined):
    """names, plus name@version for versioned symbols (GLIBC_2.17, GLIBCXX_3.4.21, ...)"""
    out = subprocess.run([nm, "-D", "--defined-only" if defined else "-u", path],
                         capture_output=True, text=True, check=True).stdout
    r = set()
    for l in out.splitlines():
        if not l.split():
            continue
        s = l.split()[-1].replace("@@", "@")
        r.add(s.split("@")[0])
        if "@" in s:
            r.add(s)
    return r


provided = set()
for lib in libs:
    path = os.path.join(sr, lib)
    if not os.path.exists(path):
        sys.exit("missing %s in sysroot" % lib)
    provided |= syms(path, True)
ignore = {"_ITM_deregisterTMCloneTable", "_ITM_registerTMCloneTable", "__gmon_start__", "_Jv_RegisterClasses"}
undefined = syms(so, False)
# a versioned reference must match a version the box library defines, so a
# symbol from a newer glibc/libstdc++ than the box has is reported too
missing = sorted(s for s in undefined if s not in provided and s.split("@")[0] not in ignore)
print("undefined symbols: %d, unresolved: %d" % (len(undefined), len(missing)))
for s in missing:
    print("  " + subprocess.run(["c++filt", s], capture_output=True, text=True).stdout.strip())
sys.exit(1 if missing else 0)
