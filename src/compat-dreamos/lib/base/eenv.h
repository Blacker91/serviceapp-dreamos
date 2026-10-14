/* DreamOS compat: declaration matching symbols exported by DreamOS 2.5 enigma2
   T eEnv::resolve(std::string const&) */
#ifndef __lib_base_eenv_h
#define __lib_base_eenv_h
#include <string>
class eEnv
{
public:
	static std::string resolve(const std::string &path);
};
#endif
