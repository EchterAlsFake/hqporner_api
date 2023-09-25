import threading
import re
import os

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

https = "https://"

url = "https://hqporner.com/hdporn/103040-its_a_comfort_thing.html"


if not os.path.exists("/run/media/asuna/hdd/Pornos/"):
    os.mkdir("/run/media/asuna/hdd/Pornos/")

output_path = "/run/media/asuna/hdd/Pornos/"

headers = {
    "Referer": "https://hqporner.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
}  # Use this to prevent detection mechanisms...

def extract_title(url):
    html = requests.get(url, headers=headers).content
    beautifulsoup = BeautifulSoup(html, "lxml")
    return beautifulsoup.find("title").text


def extract_text_after_double_slash(url):
    html = requests.get(url, headers=headers).content
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


def download_raw(video):
    high_quality_url = get_final_urls(video)[-1]
    title = extract_title(video)
    url = f"http:{high_quality_url}"
    final_path = output_path + title + ".mp4"
    response = requests.get(url, stream=True)
    file_size = int(response.headers.get('content-length', 0))
    progress_bar = tqdm(total=file_size, unit='B', unit_scale=True, desc=title)
    if not os.path.exists(final_path):

        with open(final_path, 'wb') as file:
            # Iterate over the content in chunks
            for chunk in response.iter_content(chunk_size=1024):
                # Write the chunk to the file
                file.write(chunk)
                # Update the progress bar
                progress_bar.update(len(chunk))

        # Close the progress bar when the download is complete
        progress_bar.close()


def download_from_file():
    with open("/home/asuna/Downloads/url_file.txt", "r") as url_file:
        all_videos = url_file.read().splitlines()

        for video in all_videos:
            download_raw(video)

download_from_file()
