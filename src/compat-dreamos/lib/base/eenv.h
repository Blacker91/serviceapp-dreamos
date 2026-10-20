/* DreamOS compat: eEnv as exported by DreamOS enigma2 */
#ifndef __lib_base_eenv_h
#define __lib_base_eenv_h
#include <string>
class eEnv
{
public:
	static std::string resolve(const std::string &path);
};
#endif
