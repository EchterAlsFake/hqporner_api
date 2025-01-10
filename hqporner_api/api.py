import asyncio
import os
import logging
import argparse
import traceback

from random import choice
from bs4 import BeautifulSoup
from typing import List
from base_api.base import BaseCore
from functools import cached_property
from hqporner_api.modules.errors import *
from hqporner_api.modules.locals import *
from hqporner_api.modules.functions import *
from base_api.modules import consts as bs_consts

bs_consts.HEADERS = headers
core = BaseCore()

logging.basicConfig(format='%(name)s %(levelname)s %(asctime)s %(message)s', datefmt='%I:%M:%S %p')
logger = logging.getLogger("HQPORNER API")
logger.setLevel(logging.DEBUG)

def disable_logging():
    logger.setLevel(logging.CRITICAL)


class Checks:
    """
    Does the same as the decorators, but decorators are not good for IDEs because they get confused, so I moved
    them here.
    """

    @classmethod
    def check_url(cls, url: str):
        """
        :param url: (str) The URL of the video to check for
        :return: (str) The URL if the URL is valid, otherwise raises InvalidURL
        """
        match = PATTERN_CHECK_URL.match(url)
        if match:
            logger.debug(f"URL matched {url}")
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
    def __init__(self, url, content):
        """
        :param url: (str) The URL of the video
        """
        self.url = url
        self.html_content = content

    @classmethod
    async def create(cls, url):
        content = await core.fetch(url)
        return cls(url, content)

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

    async def video_qualities(self) -> list:
        """
        :return: (list) The available qualities of the video
        """
        quals = await self.direct_download_urls()
        qualities = set()  # Using a set to avoid duplicates

        for url in quals:
            match = PATTERN_RESOLUTION.search(url)
            if match:
                qualities.add(match.group(1))

        return sorted(qualities, key=int)  # Sorting to maintain a consistent order

    async def direct_download_urls(self) -> list:
        """
        :return: (list) The direct download urls for all available qualities
        """
        cdn_url = f"https://{self.cdn_url}"
        html_content = await core.fetch(url=cdn_url)
        urls = PATTERN_EXTRACT_CDN_URLS.findall(html_content)
        return urls

    async def download(self, quality, path="./", callback=None, no_title=False):
        """
        :param quality:
        :param path:
        :param callback:
        :param no_title:
        :return: (bool)
        """

        cdn_urls = await self.direct_download_urls()
        quals = await self.video_qualities()
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
            await core.legacy_download(url=download_url, path=path, callback=callback)
            return True

        except Exception:
            error = traceback.format_exc()
            logger.error(error)
            return False

    async def get_thumbnails(self) -> list:
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
        html_content = await core.fetch(url=f"{root_url}/?q={query}")
        soup = BeautifulSoup(html_content)
        divs = soup.find_all('div', class_='row')

        for div in divs:
            scripts = div.find_all('script')
            scripts_under_divs.extend(scripts)

        pattern = re.compile(r'"(//[^"]+)"')
        for script in scripts_under_divs:
            if f"preload_{id}" in script.text:
                script = script.text
                break

        urls_ = pattern.findall(script)
        main_thumbnail = urls_[0].replace("_1.jpg", "_main.jpg")
        urls.append("https:" + main_thumbnail)
        for url in urls_:
            urls.append("https:" + url)

        return urls


class Client:

    @classmethod
    async def get_video(cls, url: str) -> Video:
        """
        :param url: The video URL
        :return: Video object
        """
        return await Video.create(url)

    @classmethod
    async def processor(cls, urls):
        tasks = []

        async def process_page(url, tasks):
            html = await core.fetch(url)
            if not check_for_page(html):
                for task in tasks:
                    task.cancel()
                    return None

            return html

        for url in urls:
            task = asyncio.create_task(process_page(url, tasks))
            tasks.append(task)

        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)

        except asyncio.CancelledError:
            pass

        final_results = [result for result in results if result not in (None, asyncio.CancelledError)]
        urls = []

        for html in final_results:
            urls_ = PATTERN_VIDEOS_ON_SITE.findall(html)
            for url in urls_:
                url = f"{root_url}hdporn/{url}"
                if PATTERN_CHECK_URL.match(url):
                    urls.append(url)

        video_tasks = [asyncio.create_task(Client.get_video(url)) for url in urls]
        video_results = await asyncio.gather(*video_tasks)
        return video_results

    @classmethod
    async def get_videos_by_actress(cls, name: str, pages: int = 2) -> List[Video]:
        """
        :param name: The actress name or the URL
        :param pages: How many pages to fetch
        :return: list of video objects
        """
        name = Checks().check_actress(name)
        urls_to_process = [f"{root_url_actress}{name}/{page}" for page in range(pages)]
        return await Client.processor(urls=urls_to_process)


    @classmethod
    async def get_videos_by_category(cls, category: Category, pages: int = 2) -> List[Video]:
        """
        :param category: Category: The video category
        :param pages: How many pages to fetch
        :return: Video object
        """
        urls = [f"{root_url_category}{category}/{page}" for page in range(pages)]
        return await Client.processor(urls=urls)


    @classmethod
    async def search_videos(cls, query: str, pages: int = 2) -> List[Video]:
        """
        :param query:
        :param pages: How many pages to fetch
        :return: Video object
        """
        query = query.replace(" ", "+")
        html_content = await core.fetch(url=f"{root_url}?q={query}")
        match = PATTERN_CANT_FIND.search(html_content)
        if "Sorry" in match.group(1).strip():
            raise NoVideosFound


        else:
            urls = [f"{root_url}?q={query}&page={page}" for page in range(pages)]
            return await Client.processor(urls)

    @classmethod
    async def get_top_porn(cls, sort_by: Sort, pages: int = 2) -> List[Video]:
        """
        :param sort_by: all_time, month, week
        :param pages: How many pages to fetch
        :return: List of video objects
        """
        if sort_by == "all_time":
            urls = [f"{root_url_top}{page}" for page in range(pages)]

        else:
            urls = [f"{root_url_top}{sort_by}/{page}" for page in range(pages)]

        return await Client.processor(urls)


    @classmethod
    async def get_all_categories(cls) -> list:
        """
        :return: (list) Returns all categories of HQporner as a list of strings
        """
        html_content = await core.fetch("https://hqporner.com/categories")
        categories = PATTERN_ALL_CATEGORIES.findall(html_content)
        return categories

    @classmethod
    async def get_random_video(cls) -> Video:
        """
        :return: Video object (random video from HQPorner)
        """
        html_content = await core.fetch(root_random)
        videos = PATTERN_VIDEOS_ON_SITE_ALT.findall(html_content)
        video = choice(videos) # The random-porn from HQPorner returns 3 videos, so we pick one of them
        return await Video.create(f"{root_url}hdporn/{video}")

    @classmethod
    async def get_brazzers_videos(cls, pages: int = 2) -> List[Video]:
        """
        :return: Video object
        """
        urls = [f"{root_brazzers}/{page}" for page in range(pages)]
        return await Client.processor(urls)


async def main():
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
    no_title = BaseCore().str_to_bool(args.no_title)

    if args.download:
        client = Client()
        video = await client.get_video(args.download)
        await video.download(quality=args.quality, path=args.output, no_title=no_title)

    if args.file:
        videos = []
        client = Client()

        with open(args.file, "r") as file:
            content = file.read().splitlines()

        for url in content:
            videos.append(await client.get_video(url))

        for video in videos:
            await video.download(quality=args.quality, path=args.output, no_title=no_title)


if __name__ == "__main__":
    asyncio.run(main())