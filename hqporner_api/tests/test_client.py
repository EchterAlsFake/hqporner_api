import pytest
from hqporner_api.api import Client, Sort

client = Client()

@pytest.mark.asyncio
async def test_all():

    top_porn_all = await client.get_top_porn(sort_by=Sort.ALL_TIME)

    for idx, video in enumerate(top_porn_all):
        assert isinstance(video.title, str) and len(video.title) > 0
        if idx == 3:
            break

    top_porn_week = await client.get_top_porn(sort_by=Sort.WEEK)

    for idx, video in enumerate(top_porn_week):
        assert isinstance(video.title, str) and len(video.title) > 0
        if idx == 3:
            break


    top_porn_month = await client.get_top_porn(sort_by=Sort.MONTH)

    for idx, video in enumerate(top_porn_month):
        assert isinstance(video.title, str) and len(video.title) > 0
        if idx == 3:
            break


    all_categories = await client.get_all_categories()
    assert isinstance(all_categories, list) and len(all_categories) > 20


    random_video = await client.get_random_video()
    assert isinstance(random_video.title, str) and len(random_video.title) > 0

    name = "anissa-kate"

    actress = await client.get_videos_by_actress(name)
    for idx, video in enumerate(actress):
        assert isinstance(video.title, str) and len(video.title) > 0
        if idx == 3:
            break

    videos = await client.get_brazzers_videos()
    for idx, video in enumerate(videos):
        assert isinstance(video.title, str) and len(video.title) > 0
        if idx == 3:
            break
