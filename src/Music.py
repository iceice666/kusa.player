import urllib3
import json
import asyncio
import typing
import youtube_dl
import streamlink

import platform
if platform.system()=="Windows ":
    import os
    os.environ["PYTHON_VLC_MODULE_PATH"] = "./vlc"

import vlc

class music:

    RemoveAll = "RemoveAll"
    http = urllib3.PoolManager()

    async def invoke(self,cmd_args):
        match cmd_args.pop():
            case 'play':
                self.add_track(cmd_args[0])

    flag_repeat = False
    flag_loop = False

    playlist = []
    nowplaying={}

    def __init__(self, args: tuple = ("--no-ts-trust-pcr","--ts-seek-percent","-q","--no-video",)):
        self.player = vlc.Instance(args).media_player_new()
        self.player.audio_set_volume(100)

    async def add_track(self, uri):
        parse = urllib3.util.parse_url(uri)
        print(f'[info] Parsing uri {uri}')
        if parse.host is None:
            pass
        elif parse.host == "www.bilibili.com":
            info = await self._fetch_bilibili_url_info(uri)
        else:
            try:
                info = await self._fetch_url_info(uri)
            except streamlink.PluginError or streamlink.NoPluginError:
                info = {"url":uri}
                if parse.host in ['www.youtube.com', 'youtu.be']:
                    info = await self._fetch_youtube_url_info(uri)


        info['uri']=self.player.get_instance().media_new(info['url'])

        self.playlist.append(info)

        if not self.player.is_playing():
            await self.play()

    async def queue(self): return self.playlist

    async def play(self):
        if self.playlist == []:
            return
        self.player.set_media(self.playlist.pop()['uri'])
        self.player.play()

    async def _fetch_url_info(self, url):
        return {'url':(streamlink.streams(url))['best'].url}

    async def _fetch_youtube_url_info(self, url):
        with youtube_dl.YoutubeDL() as ydl:
            song_info = ydl.extract_info(
                url, download=False)
        try:
            url = song_info["formats"][0]["fragment_base_url"]
        except KeyError:
            url = song_info["formats"][0]["url"]
        #with open('songinfo.json','w',encoding='utf-8') as f:f.write(str(song_info))
        return {"url":url}

    async def _fetch_bilibili_url_info(self, url):
        bvid = ((urllib3.util.parse_url(url)).path).split('/')[-1]

        cid = json.loads(
            (self.http.request(
                'GET', f'https://api.bilibili.com/x/player/pagelist?bvid={bvid}'))
            .data.decode('utf-8')
        )['data'][0]['cid']

        url = json.loads(
            (self.http.request(
                'GET', f'http://api.bilibili.com/x/player/playurl?cid={cid}&bvid={bvid}&fnval=16'))
            .data.decode('utf-8')
        )['data']['dash']['audio'][0]['baseUrl']

        return {"url":url}
