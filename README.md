<h1 align="center">HQPorner API</h1> 

<div align="center">
    <a href="https://pepy.tech/project/hqporner_api"><img src="https://static.pepy.tech/badge/hqporner_api" alt="Downloads"></a>
    <a href="https://github.com/EchterAlsFake/hqporner_api/workflows/"><img src="https://github.com/EchterAlsFake/hqporner_api/workflows/CodeQL/badge.svg" alt="CodeQL Analysis"/></a>
    <a href="https://github.com/EchterAlsFake/hqporner_api/workflows/"><img src="https://github.com/EchterAlsFake/hqporner_api/actions/workflows/tests.yml/badge.svg" alt="API Tests"/></a>
</div>

# Description

HQPorner API is an API for HQPorner. It allows you to fetch information from videos using regexes and requests.

# Disclaimer

> [!IMPORTANT] 
> HQPorner API is in violation to HQporner's ToS!
> If you are the website owner of hqporner.com, contact me at my E-Mail, and I'll take this repository immediately offline.
> EchterAlsFake@proton.me

# Quickstart

### Have a look at the [Documentation](https://github.com/EchterAlsFake/hqporner_api/blob/master/README/Documentation.md) for more details

- Install the library with `pip install hqporner_api`


```python
from hqporner_api import Client, Quality
# Initialize a Client object
client = Client()

# Fetch a video
video_object = client.get_video("<insert_url_here>")

# Download the video
video_object.download(quality=Quality.BEST, path="your_output_path + title.mp4")

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

# Contribution
Do you see any issues or having some feature requests? Simply open an Issue or talk
in the discussions.

Pull requests are welcome :) 

# License
Licensed under the LGPLv3 License

Copyright (C) 2023–2024 Johannes Habel


