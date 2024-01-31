# 0.9

- HQPorner API now uses regexes instead of bs4
- Most properties are cached now (better performance)
- Finished `get_videos_by_actress` function
- code refactoring
- Performance optimizations
- Better documentation
- Better readme
- Removed exceptions

# 1.0

- Split video methods into a new `Video` object
- Refactored code
- You can now search for videos
- You can now get videos by a category
- Fixed the get videos by actress page issue
- Added exceptions
- Updated Documentation
- Added a new progressbar

# 1.1

- added `get_top_porn` method
- added `get_all_categories`
- added `get_random_video`
- added `get_brazzers_videos`
- See Documentation for usage details

# 1.2

- fixed get_by_model function
- fixed get_by_category
- fixed some constants

# 1.3

- restructured some methods
- added some stuff related to code quality
- fixed some issues in the consts
- added `Category` and `Sort` object
- added decorators to check video objects a bit better (still not the best)
- removed tqdm, as I think we don't need it and a text progressbar is good enough

I recommend reading through t he documentation, as some usages have changed.

# 1.4
- You can now pass the quality parameter as a string instead of the object
