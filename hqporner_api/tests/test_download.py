import pytest
from ..api import Client

@pytest.mark.asyncio
async def test_downloads():
    client = Client()

    url = "https://hqporner.com/hdporn/99748-exercise_bike_Mila_Azul.html"
    url_2 = "https://hqporner.com/hdporn/118926-very_easy_on_the_eyes.html"
    url_3 = "https://hqporner.com/hdporn/116797-loss_by_loss_makes_a_big_win.html"

    video = await client.get_video(url)
    video_2 = await client.get_video(url_2)
    video_3 = await client.get_video(url_3)

    assert await video.download(quality="best") is True

    assert await video_2.download(quality="half") is True

    assert await video_3.download(quality="worst") is True