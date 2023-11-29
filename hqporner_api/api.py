import re
import os
import requests
import string

try:
    from exceptions import *

except ModuleNotFoundError:
    from .exceptions import *

from bs4 import BeautifulSoup
from tqdm import tqdm

headers = {
    "Referer": "https://hqporner.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
}  # Use this to prevent detection mechanisms...


class API:

    def check_path(self, path):
        return True if os.path.exists(path) else False

    def extract_actress(self, url):
        """

        :param url:
        :return: list
        """

        html_content = requests.get(url, headers=headers).content
        soup = BeautifulSoup(html_content, 'lxml')
        actresses = []
        try:
            li_tag = soup.find('li', class_='icon fa-star-o')
            a_tag = li_tag.find_all('a', class_='click-trigger')
            for tag in a_tag:
                actresses.append(tag.text)

        except AttributeError:
            raise NoActressFound()

        else:
             return actresses

    def extract_title(self, url):
        html = requests.get(url, headers=headers).content
        beautifulsoup = BeautifulSoup(html, "lxml")
        return beautifulsoup.find("title").text

    def extract_text_after_double_slash(self, url):
        html = requests.get(url, headers=headers).content
        beautifulsoup = BeautifulSoup(html, "lxml")
        url_pattern = re.compile(r"url: '/blocks/altplayer\.php\?i=//(.*?)',")
        match = url_pattern.search(str(beautifulsoup))

        if match:
            url_path = match.group(1)
            return url_path

    def get_final_urls(self, url):
        base_url = self.extract_text_after_double_slash(url)
        final_content = requests.get("https://" + base_url).content
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

    def get_direct_url(self, url, quality):
        """
        :param url:
        :param quality
            1) 360: returns 360p video url
            2) 720: returns 720p video url
            3) 1080: returns 1080p video url
            4) 2160: returns 2160p video url
            5) highest: returns highest quality possible
        :return: string
        """

        urls = self.get_final_urls(url)

        try:
            if quality == "highest":
                return f"https:{urls[-1]}"

            elif "360.mp4" in urls[0] and quality == "360":
                return f"https:{urls[0]}"

            elif "720.mp4" in urls[1] and quality == "720":
                return f"https:{urls[1]}"

            elif "1080.mp4" in urls[2] and quality == "1080":
                return f"https:{urls[2]}"

            elif "2160.mp4" in urls[3] and quality == "2160":
                return f"https:{urls[3]}"

            else:
                raise QualityNotSupported()

        except IndexError:
            raise QualityNotSupported()


    def strip_title(self, title):
        illegal_chars = '<>:"/\\|?*'
        cleaned_title = ''.join([char for char in title if char in string.printable and char not in illegal_chars])

        return cleaned_title

    def download(self, url, output_path, quality, callback=None, no_title=False):
        url_download = self.get_direct_url(url, quality)
        title = self.extract_title(url)
        title = self.strip_title(title)
        if no_title:
            final_path = output_path

        else:
            final_path = os.path.join(output_path, f"{title}.mp4")

        response = requests.get(url_download, stream=True)
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
                        callback(downloaded_so_far, file_size, "hqporner")

                    else:
                        progress_bar.update(len(chunk))

            if not callback:
                progress_bar.close()

    def custom_callback(self, downloaded, total):
        """This is an example of how you can implement the custom callback"""

        percentage = (downloaded / total) * 100
        print(f"Downloaded: {downloaded} bytes / {total} bytes ({percentage:.2f}%)")

    def get_categories(self, url):
        html_content = requests.get(url).content
        soup = BeautifulSoup(html_content, "lxml")

        categories = []

        section = soup.find_all('div', class_='box page-content')
        for sec in section:
            x = sec.find_all_next("a", class_="tag-link click-trigger")
            for z in x:
                f = z.find_next_sibling("a")
                try:
                    if not f.text in categories:
                        categories.append(f.text)

                except AttributeError:
                    pass

        if len(categories) == 0:
            raise "Error: No categories were found."

        else:
            return categories

    def get_videos_by_actress(self, name: str):
        root_url = "https://hqporner.com/actress/"
        final_url = f"{root_url}{name}"

        html_content = requests.get(final_url, headers=headers).content
        soup = BeautifulSoup(html_content, "lxml")  # Still in development
        row = soup.find_all("h3", class_="meta-data-title")
        for item in row:
            x = item.find("a")
            print(x)

    def download_from_file(self, file, output, quality, callback=None):
        with open(file, "r") as url_file:
            content = url_file.read().splitlines()
            for url in content:
                self.download(output_path=output, quality=quality, url=url, callback=callback)

    def get_video_length(self, url):
        html_content = requests.get(url).content
        soup = BeautifulSoup(html_content, "lxml")
        li_tag = soup.find("li", class_="icon fa-clock-o")
        return li_tag.text

    def get_publish_date(self, url):
        html_content = requests.get(url).content
        soup = BeautifulSoup(html_content, "lxml")
        li_tag = soup.find("li", class_="icon fa-calendar")
        return li_tag.text

    def get_total_size(self, url, quality):
        url_download = self.get_direct_url(url, quality)
        response = requests.get(url_download, stream=True)
        file_size = int(response.headers.get('content-length', 0))
        return file_size
