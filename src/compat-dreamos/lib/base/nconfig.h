/* DreamOS compat: T ePythonConfigQuery::getConfigValue(char const*, std::string&) */
#ifndef __lib_base_nconfig_h
#define __lib_base_nconfig_h
#include <string>
#include <lib/python/python.h>
class ePythonConfigQuery
{
	static ePyObject m_queryFunc;
public:
	static int getConfigValue(const char *key, std::string &value);
};

/* OpenPLi's eConfigManager is not in DreamOS; read through ePythonConfigQuery. */
#include <stdlib.h>
class eConfigManager
{
public:
	static int getConfigIntValue(const char *key, int defaultValue = 0)
	{
		std::string value;
		if (ePythonConfigQuery::getConfigValue(key, value) == 0 && !value.empty())
			return atoi(value.c_str());
		return defaultValue;
	}
	static bool getConfigBoolValue(const char *key, bool defaultValue = false)
	{
		std::string value;
		if (ePythonConfigQuery::getConfigValue(key, value) == 0 && !value.empty())
			return value == "True" || value == "true" || value == "1";
		return defaultValue;
	}
};
#endif
