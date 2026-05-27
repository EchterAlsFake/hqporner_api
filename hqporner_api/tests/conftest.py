import pytest
import pytest_asyncio
from ..api import Client, Video

@pytest.fixture(scope="session")
def client():
    """Returns a Client instance for the test session."""
    return Client()

@pytest_asyncio.fixture
async def video(client):
    """Returns a Video instance for a single test."""
    url = "https://hqporner.com/hdporn/99748-exercise_bike_Mila_Azul.html"
    video_instance = client.get_video(url)
    await video_instance.init()
    return video_instance

@pytest_asyncio.fixture
async def video_2(client):
    """Returns another Video instance for a single test."""
    url = "https://hqporner.com/hdporn/121767-breakfast_with_creampie.html"
    video_instance = client.get_video(url)
    await video_instance.init()
    return video_instance

@pytest_asyncio.fixture
async def video_3(client):
    """Returns a third Video instance for a single test."""
    url = "https://hqporner.com/hdporn/121768-are_you_blind_to_the_opportunity.html"
    video_instance = client.get_video(url)
    await video_instance.init()
    return video_instance
