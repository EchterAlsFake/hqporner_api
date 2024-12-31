from hqporner_api.api import Video


url = "https://hqporner.com/hdporn/99748-exercise_bike_Mila_Azul.html"
video = Video(url)


def test_title():
    assert isinstance(video.title, str) and len(video.title) > 0


def test_pornstars():
    assert isinstance(video.pornstars, list) and len(video.pornstars) > 0


def test_video_length():
    assert isinstance(video.length, str) and len(video.length) > 0


def test_categories():
    assert isinstance(video.tags, list) and len(video.tags) > 0


def test_qualities():
    assert isinstance(video.video_qualities, list) and len(video.video_qualities) > 0


def test_direct_download_url():
    assert isinstance(video.direct_download_urls(), list) and len(video.direct_download_urls()) > 0


def test_thumbnails():
    assert isinstance(video.get_thumbnails(), list) and len(video.get_thumbnails()) == 11









