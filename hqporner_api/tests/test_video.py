import pytest
from hqporner_api.api import Video



@pytest.mark.asyncio
async def test_video_all():
    url = "https://hqporner.com/hdporn/99748-exercise_bike_Mila_Azul.html"
    video = await Video.create(url)
    assert isinstance(video.title, str) and len(video.title) > 0
    assert isinstance(video.pornstars, list) and len(video.pornstars) > 0
    assert isinstance(video.length, str) and len(video.length) > 0
    assert isinstance(video.tags, list) and len(video.tags) > 0
    assert isinstance(await video.video_qualities(), list) and len(await video.video_qualities()) > 0
    assert isinstance(await video.direct_download_urls(), list) and len(await video.direct_download_urls()) > 0
    assert isinstance(await video.get_thumbnails(), list) and len(await video.get_thumbnails()) == 11









