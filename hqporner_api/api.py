import os

from functools import cached_property
from random import choice
from typing import Generator
from bs4 import BeautifulSoup
from hqporner_api.modules.locals import *
from hqporner_api.modules.errors import *
from hqporner_api.modules.functions import *
from hqporner_api.modules.progress_bars import *
from base_api.base import Core
from base_api.modules.quality import Quality


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
        self.html_content = Core().get_content(url=url, headers=headers).decode("utf-8")

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
    def categories(self) -> list:
        """
        :return: (list) A list of categories featured in this video
        """
        categories = PATTERN_CATEGORY.findall(self.html_content)
        if len(categories) > 0:
            return categories

        else:
            raise WeirdError

    @cached_property
    def video_qualities(self) -> list:
        """
        :return: (list) The available qualities of the video
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
        :return: (list) The direct download urls for all available qualities
        """
        cdn_url = f"https://{self.cdn_url}"
        html_content = Core().get_content(url=cdn_url, headers=headers).decode("utf-8")
        urls = PATTERN_EXTRACT_CDN_URLS.findall(html_content)
        return urls

    def download(self, quality, path="./", callback=None):
        """
        :param quality:
        :param path:
        :param callback:
        :return: (bool)
        """
        quality = Core().fix_quality(quality)

        cdn_urls = self.direct_download_urls
        quals = self.video_qualities
        quality_url_map = {qual: url for qual, url in zip(quals, cdn_urls)}

        # Define the quality map
        if not quals:
            raise NotAvailable

        quality_map = {
            Quality.BEST: max(quals, key=lambda x: int(x)),
            Quality.HALF: sorted(quals, key=lambda x: int(x))[len(quals) // 2],
            Quality.WORST: min(quals, key=lambda x: int(x))
        }

        selected_quality = quality_map[quality]
        download_url = f"https://{quality_url_map[selected_quality]}"
        response = requests.get(download_url, stream=True)
        file_size = int(response.headers.get('content-length', 0))

        if callback is None:
            progress_bar = Callback()

        downloaded_so_far = 0

        if not os.path.exists(path):
            with open(path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
                    downloaded_so_far += len(chunk)

                    if callback:
                        callback(downloaded_so_far, file_size)

                    else:
                        progress_bar.text_progress_bar(downloaded=downloaded_so_far, total=file_size)

            if not callback:
                del progress_bar

            return True

        else:
            raise FileExistsError("The video already exists.")

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
        html_content = Core().get_content(url=f"{root_url}/?q={query}").decode("utf-8")
        soup = BeautifulSoup(html_content, 'lxml')
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
    def get_video(cls, url: str) -> Video:
        """
        :param url: The video URL
        :return: Video object
        """
        return Video(url)

    @classmethod
    def get_videos_by_actress(cls, name: str, pages: int = 5) -> Generator[Video, None, None]:
        """
        :param name: The actress name or the URL
        :param pages: int: one page contains 46 videos
        :return: Video object
        """
        name = Checks().check_actress(name)
        for page in range(1, int(pages + 1)):
            final_url = f"{root_url_actress}{name}/{page}"
            html_content = Core().get_content(final_url, headers=headers).decode("utf-8")
            if not check_for_page(html_content):
                break

            urls_ = PATTERN_VIDEOS_ON_SITE.findall(html_content)
            for url_ in urls_:
                url = f"{root_url}hdporn/{url_}"
                if PATTERN_CHECK_URL.match(url):
                    yield Video(url)

    @classmethod
    def get_videos_by_category(cls, category: Category, pages=5) -> Generator[Video, None, None]:
        """
        :param category: Category: The video category
        :param pages: int: one page contains 46 videos
        :return: Video object
        """
        for page in range(1, int(pages + 1)):
            html_content = Core().get_content(url=f"{root_url_category}{category}/{page}", headers=headers).decode("utf-8")
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
        :return: Video object
        """
        query = query.replace(" ", "+")
        html_content = Core().get_content(url=f"{root_url}?q={query}", headers=headers).decode("utf-8")
        match = PATTERN_CANT_FIND.search(html_content)
        if "Sorry" in match.group(1).strip():
            raise NoVideosFound

        else:
            for page in range(1, int(pages + 1)):
                html_content = Core().get_content(url=f"{root_url}?q={query}&p={page}", headers=headers).decode("utf-8")
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
        :return: Video object
        """
        for page in range(1, int(pages + 1)):
            if sort_by == "all_time":
                html_content = Core().get_content(f"{root_url_top}{page}", headers=headers).decode("utf-8")

            else:
                html_content = Core().get_content(f"{root_url_top}{sort_by}/{page}", headers=headers).decode("utf-8")

            if not check_for_page(html_content):
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
        html_content = Core().get_content("https://hqporner.com/categories", headers=headers).decode("utf-8")
        categories = PATTERN_ALL_CATEGORIES.findall(html_content)
        return categories

    @classmethod
    def get_random_video(cls) -> Video:
        """
        :return: Video object (random video from HQPorner)
        """
        html_content = Core().get_content(root_random, headers=headers).decode("utf-8")
        videos = PATTERN_VIDEOS_ON_SITE.findall(html_content)
        video = choice(videos) # The random-porn from HQPorner returns 3 videos, so we pick one of them
        return Video(f"{root_url}hdporn/{video}")

    @classmethod
    def get_brazzers_videos(cls, pages=5) -> Generator[Video, None, None]:
        """
        :param pages: int: one page contains 46 videos
        :return: Video object
        """
        for page in range(1, int(pages + 1)):
            html_content = Core().get_content(url=f"{root_brazzers}/{page}", headers=headers).decode("utf-8")
            if not check_for_page(html_content):
                break

            else:
                urls = PATTERN_VIDEOS_ON_SITE.findall(html_content)
                for url_ in urls:
                    yield Video(f"{root_url}hdporn/{url_}")
