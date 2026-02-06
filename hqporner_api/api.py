import os
import httpx
import logging
import argparse
import threading
import traceback

from enum import Enum
from random import choice
from bs4 import BeautifulSoup
from functools import cached_property
from hqporner_api.modules.consts import *
from hqporner_api.modules.errors import *
from hqporner_api.modules.locals import *
from base_api.base import BaseCore, setup_logger, Helper, _choose_quality_from_list, _normalize_quality_value
from base_api.modules.config import RuntimeConfig
from typing import Generator, Optional, List


try:
    import lxml
    parser = "lxml"

except (ModuleNotFoundError, ImportError):
    parser = "html.parser"


class Checks:
    """
    Does the same as the decorators, but decorators are not good for IDEs because they get confused, so I moved
    them here.
    """
    def __init__(self):
        self.logger = setup_logger(name="HQPorner API - [Checks]", log_file=None, level=logging.CRITICAL)

    def enable_logging(self, log_file: str = None, level=None, log_ip: str = None, log_port: int = None):
        self.logger = setup_logger(name="HQPorner API - [Checks]", log_file=log_file, level=level, http_ip=log_ip, http_port=log_port)

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


def build_page_urls(pagination: Pagination = Pagination.QUERY, base: str = None, pages: int = None,
                    page_param: str = "p", start_page: int = 1) -> List[str]:
    page_urls = []
    base = base.rstrip("/")
    for i, page in enumerate(range(start_page, start_page + pages), start=0):
        page_urls.append(build_page_url(base, page, mode=pagination, page_param=page_param))

    return page_urls


class Video:
    def __init__(self, url, core):
        """
        :param url: (str) The URL of the video
        """
        self.url = url
        self.core = core
        self.logger = setup_logger(name="HQPorner API - [Video]", log_file=None, level=logging.CRITICAL)
        self.is_mobile_fix = False
        if "m.hqporner" in self.url:
            self.is_mobile_fix = True

        self.html_content = self.core.fetch(url=self.url)
        if isinstance(self.html_content, httpx.Response):
            self.logger.warning("404 Error! Applying experimental workaround...")
            self.html_content = self.core.fetch(url=str(self.url).replace("https://hqporner.com", "https://m.hqporner.com"))
            self.is_mobile_fix = True

    def enable_logging(self, log_file: str = None, level=None, log_ip: str = None, log_port: int = None):
        self.logger = setup_logger(name="HQPorner API - [Video]", log_file=log_file, level=level, http_ip=log_ip, http_port=log_port)

    @cached_property
    def title(self) -> str:
        """
        :return: (str) The video title (lowercase)
        """
        if not self.is_mobile_fix:
            return PATTERN_TITLE.search(self.html_content).group(1)

        return PATTERN_TITLE_ALTERNATE.search(self.html_content).group(1)

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
        if not self.is_mobile_fix:
            return PATTERN_VIDEO_LENGTH.search(self.html_content).group(1)

        return PATTERN_VIDEO_LENGTH_ALTERNATIVE.findall(self.html_content)[1]

    @cached_property
    def publish_date(self) -> str:
        """
        :return: (str) How many months ago the video was uploaded
        """
        if not self.is_mobile_fix:
            return PATTERN_PUBLISH_DATE.search(self.html_content).group(1)

        return PATTERN_PUBLISH_DATE_ALTERNATE.search(self.html_content).group(1)

    @cached_property
    def tags(self) -> list:
        """
        :return: (list) A list of tags (categories) featured in this video
        """
        if not self.is_mobile_fix:
            return PATTERN_TAGS.findall(self.html_content)

        return PATTERN_TAGS_ALTERNATIVE.findall(self.html_content)

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

    def download(self, quality, path="./", callback=None, no_title=False, stop_event: threading.Event = None):
        cdn_urls = self.direct_download_urls()
        quals = self.video_qualities  # e.g., ["360", "480", "720"]
        if not quals:
            raise NotAvailable

        qn = _normalize_quality_value(quality)
        chosen_height = _choose_quality_from_list(quals, qn)

        quality_url_map = {int(re.search(r'(\d{3,4})', q).group(1)): url for q, url in zip(quals, cdn_urls)}
        download_url = f"https://{quality_url_map[chosen_height]}"

        if no_title is False:
            path = os.path.join(path, f"{self.title}.mp4")

        try:
            self.core.legacy_download(url=download_url, path=path, callback=callback, stop_event=stop_event)
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
        soup = BeautifulSoup(html_content, parser)
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
        super().__init__(core, video=Video)
        self.core = core or BaseCore(config=RuntimeConfig())
        self.core.initialize_session()
        self.core.session.headers.update(headers) # These headers MUST be applied, otherwise the API will not work!
        self.logger = setup_logger(name="HQPorner API - [Client]", log_file=None, level=logging.CRITICAL)

    def enable_logging(self, log_file: str = None, level = None, log_ip: str = None, log_port: int = None):
        self.logger = setup_logger(name="HQPorner API - [Client]", log_file=log_file, level=level, http_ip=log_ip, http_port=log_port)

    def get_video(self, url: str) -> Video:
        """
        :param url: The video URL
        :return: Video object
        """
        return Video(url, self.core)

    def get_videos_by_actress(self, name: str, pages: int = 5, videos_concurrency: int = None,
                            pages_concurrency: int = None) -> Generator[Video, None, None]:
        """
        :param pages: (int) The number of pages to fetch
        :param name: The actress name or the URL
        :param videos_concurrency: (int) How many threads to use to fetch videos
        :param pages_concurrency: (int) How many threads to use to fetch pages
        :return: Video object
        """
        name = Checks().check_actress(name)
        final_url = f"{root_url_actress}{name}"
        page_urls = build_page_urls(pagination=Pagination.PATH, base=final_url, pages=pages, start_page=0)

        videos_concurrency = videos_concurrency or self.core.config.videos_concurrency
        pages_concurrency = pages_concurrency or self.core.config.pages_concurrency

        yield from self.iterator(page_urls=page_urls, videos_concurrency=videos_concurrency,
                                 pages_concurrency=pages_concurrency, extractor=extractor_html)

    def get_videos_by_category(self, category: Category, pages: int = 5, videos_concurrency: int = None,
                            pages_concurrency: int = None) -> Generator[Video, None, None]:
        """
        :param pages: (int) The number of pages to fetch
        :param category: Category: The video category
        :param videos_concurrency: (int) How many threads to use to fetch videos
        :param pages_concurrency: (int) How many threads to use to fetch pages
        :return: Video object
        """
        url = f"{root_url_category}{category}"
        page_urls = build_page_urls(pagination=Pagination.PATH, base=url, pages=pages, start_page=0)
        videos_concurrency = videos_concurrency or self.core.config.videos_concurrency
        pages_concurrency = pages_concurrency or self.core.config.pages_concurrency
        yield from self.iterator(page_urls=page_urls, videos_concurrency=videos_concurrency,
                                 pages_concurrency=pages_concurrency, extractor=extractor_html)


    def search_videos(self, query: str, pages: int = 5, videos_concurrency: int = None,
                            pages_concurrency: int = None) -> Generator[Video, None, None]:
        """
        :param query:
        :param pages: (int) How many pages to fetch
        :param videos_concurrency: (int) How many threads to use to fetch videos
        :param pages_concurrency: (int) How many threads to use to fetch pages
        :return: Video object
        """
        query = query.replace(" ", "+")
        url = f"{root_url}?q={query}"
        page_urls = build_page_urls(pagination=Pagination.QUERY, base=url, pages=pages, start_page=1)
        videos_concurrency = videos_concurrency or self.core.config.videos_concurrency
        pages_concurrency = pages_concurrency or self.core.config.pages_concurrency
        yield from self.iterator(page_urls=page_urls, videos_concurrency=videos_concurrency,
                                 pages_concurrency=pages_concurrency, extractor=extractor_html)

    def get_top_porn(self, sort_by: Sort, pages: int = 5,videos_concurrency: int = None,
                            pages_concurrency: int = None) -> Generator[Video, None, None]:
        """
        :param pages: (int) How many pages to fetch
        :param sort_by: all_time, month, week
        :param videos_concurrency: (int) How many threads to use to fetch videos
        :param pages_concurrency: (int) How many threads to use to fetch pages
        :return: Video object
        """
        if sort_by == "all_time":
            url = root_url_top

        else:
            url = f"{root_url_top}{sort_by}"

        page_urls = build_page_urls(base=url, start_page=0, pagination=Pagination.PATH, pages=pages)
        videos_concurrency = videos_concurrency or self.core.config.videos_concurrency
        pages_concurrency = pages_concurrency or self.core.config.pages_concurrency
        yield from self.iterator(page_urls=page_urls, videos_concurrency=videos_concurrency,
                                 pages_concurrency=pages_concurrency, extractor=extractor_html)

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

    def get_brazzers_videos(self, pages: int = 5, videos_concurrency: int = None,
                            pages_concurrency: int = None) -> Generator[Video, None, None]:
        """
        :param pages: (int) How many pages to fetch
        :param videos_concurrency: (int) How many threads to use to fetch videos
        :param pages_concurrency: (int) How many threads to use to fetch pages
        :return: Video object
        """
        page_urls = build_page_urls(pagination=Pagination.PATH, pages=pages, base=root_brazzers, start_page=0)
        videos_concurrency = videos_concurrency or self.core.config.videos_concurrency
        pages_concurrency = pages_concurrency or self.core.config.pages_concurrency
        yield from self.iterator(page_urls=page_urls, extractor=extractor_html, videos_concurrency=videos_concurrency,
                                 pages_concurrency=pages_concurrency)


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
    main()