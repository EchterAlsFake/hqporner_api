import pytest

query = "Mia Khalifa"

@pytest.mark.asyncio
async def test_basic_search(client):
    videos = client.search_videos(query)

    async for video in videos:
        assert isinstance(video.title, str) and len(video.title) > 0
