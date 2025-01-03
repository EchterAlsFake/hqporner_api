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
