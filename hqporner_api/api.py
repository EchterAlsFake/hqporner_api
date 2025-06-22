import os
import logging
import argparse
import traceback

from random import choice
from typing import Generator
from bs4 import BeautifulSoup
from base_api.base import BaseCore, setup_logger
from functools import cached_property
from hqporner_api.modules.errors import *
from hqporner_api.modules.locals import *
from hqporner_api.modules.functions import *
from base_api.modules import config

core = BaseCore()

def refresh_core(custom_config=None, enable_logging=False, log_file: str = None, level=None): # Needed for Porn Fetch
    global core

    cfg = custom_config or config.config
    cfg.headers = headers
    core = BaseCore(cfg)
    if enable_logging:
        core.enable_logging(log_file=log_file, level=level)

refresh_core()
class Checks:
    """
    Does the same as the decorators, but decorators are not good for IDEs because they get confused, so I moved
    them here.
    """
    def __init__(self):
        self.logger = setup_logger(name="HQPorner API - [Checks]", log_file=None, level=logging.CRITICAL)

    def enable_logging(self, log_file: str = None, level=None):
        self.logger = setup_logger(name="HQPorner API - [Checks]", log_file=log_file, level=level)

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


class Video:
    def __init__(self, url):
        """
        :param url: (str) The URL of the video
        """
        self.url = Checks().check_url(url)
        self.logger = setup_logger(name="HQPorner API - [Video]", log_file=None, level=logging.CRITICAL)

    def enable_logging(self, log_file: str = None, level=None):
        self.logger = setup_logger(name="HQPorner API - [Video]", log_file=log_file, level=level)

    @property
    def html_content(self):
        return core.fetch(url=self.url)

    @cached_property
    def title(self) -> str:
        """
        :return: (str) The video title (lowercase)
        """
        match = PATTERN_TITLE.search(self.html_content)
        if match:
            title = match.group(1)
            return title

        else:
            raise WeirdError

    @cached_property
    def cdn_url(self) -> str:
        """
        :return: (str) The Content Delivery Network URL for the video (can be used to embed the video)
        """
        match = PATTERN_CDN_URL.search(self.html_content)
        if match:
            url_path = match.group(1)
            return url_path

        else:
            raise WeirdError

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
        match = PATTERN_VIDEO_LENGTH.search(self.html_content)
        if match:
            return match.group(1)

        else:
            raise WeirdError

    @cached_property
    def publish_date(self) -> str:
        """
        :return: (str) How many months ago the video was uploaded
        """
        match = PATTERN_PUBLISH_DATE.search(self.html_content)
        if match:
            return match.group(1)

        else:
            raise WeirdError

    @cached_property
    def tags(self) -> list:
        """
        :return: (list) A list of tags (categories) featured in this video
        """
        tags = PATTERN_TAGS.findall(self.html_content)
        if len(tags) > 0:
            return tags

        else:
            raise WeirdError

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
        html_content = core.fetch(cdn_url)
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
            core.legacy_download(url=download_url, path=path, callback=callback)
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
        html_content = core.fetch(url=f"{root_url}/?q={query}")
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
            raise WeirdError("Error from HQPorner, can't do anything about it.") # Error from HQPorner itself

        main_thumbnail = urls_[0].replace("_1.jpg", "_main.jpg")
        urls.append("https:" + main_thumbnail)
        for url in urls_:
            urls.append("https:" + url)

        return urls


class Client:
    def __init__(self):
        self.logger = setup_logger(name="HQPorner API - [Client]", log_file=None, level=logging.CRITICAL)

    def enable_logging(self, log_file: str = None, level = None):
        self.logger = setup_logger(name="HQPorner API - [Client]", log_file=log_file, level=level)

    @classmethod
    def get_video(cls, url: str) -> Video:
        """
        :param url: The video URL
        :return: Video object
        """
        return Video(url)


    def get_videos_by_actress(self, name: str) -> Generator[Video, None, None]:
        """
        :param name: The actress name or the URL
        :return: Video object
        """
        name = Checks().check_actress(name)
        self.logger.info("Actress is valid")
        for page in range(1, 100):
            self.logger.info(f"Iterating for page: {page}")
            final_url = f"{root_url_actress}{name}/{page}"
            html_content = core.fetch(final_url)
            if not check_for_page(html_content):
                self.logger.info("No more videos available, breaking")
                break

            urls_ = PATTERN_VIDEOS_ON_SITE.findall(html_content)
            for url_ in urls_:
                url = f"{root_url}hdporn/{url_}"
                if PATTERN_CHECK_URL.match(url):
                    yield Video(url)


    def get_videos_by_category(self, category: Category) -> Generator[Video, None, None]:
        """
        :param category: Category: The video category
        :return: Video object
        """
        for page in range(100):
            self.logger.info(f"Iterating for page: {page}")
            html_content = core.fetch(url=f"{root_url_category}{category}/{page}")
            if not check_for_page(html_content):
                self.logger.info("No more videos available, breaking")
                break

            else:
                urls = PATTERN_VIDEOS_ON_SITE.findall(html_content)
                for url in urls:
                    yield Video(f"{root_url}hdporn/{url}")


    def search_videos(self, query: str) -> Generator[Video, None, None]:
        """
        :param query:
        :return: Video object
        """
        query = query.replace(" ", "+")
        html_content = core.fetch(url=f"{root_url}?q={query}")
        match = PATTERN_CANT_FIND.search(html_content)
        if "Sorry" in match.group(1).strip():
            raise NoVideosFound

        else:
            for page in range(100):
                self.logger.info(f"Iterating for page: {page}")
                html_content = core.fetch(url=f"{root_url}?q={query}&p={page}")
                if not check_for_page(html_content):
                    break

                else:
                    urls = PATTERN_VIDEOS_ON_SITE.findall(html_content)
                    for url in urls:
                        yield Video(f"{root_url}hdporn/{url}")

    def get_top_porn(self, sort_by: Sort) -> Generator[Video, None, None]:
        """
        :param sort_by: all_time, month, week
        :return: Video object
        """
        for page in range(100):
            self.logger.debug(f"Iterating for page: {page}")
            if sort_by == "all_time":
                html_content = core.fetch(f"{root_url_top}{page}")

            else:
                html_content = core.fetch(f"{root_url_top}{sort_by}/{page}")

            if not check_for_page(html_content):
                self.logger.info("No more videos available, breaking")
                break

            else:
                urls = PATTERN_VIDEOS_ON_SITE.findall(html_content)
                for url in urls:
                    yield Video(f"{root_url}hdporn/{url}")

    @classmethod
    def get_all_categories(cls) -> list:
        """
        :return: (list) Returns all categories of HQporner as a list of strings
        """
        html_content = core.fetch("https://hqporner.com/categories")
        categories = PATTERN_ALL_CATEGORIES.findall(html_content)
        return categories

    def get_random_video(self) -> Video:
        """
        :return: Video object (random video from HQPorner)
        """
        html_content = core.fetch(root_random)
        videos = PATTERN_VIDEOS_ON_SITE_ALT.findall(html_content)
        self.logger.info(f"Got {len(videos)} videos from HQPorner")
        video = choice(videos) # The random-porn from HQPorner returns 3 videos, so we pick one of them
        return Video(f"{root_url}hdporn/{video}")

    def get_brazzers_videos(self) -> Generator[Video, None, None]:
        """
        :return: Video object
        """
        for page in range(100):
            self.logger.info(f"Iterating for page: {page}")
            html_content = core.fetch(url=f"{root_brazzers}/{page}")
            if not check_for_page(html_content):
                break

            else:
                urls = PATTERN_VIDEOS_ON_SITE.findall(html_content)
                for url_ in urls:
                    yield Video(f"{root_url}hdporn/{url_}")


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
    video = Client().get_video("https://hqporner.com/hdporn/121767-breakfast_with_creampie.html")
    print(video.cdn_url)
    print(video.direct_download_urls())


    #main()

