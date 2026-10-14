/* DreamOS compat: ServiceApp only uses PSignal from C++ (CONNECT), so plain sigc
   signals are sufficient. */
#ifndef __lib_python_connections_h
#define __lib_python_connections_h
#include <lib/base/sigc.h>
template <class R> class PSignal0 : public sigc::signal0<R> {};
template <class R, class V0> class PSignal1 : public sigc::signal1<R, V0> {};
template <class R, class V0, class V1> class PSignal2 : public sigc::signal2<R, V0, V1> {};
#endif
