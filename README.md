<h1 align="center">HQPorner API</h1> 

<div align="center">
    <a href="https://pepy.tech/project/hqporner_api"><img src="https://static.pepy.tech/badge/hqporner_api" alt="Downloads"></a>
    <a href="https://pepy.tech/project/hqporner_api-async"><img src="https://static.pepy.tech/badge/hqporner_api-async" alt="Downloads"></a> <span style="font-size: 20px;">(Async)</span>
    <a href="https://github.com/EchterAlsFake/hqporner_api/workflows/"><img src="https://github.com/EchterAlsFake/hqporner_api/workflows/CodeQL/badge.svg" alt="CodeQL Analysis"/></a>
    <a href="https://github.com/EchterAlsFake/hqporner_api/actions/workflows/sync-tests.yml"><img src="https://github.com/EchterAlsFake/hqporner_api/actions/workflows/sync-tests.yml/badge.svg" alt="API Tests"/></a>
    <a href="https://github.com/EchterAlsFake/hqporner_api/actions/workflows/async-tests.yml"><img src="https://github.com/EchterAlsFake/hqporner_api/actions/workflows/async-tests.yml/badge.svg?branch=async" alt="API Tests"/></a>
</div>


# Description

HQPorner API is an API for HQPorner. It allows you to fetch information from videos using regexes and requests.

# Disclaimer

> [!IMPORTANT] 
> HQPorner API is in violation to HQporner's ToS!
> If you are the website owner of hqporner.com, contact me at my E-Mail, and I'll take this repository immediately offline.
> EchterAlsFake@proton.me

# Quickstart

### Have a look at the [Documentation](https://github.com/EchterAlsFake/API_Docs/blob/master/Porn_APIs/HQPorner.md) for more details

- Install the library with `pip install hqporner_api`


```python
from hqporner_api import Client
# Initialize a Client object
client = Client()

# Fetch a video
video_object = client.get_video("<insert_url_here>")

# Download the video
video_object.download(quality="best", path="your_output_path + title.mp4")

# Videos by actress
actress_generator = client.get_videos_by_actress("anissa-kate")
for video in actress_generator:
    print(video.title) # etc...

# Search for videos
videos = client.search_videos(query="Your query here")
for video in videos:
    print(video.title)

# SEE DOCUMENTATION FOR MORE
```

> [!NOTE]
> HQPorner API can also be used from the command line. Do: hqporner_api -h to see the options

# Changelog
See [Changelog](https://github.com/EchterAlsFake/hqporner_api/blob/master/README/Changelog.md) for more details.

# Support (Donations)
I am developing all my projects entirely for free. I do that, because I have fun and I don't want
to charge 30€ like other people do.

However, if you find my work useful, please consider donating something. A tiny amount such as 1€
means a lot to me.

Paypal: https://paypal.me/EchterAlsFake
<br>XMR (Monero): `46xL2reuanxZgFxXBBaoagiEJK9c7bL7aiwKNR15neyX2wUsX2QVzkeRMVG2Cro44qLUNYvsP1BQa12KPbNat2ML41nyEeq`


# Contribution
Do you see any issues or having some feature requests? Simply open an Issue or talk
in the discussions.

Pull requests are welcome :) 

# License
Licensed under the LGPLv3 License
<br>Copyright (C) 2023–2025 Johannes Habel