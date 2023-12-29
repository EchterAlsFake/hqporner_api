# HQPorner API Documentation

### Current Version 0.9


# Installation
````
Installation using pip:

$ pip install hqporner_api

Or Install directly from GitHub

$ pip install git+https://github.com/EchterAlsFake/hqporner_api
````

# Dependencies

HQPorner API depends on the following libraries:

- [tqdm](https://github.com/tqdm/tqdm)
- [requests](https://github.com/psf/requests)

# Usage

Import HQPorner API like in the example below:

```python
from hqporner_api.api import API, Quality
```

# Quality

The quality class is used for video downloading. It has three methods:

- Quality.BEST (representing the best quality)
- Quality.HALF (representing something in the middle)
- Quality.WORST (worst quality)

# API

### Fetch Information:

```python
api = API("hqporner url ending in .html")
```

### Cached Objects

Most objects are cached. Meaning, that everytime you access the API without changing the video, the attributes
aren't reloaded. Instead, they are cached. This makes it very efficient. 

The objects are:

- API().video_title
- API().cdn_url
- API().pornstars
- API().video_length
- API().publish_date
- API().categories
- API().video_qualities
- API().direct_download_urls

## Basic Video Information:

```python
from hqporner_api.api import API
api = API("YOUR_URL_HERE")

# access video title:
api.video_title # Returns a string

# access the content delivery network url:
api.cdn_url # Returns a string

# access pornstars
api.pornstars # Returns a list

# access video length
api.video_length # Returns a string

# access publish date
api.publish_date # Returns a string

# access categories
api.categories # Returns a list

# access qualities
api.video_qualities # Returns a list

# access direct download urls (for all qualities)
api.direct_download_urls
```

## Download a video


```python
from hqporner_api.api import API, Quality
api = API("YOUR_VIDEO_URL")
quality = Quality.BEST # Best quality as an example

api.download(quality=quality)

# by default all videos are downloaded to the current working directory.
# You can change this by specifying an output path:

api.download(quality=quality, output_path="your_path_here")

# Custom Callback

# You can define your own callback instead if tqdm. You must make a function that takes pos and total as arguments.
# This will disable tqdm
def custom_callback(self, downloaded, total):
    """This is an example of how you can implement the custom callback"""

    percentage = (downloaded / total) * 100
    print(f"Downloaded: {downloaded} bytes / {total} bytes ({percentage:.2f}%)")

```

## Get videos by actress

```python
from hqporner_api.api import API
actress_object = API("YOUR_URL_HERE").get_videos_by_actress("<actress_name>") # This will be improved later, but for now you need to still give a video url.

# IMPORTANT! 
# The actress name must be the name appearing in the URL. Example: https://hqporner.com/actress/anissa-kate
# The actress name would be anissa-kate NOT Anissa Kate

# You can now iterate through all videos from an actress:

for video in actress_object:
    print(video.video_title)

# This will include ALL videos. Not only from the first page.
```














