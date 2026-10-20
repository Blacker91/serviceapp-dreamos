/* DreamOS compat: OpenPLi SubtitleTrack, used internally only */
#ifndef __lib_dvb_subtitle_compat_h
#define __lib_dvb_subtitle_compat_h
#include <string>
struct SubtitleTrack
{
	int type;
	int pid;
	int page_number;
	int magazine_number;
	std::string language_code;
	SubtitleTrack() : type(0), pid(0), page_number(0), magazine_number(0) {}
	bool operator<(const SubtitleTrack &o) const
	{
		if (type != o.type) return type < o.type;
		if (pid != o.pid) return pid < o.pid;
		if (page_number != o.page_number) return page_number < o.page_number;
		if (magazine_number != o.magazine_number) return magazine_number < o.magazine_number;
		return language_code < o.language_code;
	}
};
#endif
