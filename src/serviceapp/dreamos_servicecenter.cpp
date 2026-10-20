/*
 * DreamOS: read access to eServiceCenter's private handler/extension maps
 * (no getters in enigma2 4.3.3r3). Layout comes from the enigma2-dev header.
 */
#include <map>
#include <list>
#include <string>
#include <lib/base/object.h>
#include <lib/base/smartptr.h>
#include <lib/service/iservice.h>

#define private public
#define protected public
#include <lib/service/service.h>
#undef protected
#undef private

#include "dreamos_servicecenter.h"

iServiceHandler *dreamos_getServiceHandler(eServiceCenter *sc, int id)
{
	if (!sc)
		return NULL;
	std::map<int, ePtr<iServiceHandler> >::iterator it = sc->handler.find(id);
	if (it == sc->handler.end())
		return NULL;
	return (iServiceHandler *)it->second;
}

int dreamos_getServiceExtensions(eServiceCenter *sc, int id, std::list<std::string> &out)
{
	out.clear();
	if (!sc)
		return -1;
	std::map<int, std::list<std::string> >::iterator it = sc->extensions.find(id);
	if (it == sc->extensions.end())
		return -1;
	out = it->second;
	return 0;
}
