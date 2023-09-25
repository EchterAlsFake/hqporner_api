import re
import os
import requests

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
        :return: string
        """

        html_content = requests.get(url, headers=headers).content
        soup = BeautifulSoup(html_content, 'lxml')
        li_tag = soup.find('li', class_='icon fa-star-o')
        a_tag = li_tag.find('a', class_='click-trigger')

        return a_tag.get_text()


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
        :return: string
        """

        urls = self.get_final_urls(url)

        if "360.mp4" in urls[0] and quality == "360":
            return f"http:{urls[0]}"

        elif "720.mp4" in urls[1] and quality == "720":
            return f"http:{urls[1]}"

        elif "1080.mp4" in urls[2] and quality == "1080":
            return f"http:{urls[2]}"

        elif "2160.mp4" in urls[3] and quality == "2160":
            return f"http:{urls[3]}"

        else:
            raise f"Sorry, but the video doesn't support {quality}"


    def download(self, url, output_path, quality):
        url_download = self.get_direct_url(url, quality)
        title = self.extract_title(url)

        final_path = output_path + title + ".mp4"
        response = requests.get(url_download, stream=True)
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
