import pytest
from ..api import Client


@pytest.mark.asyncio
async def test_basic_search():
    client = Client()
    query = "Mia Khalifa"

    videos = await client.search_videos(query)

    for video in videos:
        assert isinstance(video.title, str) and len(video.title) > 0
