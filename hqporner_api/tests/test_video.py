import pytest


@pytest.mark.asyncio
async def test_title(video):
    assert isinstance(video.title, str) and len(video.title) > 0


@pytest.mark.asyncio
async def test_pornstars(video):
    assert isinstance(video.pornstars, list) and len(video.pornstars) > 0


@pytest.mark.asyncio
async def test_video_length(video):
    assert isinstance(video.length, str) and len(video.length) > 0


@pytest.mark.asyncio
async def test_categories(video):
    assert isinstance(video.tags, list) and len(video.tags) > 0


@pytest.mark.asyncio
async def test_qualities(video):
    qualities = await video.video_qualities
    assert isinstance(qualities, list) and len(qualities) > 0


@pytest.mark.asyncio
async def test_direct_download_url(video):
    urls = await video.direct_download_urls()
    assert isinstance(urls, list) and len(urls) > 0

