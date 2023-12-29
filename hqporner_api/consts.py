import re

PATTERN_TITLE = re.compile(r'<h1 class="main-h1" style="line-height: 1em;">\r\n(.*?)</h1>')
PATTERN_CDN_URL = re.compile(r"url: '/blocks/altplayer\.php\?i=//(.*?)',")
PATTERN_ACTRESS = re.compile(r'/actress/(.*?)"')
PATTERN_PUBLISH_DATE = re.compile(r'fa-calendar">(.*?)</li>')
PATTERN_VIDEO_LENGTH = re.compile(r'<li class="icon fa-clock-o">(.*?)</li>')
PATTERN_CATEGORY = re.compile(r'class="tag-link click-trigger">(.*?)</a>')
PATTERN_VIDEOS_BY_ACTRESS = re.compile(r'<a href="/hdporn/(.*?)" class="image featured non-overlay atfib')
PATTERN_CANT_FIND = re.compile(r'<p style="padding-bottom: 20px;">(.*?)</p>', re.DOTALL)
PATTERN_CHECK_URL = re.compile(r"https://hqporner.com/hdporn/(.*?).html")
PATTERN_EXTRACT_CDN_URLS = re.compile(r"href='//(.*?)' style=")
PATTERN_RESOLUTION = re.compile(r'(\d{3,4})\.mp4')