from ..api import Client

client = Client()

url = "https://hqporner.com/hdporn/99748-exercise_bike_Mila_Azul.html"
url_2 = "https://hqporner.com/hdporn/118926-very_easy_on_the_eyes.html"
url_3 = "https://hqporner.com/hdporn/116797-loss_by_loss_makes_a_big_win.html"

video = client.get_video(url)
video_2 = client.get_video(url_2)
video_3 = client.get_video(url_3)


def test_download_high():
    assert video.download(quality="best") is True

def test_download_half():
    assert video_2.download(quality="half") is True

def test_download_low():
    assert video_3.download(quality="worst") is True