#!C:\Users\Andrew\AppData\Local\Programs\Python\Python37-32

import feedparser
import re

# Feed settings -- name not required
feed_name = 'RNZ Bulletin'
feed_url = 'http://createfeed.fivefilters.org/extract.php?url=https%3A%2F%2Fwww.radionz.co.nz%2Fprogrammes%2Fnews-bulletin&in_id_or_class=o-digest+o-digest--audio+o-digest--extended+u-blocklink+no-thumbnail&url_contains=%2Fnews-bulletin%2F'

# Parsing the specified feed
feed = feedparser.parse(feed_url)

# Setting the first feed entry as the latest bulletin
latest_bulletin = feed.entries[0].link

# Extracting the date/bulletin information from the url
try:
    bulletin_extract = re.search('story/(.+?)/radio-new-zealand-news', latest_bulletin).group(1)
except AttributeError:
    # AAA, ZZZ not found in the original string
    bulletin_extract = '' # apply your error handling

final_bulletin_url = "https://www.radionz.co.nz/audio/player?audio_id={}".format(bulletin_extract)

print(final_bulletin_url)
