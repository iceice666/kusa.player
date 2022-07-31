import asyncio
import json
import platform
from typing import Optional

import streamlink
import urllib3
import youtube_dl
from prompt_toolkit.application import in_terminal
from rich.console import Console

if platform.system() == "Windows":
    import os

    os.environ["PYTHON_VLC_MODULE_PATH"] = "./bin/vlc-windows"

import vlc


class Player:
    console = Console()
    http = urllib3.PoolManager(headers={
        "user-agent": "Mozilla/5.0 (Windows NT 10.0  Win64  x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.62"})

    flag_repeat: bool = False
    flag_loop: bool = False
    flag_skip: bool = False
    _finish_signal_passed: bool = False

    playlist: list[dict[str:any]] = []
    nowplaying: dict = {}

    def __init__(self, args: tuple = ("--no-ts-trust-pcr", "--ts-seek-percent", "--no-video", "-q")):
        self._rl = asyncio.get_running_loop()

        self.player: vlc.MediaPlayer = vlc.Instance(args).media_player_new()
        self.player.audio_set_volume(50)

        self.player.event_manager().event_attach(vlc.EventType.MediaPlayerStopped,
                                                 lambda *_: asyncio.run_coroutine_threadsafe(self._playing_end(),
                                                                                             self._rl))

    def event_attach(self, event, callback: callable, *args, **kwargs):
        self.player.event_manager().event_attach(event, callback, args, kwargs)

    @staticmethod
    async def execute(cmd_args):
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

    async def add_track(self, uri):

        parse = urllib3.util.parse_url(uri)
        if parse.host is None:
            return
        elif parse.host == "www.bilibili.com":
            url = await self._fetch_bilibili_url_info(uri)
        else:
            try:
                url = await self._fetch_url_info(uri)
            except (streamlink.PluginError, streamlink.NoPluginError, AttributeError):
                url = uri
                if parse.host in ['www.youtube.com', 'youtu.be']:
                    url = await self._fetch_youtube_url_info(uri)

        info = self._make_info(
            media=self.player.get_instance().media_new(url),
            url=url,
            source=uri
        )

        self.playlist.append(info)

    @staticmethod
    def _make_info(**kwargs):
        return kwargs

    @staticmethod
    async def _fetch_url_info(url):
        a = (streamlink.streams(url))['best']
        return a.url

    @staticmethod
    async def _fetch_youtube_url_info(url):
        with youtube_dl.YoutubeDL({"quiet": True}) as ydl:
            song_info = ydl.extract_info(
                url, download=False)
        try:
            url = song_info["formats"][0]["fragment_base_url"]
        except KeyError:
            url = song_info["formats"][0]["url"]
        # with open('songinfo.json','w',encoding='utf-8') as f:f.write(str(song_info))
        return url

    async def _fetch_bilibili_url_info(self, url):
        bvid = (urllib3.util.parse_url(url)).path.split('/')[-1]

        cid = json.loads(
            (self.http.request(
                'GET', f'https://api.bilibili.com/x/player/pagelist?bvid={bvid}')).data.decode('utf-8')
        )['data'][0]['cid']

        urls = json.loads(
            (self.http.request(
                'GET', f'https://api.bilibili.com/x/player/playurl?cid={cid}&bvid={bvid}&platform=html5')).data.decode(
                'utf-8')
        )['data']['durl']

        return urls[0]['url']

    async def play(self):
        if not self.playlist:
            return
        self.nowplaying = self.playlist.pop(0)
        self.player.set_media(self.nowplaying['media'])
        async with in_terminal():
            self.console.print(
                '[Player] Nowplaying: ', self.nowplaying['source'])

        self.player.play()

    async def _playing_end(self):
        if self.flag_repeat and not self.flag_skip:
            self.playlist.insert(0, self.nowplaying)
        elif self.flag_loop:
            self.playlist.append(self.nowplaying)

        self.nowplaying = {}

        await self.play()


class Search:
    def __init__(self):
        pass
