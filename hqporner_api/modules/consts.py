import re

PATTERN_TITLE = re.compile(r'<h1 class="main-h1" style="line-height: 1em;">\r\n(.*?)</h1>')
PATTERN_CDN_URL = re.compile(r"url: '/blocks/altplayer\.php\?i=//(.*?)',")
PATTERN_ACTRESS = re.compile(r'/actress/(.*?)"')
PATTERN_PUBLISH_DATE = re.compile(r'fa-calendar">(.*?)</li>')
PATTERN_VIDEO_LENGTH = re.compile(r'<li class="icon fa-clock-o">(.*?)</li>')
PATTERN_TAGS = re.compile(r'class="tag-link click-trigger">(.*?)</a>')
PATTERN_VIDEOS_ON_SITE = re.compile(r'<a href="/hdporn/(.*?)" class="image featured non-overlay atfib n8hu6s" style="margin: 0;">')
PATTERN_VIDEOS_ON_SITE_ALT = re.compile(r'<a href="/hdporn/(.*?)" class="image featured non-overlay atfib" style="margin: 0;">')
PATTERN_CANT_FIND = re.compile(r'<p style="padding-bottom: 20px;">(.*?)</p>', re.DOTALL)
PATTERN_CHECK_URL = re.compile(r"https://hqporner.com/hdporn/(.*?).html")
PATTERN_CHECK_URL_ACTRESS = re.compile(r"https://hqporner.com/actress/(.*)")
PATTERN_CHECK_CATEGORY = re.compile(r"https://hqporner.com/category(.*?)")
PATTERN_EXTRACT_CDN_URLS = re.compile(r"href='//(.*?)' style=")
PATTERN_RESOLUTION = re.compile(r'(\d{3,4})\.mp4')
PATTERN_ALL_CATEGORIES = re.compile(r'<section class="box feature"><a href="/category/(.*?)" class="image featured atfib" style="margin: 0;">')


root_url = "https://hqporner.com/"
root_url_actress = "https://hqporner.com/actress/"
root_url_category = "https://hqporner.com/category/"
root_url_top = "https://hqporner.com/top/"
root_random = "https://hqporner.com/random-porn"
root_brazzers = "https://hqporner.com/studio/free-brazzers-videos"

headers = {
    "Referer": "https://hqporner.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
}
