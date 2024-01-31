# HQPorner API Documentation

### Current Version 1.5

Disclaimer:
- Usage of this API is in violation of HQporner's ToS!
- I have no authorization.
- I am not interested in a lawsuit.
- Contact me at my E-Mail if you feel this Repository should be deleted, and I'll do so without discussing

## Table of Contents

- [Installation](#installation)
- [Dependencies](#dependencies)
- [Usage](#usage)
- [Quality](#quality)
- [Client](#client)
- [Video](#basic-video-information)
- [Videos by Actress](#get-videos-by-actress)
- [Videos by Category](#get-videos-by-category)
- [Search for Videos](#search-for-videos)
- [Get Top Porn](#get-top-porn)
- [Get all categories](#get-all-categories)
- [Random video](#get-random-video)
- [Brazzer's Videos](#get-brazzers-videos)
- [Additional Arguments](#additional-arguments)
- [Exceptions](#exceptions)
# Installation
````
Installation using pip:

$ pip install hqporner_api

Or Install directly from GitHub

$ pip install git+https://github.com/EchterAlsFake/hqporner_api
````

# Dependencies

HQPorner API depends on the following libraries:
- [requests](https://github.com/psf/requests)

# Usage

Import HQPorner API like in the example below:

```python
from hqporner_api.api import Client, Quality, Video
from hqporner_api.modules.errors import InvalidCategory, NoVideosFound, InvalidActress
from hqporner_api.modules.locals import *
```

# Quality

The quality class is used for video downloading. It has three attributes:

- Quality.BEST (representing the best quality)
- Quality.HALF (representing something in the middle)
- Quality.WORST (representing the worst quality)

! This can also be a string instead of the object like:

- Quality.BEST == `best`
- Quality.HALF == `half`
- Quality.WORST == `worst`

# Client
### Initialize a Client

```python
client = Client()
```

### Get a video object

```python
from hqporner_api.api import Client
video = Client().get_video(url="<video_url>")
```

### Cached Objects

Most objects are cached. Meaning that every time you access the API without changing the video, the attributes
aren't reloaded. Instead, they are cached. This makes it very efficient. 

The objects are:

- Video().video_title
- Video().cdn_url
- Video().pornstars
- Video().video_length
- Video().publish_date
- Video().categories
- Video().video_qualities
- Video().direct_download_urls

## Basic Video Information:

```python
from hqporner_api.api import Client
video = Client().get_video("<video_url>")

# access video title:
video.video_title # Returns a string

# access the content delivery network url:
video.cdn_url # Returns a string

# access pornstars
video.pornstars # Returns a list

# access video length
video.video_length # Returns a string

# access publish date
video.publish_date # Returns a string

# access categories
video.categories # Returns a list

# access qualities
video.video_qualities # Returns a list

# access direct download urls (for all qualities)
video.direct_download_urls
```

## Download a video


```python
from hqporner_api.api import Client, Quality
client = Client()
video = client.get_video("<video_url>")
quality = Quality.BEST # Best quality as an example

video.download(quality=quality)

# by default all videos are downloaded to the current working directory.
# You can change this by specifying an output path:

video.download(quality=quality, output_path="your_path_here")

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
from hqporner_api.api import Client

actress_object = Client().get_videos_by_actress("<actress-name>") 
# You can also enter an actress URl e.g hqporner.com/actress/...

# You can now iterate through all videos from an actress:

for video in actress_object:
    print(video.video_title)

# This will include ALL videos. Not only from the first page.
```

## Get videos by category

```python
from hqporner_api.api import Client
from hqporner_api.modules.locals import Category
videos = Client().get_videos_by_category(Category) 

for video in videos:
    print(video.video_title)

"""
All attributes of the Category class can be found in locals.py
You can also see all categories at hqporner.com/categories

The Category can also be a string. e.g Category.BIG_TITS would be equivalent to big-tits

"""

```

## Search for videos

```python
from hqporner_api.api import Client
videos = Client().search_videos(query="Search Query")

for video in videos:
    print(video.video_title)
```

## Get top porn

```python
from hqporner_api.api import Client
from hqporner_api.modules.locals import Sort
top_porn = Client().get_top_porn(sort_by=Sort) 

"""
Sort:

1) Sort.WEEK
2) Sort.MONTH
3) Sort.ALL_TIME
"""
```


## Get all categories
```python
from hqporner_api.api import Client
categories = Client().get_all_categories() # Returns a list with all possible categories
```

## Get random video
```python
from hqporner_api.api import Client
random_video = Client().get_random_video() # Returns a random video object
```

## Get brazzers videos
```python
from hqporner_api.api import Client
brazzers_videos = Client().get_brazzers_videos(pages=int) # Returns brazzers videos (generator) (pages: optional)
```

# Additional Arguments:

Some methods have a `pages` argument. This argument defines over how many pages the script iterates on HQPorner.
For example, the Pornstar Anissa Kate has currently over 162 videos. If you scroll down, you can see that
those are packed in 4 pages. If no more pages are left, the generator will simply stop and everything's fine.
One page = 46 videos

# Exceptions

There are 3 exceptions:

- InvalidCategory  (Raised when a category is invalid)
- NoVideosFound    (Raised when no videos were found during a search)
- InvalidActress   (Raised when an invalid actress was given)













