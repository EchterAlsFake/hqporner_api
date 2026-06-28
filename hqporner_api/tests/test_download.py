import pytest
from hqporner_api import DownloadConfigRAW

config_1 = DownloadConfigRAW(quality="best")
config_2 = DownloadConfigRAW(quality="half")
config_3 = DownloadConfigRAW(quality="worst")


@pytest.mark.asyncio
async def test_download_high(video):
    assert await video.download(config_1) is True


@pytest.mark.asyncio
async def test_download_half(video_2):
    assert await video_2.download(config_2) is True


@pytest.mark.asyncio
async def test_download_low(video_3):
    assert await video_3.download(config_3) is True
