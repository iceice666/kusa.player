import asyncio
from typing import Optional

from prompt_toolkit.application import in_terminal
from rich.style import Style
from rich.traceback import install

from .vlc_core import VLC

install(show_locals=True)


class Player(VLC):
    flag_repeat: bool = False
    flag_loop: bool = False
    flag_skip: bool = False
    _finish_signal_passed: bool = False

    queue: list[Track] = []
    nowplaying: Optional[Track] = None

    def __init__(self):
        super().__init__()
        self._rl = asyncio.get_running_loop()

        
    def execute(self, cmd_args):
        for c in cmd_args:
            exec(c.replace("$", "self."))

    def repeat(self):
        self.flag_repeat = not self.flag_repeat

    def loop(self):
        self.flag_loop = not self.flag_loop

    def clear(self):
        self.queue = []

    async def add_track(self, track):
        fetched_info = await NetworkIO.fetch_info(track)

        if fetched_info is None:
            return

        self.queue += fetched_info

        for i in fetched_info:
            console.print(f'[Player] Added Track: {i.webpage_url}')

        if not self.is_playing and self.nowplaying is None and len(self.queue) > 1:
            await self.play()

    async def play(self):
        if not self.queue:
            return
        self.nowplaying = self.queue.pop(0)
        if time.time() > self.nowplaying.expired_time:
            async with in_terminal():
                console.print(
                    '[Player] [yellow]This link expired, re-fetching...[/yellow]')
            self.nowplaying.source_url = (await NetworkIO.fetch_info(self.nowplaying))[0].source_url

            self.nowplaying.expired_time = time.time() + 3600

        self.player.set_uri(self.nowplaying.source_url)

        async with in_terminal():
            console.print(
                f'[Player] [#D670B3]Nowplaying: {self.nowplaying.title}', )

        self.player.play()

    async def _playing_end(self):
        if self.flag_repeat and not self.flag_skip:
            self.queue.insert(0, self.nowplaying)
        elif self.flag_loop and not self.flag_skip:
            self.queue.append(self.nowplaying)

        self.nowplaying = None

        await self.play()

    @property
    def is_playing(self):
        return self.player.is_playing()
