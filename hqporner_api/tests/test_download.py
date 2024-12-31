from ..api import Client

client = Client()

url = "https://hqporner.com/hdporn/99748-exercise_bike_Mila_Azul.html"

video = client.get_video(url)

def test_download_high():
    assert video.download(quality="best") is True

def test_download_half():
    assert video.download(quality="half") is True

def test_download_low():
    assert video.download(quality="worst") is True