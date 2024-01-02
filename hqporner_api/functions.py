import requests
from consts import *
from errors import *


def check_for_page(html_content):
    match = PATTERN_CANT_FIND.search(html_content)
    if "Sorry" in match.group(1).strip():
        return False

    else:
        return True


def check_url(url):
    if not PATTERN_CHECK_URL.match(url).group(1):
        return False

    else:
        return True


def check_actress(actress):
    content = requests.get(f"{root_url_actress}{actress}").content.decode("utf-8")
    if not check_for_page(content):
        return False

    else:
        return True


def check_category(category):
    content = requests.get(f"{root_url}{category}").content.decode("utf-8")
    if not check_for_page(content):
        return False

    else:
        return True