#!/usr/bin/env python3
# Check that every undefined symbol of serviceapp.so is provided by enigma2 or
# a library on the box, so the plugin cannot fail to load with "undefined symbol".
#   check-symbols.py <serviceapp.so> <sysroot> <nm>
import os
import subprocess
import sys

so, sr, nm = sys.argv[1:4]
libs = ["usr/bin/enigma2", "lib/libc.so.6", "lib/libm.so.6", "lib/libpthread.so.0", "lib/libdl.so.2",
        "lib/libgcc_s.so.1", "usr/lib/libstdc++.so.6", "usr/lib/libpython2.7.so.1.0",
        "usr/lib/libssl.so.1.0.0", "usr/lib/libcrypto.so.1.0.0", "usr/lib/libsigc-2.0.so.0"]
libs += [l for l in ("lib/ld.so.1", "lib/ld-linux-armhf.so.3") if os.path.exists(os.path.join(sr, l))]


def syms(path, defined):
    out = subprocess.run([nm, "-D", "--defined-only" if defined else "-u", path],
                         capture_output=True, text=True, check=True).stdout
    return {l.split()[-1].split("@")[0] for l in out.splitlines() if l.split()}


provided = set()
for lib in libs:
    path = os.path.join(sr, lib)
    if not os.path.exists(path):
        sys.exit("missing %s in sysroot" % lib)
    provided |= syms(path, True)
ignore = {"_ITM_deregisterTMCloneTable", "_ITM_registerTMCloneTable", "__gmon_start__", "_Jv_RegisterClasses"}
undefined = syms(so, False)
missing = sorted(s for s in undefined if s not in provided and s not in ignore)
print("undefined symbols: %d, unresolved: %d" % (len(undefined), len(missing)))
for s in missing:
    print("  " + subprocess.run(["c++filt", s], capture_output=True, text=True).stdout.strip())
sys.exit(1 if missing else 0)
