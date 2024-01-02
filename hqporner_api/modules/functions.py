import requests
from hqporner_api.modules.consts import *
from typing import Callable

def check_for_page(html_content) -> Callable:
    match = PATTERN_CANT_FIND.search(html_content)
    try:
        if "Sorry" in match.group(1).strip():
            return False

        else:
            return True

    except AttributeError:
        return False


def check_url(url) -> Callable:
    try:
        if not PATTERN_CHECK_URL.match(url).group(1):
            return False

        else:
            return True

    except AttributeError:
        return False

def check_actress(actress) -> Callable:

    if str(actress).startswith("https://"):
        actress = re.search("https://hqporner.com/actress/(.*?)")

    content = requests.get(f"{root_url_actress}{actress}").content.decode("utf-8")
    if not check_for_page(content):
        return False

    else:
        return True


def check_category(category) -> Callable:
    content = requests.get(f"{root_url}{category}").content.decode("utf-8")
    if not check_for_page(content):
        return False

    else:
        return True