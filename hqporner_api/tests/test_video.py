import pytest
from ..api import Client, DownloadConfigRAW


@pytest.fixture
def client() -> Client:
    return Client()

@pytest.mark.asyncio
async def test_video(client):
    video = await client.get_video("https://hqporner.com/hdporn/126829-this_is_our_story.html")
    assert isinstance(video.title, str)
    assert isinstance(await video.video_qualities, list)
    assert isinstance(video.tags, list)
    assert isinstance(video.length, str)
    assert isinstance(video.pornstars, list)
    assert isinstance(video.cdn_url, str)
    assert isinstance(video.publish_date, str)

    config_low = DownloadConfigRAW(quality="best")
    assert await video.download(config_low) is True
