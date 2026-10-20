#ifndef __dreamos_servicecenter_h
#define __dreamos_servicecenter_h

class eServiceCenter;
class iServiceHandler;

/* handler registered for service type id, or NULL */
iServiceHandler *dreamos_getServiceHandler(eServiceCenter *sc, int id);

#include <list>
#include <string>
/* file extensions registered for service type id */
int dreamos_getServiceExtensions(eServiceCenter *sc, int id, std::list<std::string> &out);

#endif
