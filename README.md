<h1 align="center">HQPorner API</h1> 

<div align="center">
    <a href="https://pepy.tech/project/hqporner_api"><img src="https://static.pepy.tech/badge/hqporner_api" alt="Downloads"></a>
    <a href="https://github.com/EchterAlsFake/hqporner_api/workflows/"><img src="https://github.com/EchterAlsFake/hqporner_api/workflows/CodeQL/badge.svg" alt="CodeQL Analysis"/></a>
    <a href="https://github.com/EchterAlsFake/hqporner_api/workflows/"><img src="https://github.com/EchterAlsFake/hqporner_api/actions/workflows/tests.yml/badge.svg" alt="API Tests"/></a>
</div>

# Description

HQPorner API is an API for HQPorner. It allows you to fetch information from videos using regexes and requests.
It is optimized for performance and as lightweight as possible.

# Disclaimer

[!IMPORTANT] HQPorner API is in violation to HQporner's ToS!

Copyright Information: I have no intention of stealing copyright protected content or slowing down
a website. Contact me at my E-Mail, and I'll take this Repository immediately offline.


# Quickstart

### Have a look at the [Documentation](https://github.com/EchterAlsFake/hqporner_api/blob/master/README/DOCUMENTATION.md) for more details

- Install the library with `pip install hqporner_api`


```python
from hqporner_api.api import Client, Quality
# Initialize a Client object
client = Client()

# Fetch a video
video_object = client.get_video("<insert_url_here>")

# Download the video

video_object.download(quality=Quality.BEST, output_path="your_output_path")

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

# Changelog
See [Changelog](https://github.com/EchterAlsFake/hqporner_api/blob/master/README/CHANGELOG.md) for more details.

# Contribution
Do you see any issues or having some feature requests? Simply open an Issue or talk
in the discussions.

Pull requests are also welcome, but please avoid bs4 and use regex :) 

# License
Licensed under the LGPLv3 License

Copyright (C) 2023–2024 Johannes Habel

# Support

Leave a star on the repository. That's enough :) 


