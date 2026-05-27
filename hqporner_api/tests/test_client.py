import pytest
from hqporner_api.api import Sort


@pytest.mark.asyncio
async def test_get_top_porn_all_time(client):
    top_porn_all = client.get_top_porn(sort_by=Sort.ALL_TIME)

    idx = 0
    async for video in top_porn_all:
        assert isinstance(video.title, str) and len(video.title) > 0
        if idx == 3:
            break
        idx += 1

@pytest.mark.asyncio
async def test_get_top_porn_week(client):
    top_porn_week = client.get_top_porn(sort_by=Sort.WEEK)

    idx = 0
    async for video in top_porn_week:
        assert isinstance(video.title, str) and len(video.title) > 0
        if idx == 3:
            break
        idx += 1


@pytest.mark.asyncio
async def test_get_top_porn_month(client):
    top_porn_month = client.get_top_porn(sort_by=Sort.MONTH)

    idx = 0
    async for video in top_porn_month:
        assert isinstance(video.title, str) and len(video.title) > 0
        if idx == 3:
            break
        idx += 1


@pytest.mark.asyncio
async def test_get_all_categories(client):
    all_categories = await client.get_all_categories()
    assert isinstance(all_categories, list) and len(all_categories) > 20


@pytest.mark.asyncio
async def test_random_video(client):
    random_video = await client.get_random_video()
    await random_video.init()
    assert isinstance(random_video.title, str) and len(random_video.title) > 0


@pytest.mark.asyncio
async def test_get_videos_by_category(client):
    #  This will test ALL categories

    categories = await client.get_all_categories()
    for idx, category in enumerate(categories):
        videos = client.get_videos_by_category(category=category)
        inner_idx = 0
        async for video in videos:
            assert isinstance(video.title, str) and len(video.title) > 0
            if inner_idx == 1:
                break
            inner_idx += 1


@pytest.mark.asyncio
async def test_get_videos_by_actress(client):
    name = "anissa-kate"

    actress = client.get_videos_by_actress(name)
    idx = 0
    async for video in actress:
        assert isinstance(video.title, str) and len(video.title) > 0
        if idx == 3:
            break
        idx += 1


@pytest.mark.asyncio
async def test_get_brazzers_videos(client):
    videos = client.get_brazzers_videos()
    idx = 0
    async for video in videos:
        assert isinstance(video.title, str) and len(video.title) > 0
        if idx == 3:
            break
        idx += 1
