import pytest

@pytest.mark.asyncio
async def test_download_high(video):
    assert await video.download(quality="best") is True

@pytest.mark.asyncio
async def test_download_half(video_2):
    assert await video_2.download(quality="half") is True

@pytest.mark.asyncio
async def test_download_low(video_3):
    assert await video_3.download(quality="worst") is True
