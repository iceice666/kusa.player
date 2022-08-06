import asyncio
import json
import platform
import time
from typing import Optional

import streamlink
import urllib3
import youtube_dl
from bilibili_api import parse_link, video
from prompt_toolkit.application import in_terminal
from rich.console import Console
from rich.style import Style

from config.CONFIG import *

if platform.system() == "Windows":
    import os

    os.environ["PYTHON_VLC_MODULE_PATH"] = "./bin/vlc-windows"

import vlc

http = urllib3.PoolManager(headers={
    "user-agent": "Mozilla/5.0 (Windows NT 10.0  Win64  x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                  "Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.62"})


def send_get_request(url) -> dict:
    return json.loads((http.request('GET', url)).data.decode('utf-8'))


class Player:
    flag_repeat: bool = False
    flag_loop: bool = False
    flag_skip: bool = False
    _finish_signal_passed: bool = False

    playlist: list[dict[str:any]] = []
    nowplaying: dict = {}

    def __init__(self, args: tuple = ("--no-ts-trust-pcr", "--ts-seek-percent", "--no-video", "-q"), rich_console=Console()):
        self.console = rich_console
        self._rl = asyncio.get_running_loop()

        self.player: vlc.MediaPlayer = vlc.Instance(args).media_player_new()
        self.player.audio_set_volume(20)

        self.player.event_manager().event_attach(vlc.EventType.MediaPlayerStopped,
                                                 lambda *_: asyncio.run_coroutine_threadsafe(self._playing_end(),
                                                                                             self._rl))

    def event_attach(self, event, callback: callable, *args, **kwargs):
        self.player.event_manager().event_attach(event, callback, args, kwargs)

    async def execute(self, cmd_args):
        for c in cmd_args:
            exec(c.replace("$", "self."))

    async def help_cmd(self):
        self.console.print("help!")

    async def queue(self):
        return self.playlist

    async def volume(self, vol: Optional[int] = None):
        if vol is None:
            pass
        else:
            self.player.audio_set_volume(vol)
        return self.player.audio_get_volume()

    async def position(self, pos: int | float):
        if 1 > pos >= 0:
            self.player.set_position(pos)
        elif 1 <= pos < self.player.get_length():
            self.player.set_position(pos / self.player.get_length())

    async def repeat(self):
        self.flag_repeat = not self.flag_repeat

    async def loop(self):
        self.flag_loop = not self.flag_loop

    async def skip(self):
        self.flag_skip = True
        self.player.stop()

    async def pause(self):
        self.player.set_pause(1)

    async def resume(self):
        self.player.set_pause(0)

    async def clear(self):
        self.playlist = []

    async def add_track(self, webpage_url=None, website=None, vid_id=None, ):

        self.playlist += await Search.fetch_info(webpage_url, website, vid_id)

        if vid_id is not None:
            if vid_id.startswith('BV'):
                url = f'https://www.bilibili.com/video/{vid_id}'
            else:
                url = f'https://youtu.be/{vid_id}'
        else:
            url = webpage_url

        self.console.print(f'[Player] Added Track: {url}')

        if not self.player.is_playing() and not self.nowplaying and len(self.playlist) > 1:
            await self.play()

    async def play(self):
        if not self.playlist:
            return
        self.nowplaying = self.playlist.pop(0)
        if time.time() > self.nowplaying['expired_time']:
            self.console.print(
                '[Player] [yellow]This link expired, re-fetching...[/yellow]')
            self.nowplaying['url'] = (await Search.fetch_info(
                webpage_url=self.nowplaying['website_url'],
                website=self.nowplaying['website'])
                                      )[0]['source_url']

            self.nowplaying['expired_time'] = time.time() + 3600

        self.player.set_media(
            self.player.get_instance().media_new(self.nowplaying['source_url']))

        async with in_terminal():
            self.console.print('[Player] ', end='')
            self.console.print(
                'Nowplaying: ', self.nowplaying['title'], style=Style(color='#D670B3'))

        self.player.play()

    async def _playing_end(self):
        if self.flag_repeat and not self.flag_skip:
            self.playlist.insert(0, self.nowplaying)
        elif self.flag_loop and not self.flag_skip:
            self.playlist.append(self.nowplaying)

        self.nowplaying = {}

        await self.play()


class Search:
    def __init__(self):
        pass

    '''
    tracks format
    {
        'website':'',
        'webpage_url':'',
        'source_url':'',
        'title':'',
        'author':'',
        'expired_time':''
    }

    '''

    @classmethod
    async def fetch_info(cls, webpage_url=None, website=None, vid_id=None, ):

        if website is None and webpage_url is not None:
            parse = urllib3.util.parse_url(webpage_url)

            if parse.host.lower() == "www.bilibili.com":
                return await Search.fetch_bilibili_url_info(webpage_url)
            elif parse.host.lower() in ['www.youtube.com', 'youtu.be']:
                return await Search.fetch_youtube_url_info(webpage_url)
            else:
                return await Search.fetch_url_info(webpage_url)

        elif website.lower() == 'youtube':
            if vid_id is None:
                return await Search.fetch_youtube_url_info(webpage_url)
            elif vid_id is not None:
                return await Search.fetch_youtube_url_info(f'https://youtu.be/{vid_id}')

        elif website.lower() == 'bilibili':
            if vid_id is None:
                return await Search.fetch_bilibili_url_info(webpage_url)
            elif vid_id is not None:
                return await Search.fetch_bilibili_url_info(bvid=vid_id)

    @staticmethod
    async def fetch_url_info(url):
        return (streamlink.streams(url))['best'].url

    @staticmethod
    async def fetch_youtube_url_info(webpage_url):
        _return = []
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

            _return.append({'website': 'youtube',
                            'source_url': source_url,
                            'webpage_url': i['webpage_url'],
                            'title': i['title'],
                            'author': i['uploader'],
                            'expired_time': int(time.time()) + 3600})
        return _return

    @staticmethod
    async def fetch_bilibili_url_info(webpage_url=None, bvid=None):
        v: video.Video

        if bvid is not None:
            v = video.Video(bvid)
        else:
            v = (await parse_link(webpage_url))[0]

        source_info = await v.get_info()

        return [{'website': 'bilibili',
                 'source_url': (await v.get_download_url(0, html5=True))["durl"][0]['url'],
                 'webpage_url': webpage_url,
                 'title': source_info['title'],
                 'author': source_info['owner']['name'],
                 'expired_time': int(time.time()) + 3600}]

    @staticmethod
    async def youtube(searching):
        searched_list = send_get_request(
            f"https://www.googleapis.com/youtube/v3/search?part=snippet&"
            f"q={searching.replace(' ', '+')}&key={YOUTUBE_API}&maxResults=20&"
            "type=video"
        )['items']

        searched_result = []
        for i in searched_list:
            searched_result.append({
                'title': i['snippet']['title'],
                'website': 'youtube',
                'vid_id': i['id']['videoId']})

        return searched_result

    @staticmethod
    async def bilibili(searching):
        searched_list = send_get_request(
            f'https://api.bilibili.com/x/web-interface/search/all/v2?keyword={searching}')['data']['result'][-1]['data']
        searched_result = []
        for i in searched_list:
            searched_result.append({
                'title': str(i['title']).replace(
                    '<em class="keyword">', '').replace('</em>', ''),
                'website': 'bilibili',
                'vid_id': i['bvid']
            })
        return searched_result
