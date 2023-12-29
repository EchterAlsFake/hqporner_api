import os
import requests  # pip install requests
import string
from functools import cached_property
from enum import Enum
from consts import *
from tqdm import tqdm  # pip install tqdm

headers = {
    "Referer": "https://hqporner.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
}  # Use this to prevent detection mechanisms...


class Quality(Enum):
    BEST = 'BEST'
    HALF = 'HALF'
    WORST = 'WORST'


class API:
    def __init__(self, url):
        self.html_content = requests.get(url=url, headers=headers).content.decode("utf-8")
        self.url = url

    @cached_property
    def video_title(self) -> str:
        match = PATTERN_TITLE.search(self.html_content)
        if match:
            title = match.group(1)
            return title

    @cached_property
    def cdn_url(self) -> str:
        match = PATTERN_CDN_URL.search(self.html_content)
        if match:
            url_path = match.group(1)
            return url_path

    @cached_property
    def pornstars(self) -> list:
        actress_names = PATTERN_ACTRESS.findall(self.html_content)
        return actress_names

    @cached_property
    def video_length(self) -> str:
        match = PATTERN_VIDEO_LENGTH.search(self.html_content)
        if match:
            return match.group(1)

    @cached_property
    def publish_date(self) -> str:
        match = PATTERN_PUBLISH_DATE.search(self.html_content)
        if match:
            return match.group(1)

    @cached_property
    def categories(self) -> list:
        categories = PATTERN_CATEGORY.findall(self.html_content)
        return categories

    @cached_property
    def video_qualities(self) -> list:
        quals = self.direct_download_urls
        qualities = set()  # Using a set to avoid duplicates

        for url in quals:
            match = PATTERN_RESOLUTION.search(url)
            if match:
                qualities.add(match.group(1))

        return sorted(qualities, key=int)  # Sorting to maintain a consistent order

    @cached_property
    def direct_download_urls(self) -> list:
        cdn_url = f"https://{self.cdn_url}"
        html_content = requests.get(url=cdn_url, headers=headers).content.decode("utf-8")
        urls = PATTERN_EXTRACT_CDN_URLS.findall(html_content)
        return urls

    def download(self, quality, output_path="./", no_title=False, callback=None):
        cdn_urls = self.direct_download_urls
        quals = self.video_qualities
        quality_url_map = {qual: url for qual, url in zip(quals, cdn_urls)}

        # Define the quality map
        quality_map = {
            Quality.BEST: max(quals, key=lambda x: int(x)),
            Quality.HALF: sorted(quals, key=lambda x: int(x))[len(quals) // 2],
            Quality.WORST: min(quals, key=lambda x: int(x))
        }

        selected_quality = quality_map[quality]
        download_url = f"https://{quality_url_map[selected_quality]}"
        title = self.strip_title(self.video_title)
        if no_title:
            final_path = output_path

        else:
            final_path = os.path.join(output_path, f"{title}.mp4")

        response = requests.get(download_url, stream=True)
        file_size = int(response.headers.get('content-length', 0))

        if callback is None:
            progress_bar = tqdm(total=file_size, unit='B', unit_scale=True, desc=title)

        downloaded_so_far = 0

        if not os.path.exists(final_path):
            with open(final_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
                    downloaded_so_far += len(chunk)

                    if callback:
                        callback(downloaded_so_far, file_size)

                    else:
                        progress_bar.update(len(chunk))

            if not callback:
                progress_bar.close()

    def strip_title(self, title) -> str:
        illegal_chars = '<>:"/\\|?*'
        cleaned_title = ''.join([char for char in title if char in string.printable and char not in illegal_chars])
        return cleaned_title

    def custom_callback(self, downloaded, total):
        """This is an example of how you can implement the custom callback"""

        percentage = (downloaded / total) * 100
        print(f"Downloaded: {downloaded} bytes / {total} bytes ({percentage:.2f}%)")

    def get_videos_by_actress(self, name: str):
        pages = 0
        # Brute force total pages

        while True:
            response = requests.get(f"https://hqporner.com/actress/{name}/{pages}").content.decode("utf-8")
            match = PATTERN_CANT_FIND.search(response)
            if "Sorry" in match.group(1).strip():
                break

            else:
                pages += 1

        for page in range(pages):
            root_url = "https://hqporner.com/actress/"
            if page == 0:
                final_url = f"{root_url}{name}"

            else:
                final_url = f"{root_url}{name}/{page}"

            html_content = requests.get(final_url, headers=headers).content.decode("utf-8")
            urls_ = PATTERN_VIDEOS_BY_ACTRESS.findall(html_content)
            for url_ in urls_:
                url = f"https://hqporner.com/hdporn/{url_}"
                if PATTERN_CHECK_URL.match(url):
                    yield API(url)
