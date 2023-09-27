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
- [License](#license)


# Description

HQPorner API is an API written for the Porn site hqporner.com
<br>It can retrieve data by extracting them from the HTML code
<br> with Beautifulsoup and requests.

Please note that web scarping isn't allowed in most cases!
<br>Consider using a VPN when using this API

# Installation

```
# Installing via PyPi

pip install --upgrade hqporner_api

# Installing from GitHub to get latest version

pip install git+https://github.com/EchterAlsFake/hqporner_api.git
```

# Usage

### Import the package:

```
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

```
title = API().extract_title(url)
```

### Get the actresses of the video

```
actress = API().extract_actress(url) # Returns a list of actresses (string)
```

### Get direct download URLs

```
url = API().get_direct_url(url, quality) # Returns URL for given quality
```

### Download the video

```
API().download(url, quality, path) # Downloads the video with a tqdm progressbar
```
Note: Download speeds can be slow if the CDN Network is slow.

### Download from file

```
API().download(file, quality, path) # Downloads all urls from file. Separate URLs with new line
```



### Get length of the video

```
API().get_length(url) # Returns video length (string)
```

### Get publish date of the video

```
API().get_publish_date(url) # Returns the publish date (string)
```

### Get categories of the video

```
API().get_categories(url) # Returns a list with categories (string)
```

#### Exceptions are in exceptions.py, but they aren't really well implemented yet.


# License


Licensed under the LGPLv3 License

Copyright (C) 2023 EchterAlsFake


