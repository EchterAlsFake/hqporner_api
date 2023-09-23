import requests
from bs4 import BeautifulSoup
import re

https = "https://"
url = "https://hqporner.com/hdporn/113337-sweaty_feet_have_the_best_taste.html"


def extract_text_after_double_slash(url):
    html = requests.get(url).content
    beautifulsoup = BeautifulSoup(html, "lxml")
    url_pattern = re.compile(r"url: '/blocks/altplayer\.php\?i=//(.*?)',")
    match = url_pattern.search(str(beautifulsoup))

    if match:
        url_path = match.group(1)
        return url_path


def get_final_urls(url):
    base_url = extract_text_after_double_slash(url)
    final_content = requests.get(https + base_url).content
    soup = BeautifulSoup(final_content, "lxml")
    for script in soup.find_all('script'):
        if 'do_pl()' in script.text:
            script_content = script.text
            break

    video_urls = re.findall(r'//[^\'"]+\.mp4', script_content)
    urls = []
    for url in video_urls:
        urls.append(url) if not url in urls else ""

    return urls

urls = get_final_urls(url)

for url in urls:
    print(f"https:{url}")