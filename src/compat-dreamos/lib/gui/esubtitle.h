/* DreamOS compat: OpenPLi subtitle page/user types, used internally only */
#ifndef __lib_gui_esubtitle_compat_h
#define __lib_gui_esubtitle_compat_h
#include <string>
#include <vector>
#include <lib/service/iservice.h>
#include <lib/dvb/idvb.h>
#include <lib/gdi/rgba.h>

struct ePangoSubtitlePageElement
{
	gRGB m_color;
	bool m_have_color;
	std::string m_pango_line;
	ePangoSubtitlePageElement(const gRGB &color, const std::string &text)
		: m_color(color), m_have_color(true), m_pango_line(text) {}
};

struct ePangoSubtitlePage
{
	pts_t m_show_pts;
	int m_timeout; /* ms */
	std::vector<ePangoSubtitlePageElement> m_elements;
	ePangoSubtitlePage() : m_show_pts(0), m_timeout(0) {}
	void clear() { m_elements.clear(); }
};

class iSubtitleUser
{
public:
	virtual void setPage(const ePangoSubtitlePage &page) = 0;
	virtual void destroy() = 0;
	virtual ~iSubtitleUser() {}
};
#endif
