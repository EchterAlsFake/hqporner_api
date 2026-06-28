import pytest

query = "Mia Khalifa"

@pytest.mark.asyncio
async def test_basic_search(client):
    videos = client.search_videos(query)

    async for scrape_result in videos:
        assert isinstance(scrape_result.video.title, str) and len(scrape_result.video.title) > 0
