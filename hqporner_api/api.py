import os
import httpx
import logging
import argparse
import traceback

from enum import Enum
from random import choice
from httpx import Response
from bs4 import BeautifulSoup
from functools import cached_property
from typing import Generator, Optional
from hqporner_api.modules.errors import *
from hqporner_api.modules.locals import *
from hqporner_api.modules.functions import *
from base_api.base import BaseCore, setup_logger
from base_api.modules.config import RuntimeConfig
from concurrent.futures import ThreadPoolExecutor, as_completed


class Checks:
    """
    Does the same as the decorators, but decorators are not good for IDEs because they get confused, so I moved
    them here.
    """
    def __init__(self):
        self.logger = setup_logger(name="HQPorner API - [Checks]", log_file=None, level=logging.CRITICAL)

    def enable_logging(self, log_file: str = None, level=None, log_ip: str = None, log_port: int = None):
        self.logger = setup_logger(name="HQPorner API - [Checks]", log_file=log_file, level=level, http_ip=log_ip, http_port=log_port)

    def check_url(self, url: str):
        """
        :param url: (str) The URL of the video to check for
        :return: (str) The URL if the URL is valid, otherwise raises InvalidURL
        """
        match = PATTERN_CHECK_URL.match(url)
        if match:
            self.logger.debug(f"URL matched {url}")
            return url

        else:
            raise InvalidURL

    @classmethod
    def check_actress(cls, actress: str):
        """
        :param: actress: (str) The name or URL of the actress to check for
        :return: (str) The name of the actress if valid, otherwise raises InvalidActress Exception
        """
        if actress.startswith("https://"):
            match = PATTERN_CHECK_URL_ACTRESS.match(actress)
            if match:
                name_extraction = re.compile(r'https://hqporner.com/actress/(.+)')
                name = name_extraction.search(actress).group(1)
                return name

            else:
                raise InvalidActress

        else:
            actress = actress.replace(" ", "-")  # For later url processing (makes sense, trust me)
            return actress
            # I assume that if it's not a URL, the user was smart enough to enter just the name lol


class ErrorVideo:
    """Drop-in-ish stand-in that raises when accessed."""
    def __init__(self, url: str, err: Exception):
        self.url = url
        self._err = err

    def __getattr__(self, _):
        # Any attribute access surfaces the original error
        raise self._err


class Pagination(Enum):
    QUERY = "query"
    PATH = "path"


def build_page_url(base_url: str, page: int, *,
                   mode: Pagination,
                   page_param: str = "p") -> str:
    """Erzeugt die Seiten-URL je nach Modus."""
    if page <= 1:
        return base_url
    if mode is Pagination.QUERY:
        sep = "&" if "?" in base_url else "?"
        return f"{base_url}{sep}{page_param}={page}"
    elif mode is Pagination.PATH:
        return f"{base_url.rstrip('/')}/{page}"


class Helper:
    def __init__(self, core: BaseCore):
        self.core = core
        self.url: Optional[str] = None

    def _get_video(self, url: str):
        return Video(url, core=self.core)

    def _make_video_safe(self, url: str):
        try:
            return Video(url, core=self.core)
        except Exception as e:
            return ErrorVideo(url, e)

    def iterator(self, pages: int = 0, max_workers: int = 20, base_url: str = None, pagination: Pagination = Pagination.QUERY,
                 page_param: str = "p", start_page: int = 1):
        if pages <= 0:
            return

        base = (base_url or self.url or "").rstrip("/")

        def extract_urls(html: str):
            return (f"{root_url}hdporn/{m}" for m in PATTERN_VIDEOS_ON_SITE.findall(html))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for i, page in enumerate(range(start_page, start_page + pages), start=0):
                current_url = build_page_url(base, page, mode=pagination, page_param=page_param)

                html_content = self.core.fetch(current_url)
                if isinstance(html_content, Response) or not html_content:
                    break

                video_urls = list(extract_urls(html_content))
                futures = [executor.submit(self._make_video_safe, u) for u in video_urls]
                for fut in as_completed(futures):
                    yield fut.result()


class Video:
    def __init__(self, url, core):
        """
        :param url: (str) The URL of the video
        """
        self.url = Checks().check_url(url)
        self.core = core
        self.logger = setup_logger(name="HQPorner API - [Video]", log_file=None, level=logging.CRITICAL)

    def enable_logging(self, log_file: str = None, level=None, log_ip: str = None, log_port: int = None):
        self.logger = setup_logger(name="HQPorner API - [Video]", log_file=log_file, level=level, http_ip=log_ip, http_port=log_port)

    @property
    def html_content(self):
        content = self.core.fetch(url=self.url)
        if isinstance(content, httpx.Response):
            self.logger.warning("404 Error! Applying experimental workaround...")
            content = self.core.fetch(url=str(self.url).replace("https://hqporner.com", "https://m.hqporner.com"))

        return content

    @cached_property
    def title(self) -> str:
        """
        :return: (str) The video title (lowercase)
        """
        return PATTERN_TITLE.search(self.html_content).group(1)

    @cached_property
    def cdn_url(self) -> str:
        """
        :return: (str) The Content Delivery Network URL for the video (can be used to embed the video)
        """
        return PATTERN_CDN_URL.search(self.html_content).group(1)

    @cached_property
    def pornstars(self) -> list:
        """
        :return: (list) The list of pornstars featured in the video
        """
        return PATTERN_ACTRESS.findall(self.html_content)  # There are videos where no pornstars are listed, so can be 0

    @cached_property
    def length(self) -> str:
        """
        :return: (str) The length of the video in h / m / s format
        """
        return  PATTERN_VIDEO_LENGTH.search(self.html_content).group(1)

    @cached_property
    def publish_date(self) -> str:
        """
        :return: (str) How many months ago the video was uploaded
        """
        return PATTERN_PUBLISH_DATE.search(self.html_content).group(1)

    @cached_property
    def tags(self) -> list:
        """
        :return: (list) A list of tags (categories) featured in this video
        """
        return PATTERN_TAGS.findall(self.html_content)

    @cached_property
    def video_qualities(self) -> list:
        """
        :return: (list) The available qualities of the video
        """
        quals = self.direct_download_urls()
        qualities = set()  # Using a set to avoid duplicates

        for url in quals:
            match = PATTERN_RESOLUTION.search(url)
            if match:
                qualities.add(match.group(1))

        return sorted(qualities, key=int)  # Sorting to maintain a consistent order

    def direct_download_urls(self) -> list:
        """
        :return: (list) The direct download urls for all available qualities
        """
        cdn_url = f"https://{self.cdn_url}"
        html_content = self.core.fetch(cdn_url)
        urls = PATTERN_EXTRACT_CDN_URLS.findall(html_content)
        return urls

    def download(self, quality, path="./", callback=None, no_title=False):
        """
        :param quality:
        :param path:
        :param callback:
        :param no_title:
        :return: (bool)
        """

        cdn_urls = self.direct_download_urls()
        quals = self.video_qualities
        quality_url_map = {qual: url for qual, url in zip(quals, cdn_urls)}

        # Define the quality map
        if not quals:
            raise NotAvailable

        quality_map = {
            "best": max(quals, key=lambda x: int(x)),
            "half": sorted(quals, key=lambda x: int(x))[len(quals) // 2],
            "worst": min(quals, key=lambda x: int(x))
        }

        if no_title is False:
            path = os.path.join(path, f"{self.title}.mp4")

        selected_quality = quality_map[quality]
        download_url = f"https://{quality_url_map[selected_quality]}"
        try:
            self.core.legacy_download(url=download_url, path=path, callback=callback)
            return True

        except Exception:
            error = traceback.format_exc()
            self.logger.error(error)
            return False

    def get_thumbnails(self) -> list:
        """
        :return: (list) First item = Thumbnail, others = Preview
        """

        id_from_url_pattern = re.compile("hqporner.com/hdporn/(.*?)-")
        id = id_from_url_pattern.search(self.url).group(1)
        title = self.title
        urls = []
        scripts_under_divs = []
        script = None

        query = title.replace(" ", "+")
        html_content = self.core.fetch(url=f"{root_url}?q={query}")
        soup = BeautifulSoup(html_content, features="html.parser")
        divs = soup.find_all('div', class_='row')

        for div in divs:
            scripts = div.find_all('script')
            scripts_under_divs.extend(scripts)

        pattern = re.compile(r'"(//[^"]+)"')
        for script in scripts_under_divs:
            if f"preload_{id}" in script.text:
                script = script.text
                break

        try:
            urls_ = pattern.findall(script)

        except TypeError:
            raise WeirdError("""
I tried searching for the video on HQPorner to receive the thumbnail, but when searching, HQPorner did NOT 
give the video in the results. This is an issue from HQPorner itself and not my fault. Please do not report this error.
There's no way to fix it, unless you find an API call to get a thumbnail for a video lol.
""") # Error from HQPorner itself

        main_thumbnail = urls_[0].replace("_1.jpg", "_main.jpg")
        urls.append("https:" + main_thumbnail)
        for url in urls_:
            urls.append("https:" + url)

        if urls is None or len(urls) == 0:
            raise ThumbnailError("Couldn't find any thumbnails for this video. Please report this issue in GitHub!")

        return urls


class Client(Helper):
    def __init__(self, core: Optional[BaseCore] = None):
        super().__init__(core)
        self.core = core or BaseCore(config=RuntimeConfig())
        self.core.initialize_session(headers) # These headers MUST be applied, otherwise the API will not work!
        self.logger = setup_logger(name="HQPorner API - [Client]", log_file=None, level=logging.CRITICAL)

    def enable_logging(self, log_file: str = None, level = None, log_ip: str = None, log_port: int = None):
        self.logger = setup_logger(name="HQPorner API - [Client]", log_file=log_file, level=level, http_ip=log_ip, http_port=log_port)

    def get_video(self, url: str) -> Video:
        """
        :param url: The video URL
        :return: Video object
        """
        return Video(url, self.core)

    def get_videos_by_actress(self, name: str, pages: int = 5, max_workers: int = 20) -> Generator[Video, None, None]:
        """
        :param pages: (int) The number of pages to fetch
        :param name: The actress name or the URL
        :param max_workers: (int) The maximum number of threads to use
        :return: Video object
        """
        name = Checks().check_actress(name)
        final_url = f"{root_url_actress}{name}"
        yield from self.iterator(pages=pages, base_url=final_url, start_page=0, max_workers=max_workers,
                                 pagination=Pagination.PATH)

    def get_videos_by_category(self, category: Category, pages: int = 5, max_workers: int = 20) -> Generator[Video, None, None]:
        """
        :param pages: (int) The number of pages to fetch
        :param category: Category: The video category
        :param max_workers: (int) The maximum number of threads to use
        :return: Video object
        """
        base_url = f"{root_url_category}{category}"
        yield from self.iterator(pages=pages, base_url=base_url, start_page=0, max_workers=max_workers,
                                 pagination=Pagination.PATH)


    def search_videos(self, query: str, pages: int = 5, max_workers: int = 20) -> Generator[Video, None, None]:
        """
        :param query:
        :param pages: (int) How many pages to fetch
        :param max_workers:
        :return: Video object
        """
        query = query.replace(" ", "+")
        self.url = f"{root_url}?q={query}"
        yield from self.iterator(pages=pages, max_workers=max_workers, base_url=self.url, start_page=0, pagination=Pagination.QUERY)

    def get_top_porn(self, sort_by: Sort, pages: int = 5, max_workers: int = 20) -> Generator[Video, None, None]:
        """
        :param pages: (int) How many pages to fetch
        :param sort_by: all_time, month, week
        :param max_workers: (int) The maximum number of threads to use
        :return: Video object
        """
        if sort_by == "all_time":
            url = root_url_top

        else:
            url = f"{root_url_top}{sort_by}"

        yield from self.iterator(pages=pages, base_url=url, start_page=0, pagination=Pagination.PATH,
                      max_workers=max_workers)

    def get_all_categories(self) -> list:
        """
        :return: (list) Returns all categories of HQporner as a list of strings
        """
        html_content = self.core.fetch("https://hqporner.com/categories")
        categories = PATTERN_ALL_CATEGORIES.findall(html_content)
        return categories

    def get_random_video(self) -> Video:
        """
        :return: Video object (random video from HQPorner)
        """
        html_content = self.core.fetch(root_random)
        videos = PATTERN_VIDEOS_ON_SITE_ALT.findall(html_content)
        self.logger.info(f"Got {len(videos)} videos from HQPorner")
        video = choice(videos) # The random-porn from HQPorner returns 3 videos, so we pick one of them
        return Video(f"{root_url}hdporn/{video}", self.core)

    def get_brazzers_videos(self, pages: int = 5, max_workers: int = 20) -> Generator[Video, None, None]:
        """
        :param pages: (int) How many pages to fetch
        :param max_workers: (int) The maximum number of threads to use
        :return: Video object
        """
        url = root_brazzers
        yield from self.iterator(pages=pages, base_url=url, start_page=0, pagination=Pagination.PATH,
                                 max_workers=max_workers)

def main():
    parser = argparse.ArgumentParser(description="API Command Line Interface")
    parser.add_argument("--download", metavar="URL (str)", type=str, help="URL to download from")
    parser.add_argument("--quality", metavar="best,half,worst", type=str, help="The video quality (best,half,worst)",
                        required=True)
    parser.add_argument("--file", metavar="Source to .txt file", type=str,
                        help="(Optional) Specify a file with URLs (separated with new lines)")
    parser.add_argument("--output", metavar="Output directory", type=str, help="The output path (with filename)",
                        required=True)
    parser.add_argument("--no-title", metavar="True,False", type=str,
                        help="Whether to apply video title automatically to output path or not", required=True)

    args = parser.parse_args()
    no_title = args.no_title
    if args.download:
        client = Client()
        video = client.get_video(args.download)
        video.download(quality=args.quality, path=args.output, no_title=no_title)

    if args.file:
        videos = []
        client = Client()

        with open(args.file, "r") as file:
            content = file.read().splitlines()

        for url in content:
            videos.append(client.get_video(url))

        for video in videos:
            video.download(quality=args.quality, path=args.output, no_title=no_title)


if __name__ == "__main__":
    videos = Client().get_brazzers_videos(max_workers=60)
    for video in videos:
        print(video.title)