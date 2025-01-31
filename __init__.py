# Copyright 2018 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import feedparser
import re
import os
import subprocess

from adapt.intent import IntentBuilder
from mycroft.audio import wait_while_speaking
from mycroft.skills.core import intent_handler
from mycroft.skills.common_play_skill import CommonPlaySkill, CPSMatchLevel

from requests import Session

STREAM = '/tmp/stream'

def find_mime(url):
    mime = 'audio/mpeg'
    response = Session().head(url, allow_redirects=True)
    if 200 <= response.status_code < 300:
        mime = response.headers['content-type']
    return mime

class NewsSkill(CommonPlaySkill):
    def __init__(self):
        super().__init__(name="NewsSkill")
        self.curl = None

    def CPS_match_query_phrase(self, phrase):
        if self.voc_match(phrase, "News"):
            # TODO: Match against NPR, BBC, etc
            return ("news", CPSMatchLevel.TITLE)

    def CPS_start(self, phrase, data):
        # Use the "latest news" intent handler
        self.handle_latest_news(None)

    @property
    def url_rss(self):
        url_rss = final_bulletin_url

        feed_url = 'http://createfeed.fivefilters.org/extract.php?url=https%3A%2F%2Fwww.radionz.co.nz%2Fprogrammes%2Fnews-bulletin&in_id_or_class=o-digest+o-digest--audio+o-digest--extended+u-blocklink+no-thumbnail&url_contains=%2Fnews-bulletin%2F'

        # Parsing the specified feed
        rss_feed = feedparser.parse(feed_url)

        # Setting the first feed entry as the latest bulletin
        latest_bulletin = feed.entries[0].link

        # Extracting the date/bulletin information from the url
        try:
            bulletin_extract = re.search('story/(.+?)/radio-new-zealand-news', latest_bulletin).group(1)
        except AttributeError:
            # AAA, ZZZ not found in the original string
            bulletin_extract = '' # apply your error handling

        final_bulletin_url = "https://www.radionz.co.nz/audio/player?audio_id={}".format(bulletin_extract)

        # After the intro, find and start the news stream
        # select the first link to an audio file
        for link in data['entries'][0]['links']:
            if 'audio' in link['type']:
                media = link['href']
                break
        else:
            # fall back to using the first link in the entry
            media = data['entries'][0]['links'][0]['href']
        self.log.info('Will play news from URL: '+media)
        return media

    @intent_handler(IntentBuilder("").require("Latest").require("News"))
    def handle_latest_news(self, message):
        try:
            self.stop()

            mime = find_mime(self.url_rss)
            # (Re)create Fifo
            if os.path.exists(STREAM):
                os.remove(STREAM)
            self.log.debug('Creating fifo')
            os.mkfifo(STREAM)

            self.log.debug('Running curl {}'.format(self.url_rss))
            self.curl = subprocess.Popen(
                'curl -L "{}" > {}'.format(self.url_rss, STREAM),
                shell=True)

            # Speak an intro
            self.speak_dialog('news', wait=True)
            # Begin the news stream
            self.CPS_play(('file://' + STREAM, mime))

        except Exception as e:
            self.log.error("Error: {0}".format(e))

    def stop(self):
        if self.curl:
            self.curl.kill()
            self.curl.communicate()


def create_skill():
    return RNZNewsSkill()
