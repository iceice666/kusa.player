import asyncio
import json
from pydoc import plain
import time
from typing import Optional

import streamlink
import urllib3
import youtube_dl
from bilibili_api import parse_link, video
from prompt_toolkit.application import in_terminal
from rich.console import Console
from rich.style import Style
from rich.traceback import install

from config.CONFIG import *
from src.core import VLC

install(show_locals=True)

http = urllib3.PoolManager(headers={
    "user-agent": "Mozilla/5.0 (Windows NT 10.0  Win64  x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                  "Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.62"})


def send_get_request(url) -> dict:
    return json.loads((http.request('GET', url)).data.decode('utf-8'))


class Track:

    def __init__(self, *,
                 website: str = None,
                 source_url: str = None,
                 webpage_url: str = None,
                 title: str = None,
                 author: str = None,
                 expired_time: int = None,
                 video_id: str = None
                 ):
        self.website = website
        self.source_url = source_url
        self.webpage_url = webpage_url
        self.title = title
        self.author = author
        self.expired_time = expired_time
        self.video_id = video_id


class Player:
    flag_repeat: bool = False
    flag_loop: bool = False
    flag_skip: bool = False
    _finish_signal_passed: bool = False

    playlist: list[Track] = []
    nowplaying: Optional[Track] = None

    def __init__(self,  rich_console=Console()):
        self.console = rich_console
        self._rl = asyncio.get_running_loop()

        _v=VLC()
        _v._playing_end=self._playing_end

        self.player=_v.player



    async def execute(self, cmd_args):
        for c in cmd_args:
            exec(c.replace("$", "self."))

    async def help_cmd(self):
        self.console.print("help!")

    async def queue(self):
        return self.playlist

    async def volume(self, vol: Optional[int] = None):
        await self.player.volume(vol)

    async def position(self, pos: int | float):
        await self.player.position(pos)

    async def repeat(self):
        self.flag_repeat = not self.flag_repeat

    async def loop(self):
        self.flag_loop = not self.flag_loop

    async def skip(self):
        self.player.stop()

    async def pause(self):
        self.player.pause()

    async def resume(self):
        self.player.resume()

    async def clear(self):
        self.playlist = []

    async def add_track(self, track):

        fetched_info = await Fetching.fetch_info(track)



        self.playlist += fetched_info

        for i in fetched_info:
            self.console.print(f'[Player] Added Track: {i.webpage_url}')

        if not self.player.is_playing and self.nowplaying is None and len(self.playlist) > 1:
            await self.play()

    async def play(self):
        if not self.playlist:
            return
        self.nowplaying = self.playlist.pop(0)
        if time.time() > self.nowplaying.expired_time:
            self.console.print(
                '[Player] [yellow]This link expired, re-fetching...[/yellow]')
            self.nowplaying.source_url = (await Fetching.fetch_info(self.nowplaying))[0].source_url

            self.nowplaying.expired_time = time.time() + 3600

        self.player.set_uri(self.nowplaying.source_url)

        async with in_terminal():
            self.console.print('[Player] ', end='')
            self.console.print(
                'Nowplaying: ', self.nowplaying.title, style=Style(color='#D670B3'))

        self.player.play()

    async def _playing_end(self):
        if self.flag_repeat and not self.flag_skip:
            self.playlist.insert(0, self.nowplaying)
        elif self.flag_loop and not self.flag_skip:
            self.playlist.append(self.nowplaying)

        self.nowplaying = None

        await self.play()


class Fetching:
    def __init__(self):
        pass

    @classmethod
    async def fetch_info(cls, track):

        if track.website:
            if track.website == 'youtube':
                func = cls.fetch_youtube_url_info
            elif track.website == 'bilibili':
                func = cls.fetch_bilibili_url_info
            else:
                func = cls.fetch_url_info

            if track.video_id:
                arguments = {"video_id": track.video_id}
            else:
                arguments = {"webpage_url": track.webpage_url}

        elif track.webpage_url:
            parse = urllib3.util.parse_url(track.webpage_url)

            if parse.host.lower() == "www.bilibili.com":
                func = cls.fetch_bilibili_url_info
            elif parse.host.lower() in ['www.youtube.com', 'youtu.be']:
                func = cls.fetch_youtube_url_info
            else:
                func = cls.fetch_url_info

            arguments = {"webpage_url": track.webpage_url}

        else:
            func = cls.fetch_url_info
            arguments = {"webpage_url": track.webpage_url}

        result = await func(**arguments)
        for i in result:
            i.expired_time = int(time.time()) + 3600

        return result

    @staticmethod
    async def fetch_url_info(webpage_url):
        return Track(source_url=(streamlink.streams(webpage_url))['best'].url)

    @staticmethod
    async def fetch_youtube_url_info(webpage_url=None, video_id=None):
        result = []
        if video_id:
            webpage_url = f'https://youtu.be/{video_id}'

        with youtube_dl.YoutubeDL({"quiet": True}) as ydl:
            source_info: dict = ydl.extract_info(
                webpage_url, download=False)

        if source_info.get('_type', None) == 'playlist':
            playlist = source_info['entries']
        else:
            playlist = [source_info]

        for i in playlist:
            try:
                source_url = i["formats"][0]["fragment_base_url"]
            except KeyError:
                source_url = i["formats"][0]["url"]

            result.append(Track(website='youtube',
                                source_url=source_url,
                                webpage_url=i['webpage_url'],
                                title=i['title'],
                                author=i['uploader'],
                                ))
        return result

    # YouTube API Key required
    # Youtube Api playlist api only returns 50 videos per GET request sent.
    @staticmethod
    async def fetch_youtube_playlist_info(webpage_url) -> list[Track]:
        api = f'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet,contentDetails,status' \
              f'&playlistId={webpage_url}&key={YOUTUBE_API}&maxResults=50'

        playlist=send_get_request(api)['items']

        return [Track(website='youtube', video_id=i['contentDetails']['videoId']) for i in playlist]

    @staticmethod
    async def fetch_bilibili_url_info(webpage_url=None, video_id=None):
        v: video.Video

        if video_id:
            v = video.Video(video_id)
        else:
            v = (await parse_link(webpage_url))[0]

        source_info = await v.get_info()

        return [Track(website='bilibili',
                      source_url=(await v.get_download_url(0, html5=True))["durl"][0]['url'],
                      webpage_url=webpage_url,
                      title=source_info['title'],
                      author=source_info['owner']['name'])]

    @staticmethod
    async def search_youtube(searching):
        searched_list = send_get_request(
            f"https://www.googleapis.com/youtube/v3/search?part=snippet&"
            f"q={searching.replace(' ', '+')}&key={YOUTUBE_API}&maxResults=20&"
            "type=video"
        )['items']


        return [Track(
                title=i['snippet']['title'],
                website='youtube',
                video_id=i['id']['videoId']) for i in searched_list]

    @staticmethod
    async def search_bilibili(searching):
        searched_list = send_get_request(
            f'https://api.bilibili.com/x/web-interface/search/all/v2?keyword={searching}')['data']['result'][-1]['data']

        return [Track(title=str(i['title']).replace('<em class="keyword">', '').replace('</em>', ''),
                      website='bilibili',
                      video_id=i['bvid']) for i in searched_list]
