# HQPorner API

### Table of contents

- [Description](#description)
- [Installation](#installation)
- [Usage](#usage)
  - [Get started](#import-the-package)
  - [Arguments](#arguments)
  - [Get the title](#get-the-title-of-the-video)
  - [Get actress](#get-the-actress-of-the-video)
  - [Get length](#get-the-length-of-the-video)
  - [Get Publish date](#get-the-publish-date-of-the-video)
  - [Get direct download urls](#get-direct-download-urls)
  - [Download a video](#download-the-video)
- [Custom Callback for custom Progressbar](#callback)
- [License](#license)


# Description

HQPorner API is an API written for the Porn site hqporner.com
<br>It can retrieve data by extracting them from the HTML code
<br> with Beautifulsoup and requests.

Please note that web scarping isn't allowed in most cases!
<br>Consider using a VPN when using this API

# Installation

```py
# Installing via PyPi

pip install --upgrade hqporner_api

# Installing from GitHub to get latest version

pip install git+https://github.com/EchterAlsFake/hqporner_api.git
```

# Usage

### Import the package:

```py
from hqporner_api.api import API
```

### Arguments
- URL: Must be URL of hqporner.com ending with .html
- Quality:
    - 360 : Returns 360p quality video
    - 720 : Returns 720p quality video
    - 1080 : Returns 1080p quality video
    - 2160 : Returns 2160p quality video
    - 'highest': Returns highest quality available (Recommended!)

- Path: Where the video should be stored in
- File: Location of the file containing urls. Separated by new lines!





### Get the title of the video

```py
title = API().extract_title(url)
```

### Get the actresses of the video

```py
actress = API().extract_actress(url) # Returns a list of actresses (string)
```

### Get direct download URLs

```py
url = API().get_direct_url(url, quality) # Returns URL for given quality
```

### Download the video

```py
API().download(url, quality, path) # Downloads the video with a tqdm progressbar
```
Note: Download speeds can be slow if the CDN Network is slow.

### Download from file

```py
API().download(file, quality, path) # Downloads all urls from file. Separate URLs with new line
```



### Get length of the video

```py
API().get_length(url) # Returns video length (string)
```

### Get publish date of the video

```py
API().get_publish_date(url) # Returns the publish date (string)
```

### Get categories of the video

```py
API().get_categories(url) # Returns a list with categories (string)
```

### Get total file size


```py
API().get_total_size(url, quality) # Returns the file size (int)
```

#### Exceptions are in exceptions.py, but they aren't really well implemented yet.


# Callback

HQPorner API uses a tqdm progressbar by default. You can specify your own custom progressbar with

```py
API().download(...., callback=your_custom_progressbar)
```

This will return pos (current progress) and total to the custom function.
<br>Here's an Example: 

```py
def custom_callback(self, downloaded, total, identifier): # The identifier just returns "hqporner" and can be ignored!
    """This is an example of how you can implement the custom callback"""

    percentage = (downloaded / total) * 100
    print(f"Downloaded: {downloaded} bytes / {total} bytes ({percentage:.2f}%)")
```


# License


Licensed under the LGPLv3 License

Copyright (C) 2023 EchterAlsFake


