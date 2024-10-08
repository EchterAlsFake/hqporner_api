# HQPorner API Documentation

> - Version 1.6
> - Author: Johannes Habel
> - Copyright (C) 2024
> - License: LGPLv3
> - Dependencies: requests, beautifulsoup (bs4), eaf_base_api

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Quality](#quality)
- [Client](#client)
  - [Video](#video-attributes)
  - [Videos by Actress](#get-videos-by-actress)
  - [Videos by Category](#get-videos-by-category)
  - [Search for Videos](#search-for-videos)
  - [Get Top Porn](#get-top-porn)
  - [Get all categories](#get-all-categories)
  - [Random video](#get-random-video)
  - [Brazzer's Videos](#get-brazzers-videos)
- [Locals](#locals)
- [Additional Arguments](#additional-arguments)
- [Exceptions](#exceptions)
- [Quality](#quality)

# Installation

Installation using pip:

$ `pip install hqporner_api`

Or Install directly from GitHub

`pip install git+https://github.com/EchterAlsFake/hqporner_api`

# Important Notice
The ToS of hqporner.com clearly say that using scrapers / bots isn't allowed.
> Using this API is at your risk. I am not liable for your actions!


# Usage

Import HQPorner API like in the example below:

```python
from hqporner_api import Client, Quality, Video
from hqporner_api import locals, errors
```

# Client
### Initialize a Client

```python
from hqporner_api.api import Client
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

## Video Attributes

| Attribute             | Returns | is cached? |
|:----------------------|:-------:|:----------:|
| .title                |   str   |    Yes     |
| .pornstars            |  list   |    Yes     |
| .length               |   str   |    Yes     |
| .publish_date         |   str   |    Yes     |
| .categories           |  list   |    Yes     |
| .video_qualities      |  list   |    Yes     |
| .direct_download_urls |  list   |    Yes     |
| .get_thumbnails       |  list   |     No     |

### Thumbnails

The .get_thumbnails() function from the video objects will return a list.
<br>The list contains 11 items. The first one is the thumbnail, and the 10 others
<br>are the thumbnails you see when you hover of the video.

## Download a video


```python
from hqporner_api import Client, Quality
client = Client()
video = client.get_video("<video_url>")
quality = Quality.BEST # Best quality as an example

video.download(quality=quality)

# by default all videos are downloaded to the current working directory.
# You can change this by specifying an output path:

video.download(quality=quality, path="your_path_here + video_tite.mp4")
# NOTE: The video title isn't automatically assigned to the output path!
# Custom Callback

# You can define your own callback instead if tqdm. You must make a function that takes pos and total as arguments.
# This will disable tqdm
def custom_callback(downloaded, total):
    """This is an example of how you can implement the custom callback"""

    percentage = (downloaded / total) * 100
    print(f"Downloaded: {downloaded} bytes / {total} bytes ({percentage:.2f}%)")

```

## Get videos by actress

```python
from hqporner_api import Client

actress_object = Client().get_videos_by_actress("<actress-name>") # or URL
# You can also enter an actress URl e.g hqporner.com/actress/...

# You can now iterate through all videos from an actress:

for video in actress_object:
    print(video.title)

# This will include ALL videos. Not only from the first page.
```

## Get videos by category

```python
from hqporner_api import Client
from hqporner_api import Category
videos = Client().get_videos_by_category(Category.POV) # example category 

for video in videos:
    print(video.title)

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
    print(video.title)
```

## Get top porn

```python
from hqporner_api import Client
from hqporner_api import Sort
top_porn = Client().get_top_porn(sort_by=Sort.WEEK) # example sorting 

"""
Sort:

1) Sort.WEEK
2) Sort.MONTH
3) Sort.ALL_TIME
"""
```


## Get all categories
```python
from hqporner_api import Client
categories = Client().get_all_categories() # Returns a list with all possible categories
```

## Get random video
```python
from hqporner_api import Client
random_video = Client().get_random_video() # Returns a random video object
```

## Get brazzers videos
```python
from hqporner_api.api import Client
brazzers_videos = Client().get_brazzers_videos() # Returns brazzers videos (generator) (pages: optional)
```

# Locals

## Exceptions

There are three exceptions:

- InvalidCategory  (Raised when a category is invalid)
- NoVideosFound    (Raised when no videos were found during a search)
- InvalidActress   (Raised when an invalid actress was given)

## Quality

The quality class is used for video downloading. It has three attributes:

- Quality.BEST (representing the best quality)
- Quality.HALF (representing something in the middle)
- Quality.WORST (representing the worst quality)

! This can also be a string instead of the object like:

- Quality.BEST == `best`
- Quality.HALF == `half`
- Quality.WORST == `worst`











