from hqporner_api.api import Client, Sort


client = Client()


def test_get_top_porn_all_time():
    top_porn_all = client.get_top_porn(sort_by=Sort.ALL_TIME)

    for idx, video in enumerate(top_porn_all):
        assert isinstance(video.title, str) and len(video.title) > 0
        if idx == 3:
            break

def test_get_top_porn_week():
    top_porn_week = client.get_top_porn(sort_by=Sort.WEEK)

    for idx, video in enumerate(top_porn_week):
        assert isinstance(video.title, str) and len(video.title) > 0
        if idx == 3:
            break


def test_get_top_porn_month():
    top_porn_month = client.get_top_porn(sort_by=Sort.MONTH)

    for idx, video in enumerate(top_porn_month):
        assert isinstance(video.title, str) and len(video.title) > 0
        if idx == 3:
            break


def test_get_all_categories():
    all_categories = client.get_all_categories()
    assert isinstance(all_categories, list) and len(all_categories) > 20


def test_random_video():
    random_video = client.get_random_video()
    assert isinstance(random_video.title, str) and len(random_video.title) > 0


def test_get_videos_by_category():
    #  This will test ALL categories

    categories = client.get_all_categories()
    for idx, category in enumerate(categories):
        videos = client.get_videos_by_category(category=category)
        for idx, video in enumerate(videos):
            assert isinstance(video.title, str) and len(video.title) > 0
            if idx == 1:
                break


def test_get_videos_by_actress():
    name = "anissa-kate"

    actress = client.get_videos_by_actress(name)
    for idx, video in enumerate(actress):
        assert isinstance(video.title, str) and len(video.title) > 0
        if idx == 3:
            break


def test_get_brazzers_videos():
    videos = client.get_brazzers_videos()
    for idx, video in enumerate(videos):
        assert isinstance(video.title, str) and len(video.title) > 0
        if idx == 3:
            break
