#ifndef __dreamos_servicecenter_h
#define __dreamos_servicecenter_h

class eServiceCenter;
class iServiceHandler;

/* Handler currently registered in eServiceCenter for service type 'id' (NULL if none). */
iServiceHandler *dreamos_getServiceHandler(eServiceCenter *sc, int id);

#include <list>
#include <string>
/* File extensions registered for service type 'id' (empty list, -1 if none). */
int dreamos_getServiceExtensions(eServiceCenter *sc, int id, std::list<std::string> &out);

#endif
