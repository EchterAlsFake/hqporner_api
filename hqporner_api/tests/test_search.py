from ..api import Client

client = Client()
query = "Mia Khalifa"


def test_basic_search():
    videos = client.search_videos(query, pages=3)

    for video in videos:
        assert isinstance(video.title, str) and len(video.title) > 0
