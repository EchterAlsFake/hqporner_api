import os
import string
from functools import cached_property, wraps
from random import choice
from typing import Any, Generator, Callable

from hqporner_api.modules.locals import *
from hqporner_api.modules.errors import *
from hqporner_api.modules.functions import *
from hqporner_api.modules.progress_bars import *


def validate_url(func: Callable):
    @wraps(func)
    def wrapper(self, url, *args, **kwargs) -> Any:
        if check_url(url):
            return func(self, url, *args, **kwargs)
        else:
            raise InvalidURL
    return wrapper


def validate_actress(func: Callable):
    @wraps(func)
    def wrapper(self, actress,  *args, **kwargs) -> Callable:
        if check_actress(actress):
            return func(self, actress, *args, **kwargs)

        else:
            raise InvalidActress

    return wrapper


def validate_category(func: Callable):
    @wraps(func)
    def wrapper(self, category: Category, *args,  **kwargs):
        if check_category(category):
            return func(self, category, *args, **kwargs)

        else:
            raise InvalidCategory

    return wrapper


class Video:
    """
    Creates a Video object, which can be used to retrieve information of a HQPorner video and download it.
    """
    @validate_url
    def __init__(self, url):
        """
        Initialize a new Video instance.

        This method takes a URL, validates it, and then fetches the HTML content of the web page at that URL.

        Args:
            url (str): A URL string pointing to a video. The URL should be valid and accessible.

        Attributes:
            url (str): The URL of the video.
            html_content (str): The HTML content of the web page at the provided URL.
        """
        self.url = url
        self.html_content = requests.get(url=self.url, headers=headers).content.decode("utf-8")

    @classmethod
    def fix_quality(cls, quality):
        if isinstance(quality, Quality):
            return quality

        else:
            if str(quality) == "best":
                return Quality.BEST

            elif str(quality) == "half":
                return Quality.HALF

            elif str(quality) == "worst":
                return Quality.WORST

    @cached_property
    def video_title(self) -> str:
        """
        :return: str: The video title (lowercase)
        """
        match = PATTERN_TITLE.search(self.html_content)
        if match:
            title = match.group(1)
            return title

    @cached_property
    def cdn_url(self) -> str:
        """
        :return: str: The Content Delivery Network URL for the video
        """
        match = PATTERN_CDN_URL.search(self.html_content)
        if match:
            url_path = match.group(1)
            return url_path

    @cached_property
    def pornstars(self) -> list:
        """
        :return: list: The list of pornstars featured in the video
        """
        actress_names = PATTERN_ACTRESS.findall(self.html_content)
        return actress_names

    @cached_property
    def video_length(self) -> str:
        """
        :return: str: The length of the video in h / m / s format
        """
        match = PATTERN_VIDEO_LENGTH.search(self.html_content)
        if match:
            return match.group(1)

    @cached_property
    def publish_date(self) -> str:
        """
        :return: str: How many months ago the video was uploaded
        """
        match = PATTERN_PUBLISH_DATE.search(self.html_content)
        if match:
            return match.group(1)

    @cached_property
    def categories(self) -> list:
        """
        :return: list: A list of categories featured in this video
        """
        categories = PATTERN_CATEGORY.findall(self.html_content)
        return categories

    @cached_property
    def video_qualities(self) -> list:
        """
        :return: list: The available qualities of the video
        """
        quals = self.direct_download_urls
        qualities = set()  # Using a set to avoid duplicates

        for url in quals:
            match = PATTERN_RESOLUTION.search(url)
            if match:
                qualities.add(match.group(1))

        return sorted(qualities, key=int)  # Sorting to maintain a consistent order

    @cached_property
    def direct_download_urls(self) -> list:
        """
        :return: list: The direct download urls for all available qualities
        """
        cdn_url = f"https://{self.cdn_url}"
        html_content = requests.get(url=cdn_url, headers=headers).content.decode("utf-8")
        urls = PATTERN_EXTRACT_CDN_URLS.findall(html_content)
        return urls

    def download(self, quality, output_path="./", no_title=False, callback=None):
        """
        :param quality:
        :param output_path:
        :param no_title:
        :param callback:
        :return:
        """
        quality = self.fix_quality(quality)

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
            progress_bar = Callback()

        downloaded_so_far = 0

        if not os.path.exists(final_path):
            with open(final_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
                    downloaded_so_far += len(chunk)

                    if callback:
                        callback(downloaded_so_far, file_size)

                    else:
                        progress_bar.text_progress_bar(downloaded=downloaded_so_far, total=file_size)

            if not callback:
                del progress_bar

    @classmethod
    def strip_title(cls, title: str) -> str:
        """
        :param title:
        :return: str: strips out non UTF-8 chars of the title
        """
        illegal_chars = '<>:"/\\|?*'
        cleaned_title = ''.join([char for char in title if char in string.printable and char not in illegal_chars])
        return cleaned_title


class Client:

    @validate_url
    def get_video(self, url: str) -> Video:
        """
        :param url:
        :return: Video object
        """
        return Video(url)

    @validate_actress
    def get_videos_by_actress(self, name: str, pages: int = 5) -> Generator[Video, None, None]:
        """
        :param name:
        :param pages: int: one page contains 46 videos
        :return:
        """
        match = re.search("hqporner.com/actress/(.+)", name)
        if match:
            name = match.group(1)

        name = name.replace(" ", "-")
        for page in range(1, int(pages + 1)):
            final_url = f"{root_url_actress}{name}/{page}"
            html_content = requests.get(final_url, headers=headers).content.decode("utf-8")
            if not check_for_page(html_content):
                break

            urls_ = PATTERN_VIDEOS_ON_SITE.findall(html_content)
            for url_ in urls_:
                url = f"{root_url}hdporn/{url_}"
                if PATTERN_CHECK_URL.match(url):
                    yield Video(url)

    @validate_category
    def get_videos_by_category(self, category: Category, pages=5) -> Generator[Video, None, None]:
        """
        :param category: Category: The video category
        :param pages: int: one page contains 46 videos
        :return:
        """
        for page in range(1, int(pages + 1)):
            html_content = requests.get(url=f"{root_url_category}{category}/{page}").content.decode("utf-8")
            if not check_for_page(html_content):
                break

            else:
                urls = PATTERN_VIDEOS_ON_SITE.findall(html_content)
                for url in urls:
                    yield Video(f"{root_url}hdporn/{url}")

    @classmethod
    def search_videos(cls, query: str, pages: int = 5) -> Generator[Video, None, None]:
        """
        :param query:
        :param pages: int: one page contains 46 videos
        :return:
        """
        query = query.replace(" ", "+")
        html_content = requests.get(url=f"{root_url}/?q={query}").content.decode("utf-8")
        match = PATTERN_CANT_FIND.search(html_content)
        if "Sorry" in match.group(1).strip():
            raise NoVideosFound

        else:
            for page in range(1, int(pages + 1)):
                html_content = requests.get(url=f"{root_url}/?q={query}&p={page}").content.decode("utf-8")
                if not check_for_page(html_content):
                    break

                else:
                    urls = PATTERN_VIDEOS_ON_SITE.findall(html_content)
                    for url in urls:
                        yield Video(f"{root_url}hdporn/{url}")

    @classmethod
    def get_top_porn(cls, sort_by: Sort, pages: int = 5) -> Generator[Video, None, None]:
        """
        :param pages: int: one page contains 46 videos
        :param sort_by: all_time, month, week
        :return:
        """
        for page in range(1, int(pages + 1)):
            if sort_by == "all_time":
                html_content = requests.get(f"{root_url_top}{page}", headers=headers).content.decode("utf-8")

            else:
                html_content = requests.get(f"{root_url_top}{sort_by}/{page}", headers=headers).content.decode("utf-8")

            if not check_for_page(html_content):
                break

            else:
                urls = PATTERN_VIDEOS_ON_SITE.findall(html_content)
                for url in urls:
                    yield Video(f"{root_url}hdporn/{url}")

    @classmethod
    def get_all_categories(cls) -> list:
        """
        :return: list: Returns all categories of HQporner as a list of strings
        """
        html_content = requests.get("https://hqporner.com/categories", headers=headers).content.decode("utf-8")
        categories = PATTERN_ALL_CATEGORIES.findall(html_content)
        return categories

    @classmethod
    def get_random_video(cls) -> Video:
        """
        :return: Video object (random video from HQPorner)
        """
        html_content = requests.get(root_random, headers=headers).content.decode("utf-8")
        videos = PATTERN_VIDEOS_ON_SITE.findall(html_content)
        video = choice(videos) # The random-porn from HQPorner returns 3 videos, so we pick one of them
        return Video(f"{root_url}hdporn/{video}")

    @classmethod
    def get_brazzers_videos(cls, pages=5) -> Generator[Video, None, None]:
        """
        :param pages: int: one page contains 46 videos
        :return:
        """
        for page in range(1, int(pages + 1)):
            html_content = requests.get(url=f"{root_brazzers}/{page}").content.decode("utf-8")
            if not check_for_page(html_content):
                break

            else:
                urls = PATTERN_VIDEOS_ON_SITE.findall(html_content)
                for url_ in urls:
                    yield Video(f"{root_url}hdporn/{url_}")
