import requests
from hqporner_api.modules.consts import *


def check_for_page(html_content) -> bool:
    match = PATTERN_CANT_FIND.search(html_content)
    try:
        if "Sorry" in match.group(1).strip():
            return False

        else:
            return True

    except AttributeError:
        return False


def check_url(url) -> bool:
    try:
        if not PATTERN_CHECK_URL.match(url).group(1):
            return False

        else:
            return True

    except AttributeError:
        return False


def check_actress(actress) -> bool:

    match = re.search("hqporner.com/actress/(.+)", actress)
    if match:
        return True

    else:
        content = requests.get(f"{root_url_actress}{actress}").content.decode("utf-8")
        if not check_for_page(content):
            return False

        else:
            return True


def check_category(category) -> bool:
    content = requests.get(f"{root_url_category}{category}").content.decode("utf-8")
    if not check_for_page(content):
        return False

    else:
        return True
