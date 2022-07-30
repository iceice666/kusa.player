import asyncio
import atexit
import sys

import InquirerPy
from InquirerPy import inquirer
from prompt_toolkit.application import run_in_terminal
from rich.console import Console

from GIYA import Command, Dispatcher, Ignore
from src.Music import Player


class Interface:
    # https://inquirerpy.readthedocs.io/en/latest/pages/style.html
    _default_color = InquirerPy.utils.get_style({
        "questionmark": "#ff4500",
        "answermark": "",
        "answer": "#267cd8",
        "input": "#006400",
        "question": "",
        "answered_question": "",
        "instruction": "#abb2bf",
        "long_instruction": "#abb2bf",
        "pointer": "#61afef",
        "checkbox": "#98c379",
        "separator": "",
        "skipped": "#5c6370",
        "validator": "",
        "marker": "#e5c07b",
        "fuzzy_prompt": "#c678dd",
        "fuzzy_info": "#abb2bf",
        "fuzzy_border": "#4b5263",
        "fuzzy_match": "#c678dd",
        "spinner_pattern": "#e5c07b",
        "spinner_text": ""
    })

    def _play(self, cmd_args):
        for uri in cmd_args:
            asyncio.gather(self.MUSIC.add_track(uri))
            self.console.print(
                f'[Player] Add Track: Parsing uri {uri}')

    def _volume(self, volume=None):
        if volume is None:
            vol = asyncio.gather(self.MUSIC.volume(None))
            self.console.print(f"[Player] Volume: {vol}")
        else:
            prev_vol = asyncio.gather(self.MUSIC.volume(None))
            vol = asyncio.gather(self.MUSIC.volume(volume))
            self.console.print(f"[Player] Volume: {prev_vol} => {vol}")

    def _stop(self):
        asyncio.gather(self.MUSIC.clear(),
                       self.MUSIC.skip())

    def _pause(self):
        asyncio.gather(self.MUSIC.pause())
        self.console.print('[Player] Paused')

    def _resume(self):
        asyncio.gather(self.MUSIC.resume())

    def _loop(self):
        asyncio.gather(self.MUSIC.loop())
        self.console.print(
            f'[Player] Now player [red bold]will{"" if self.MUSIC.flag_loop else " not"}[/red bold] loop the queue.')

    def _repeat(self):
        asyncio.gather(self.MUSIC.repeat())
        self.console.print(
            f'[Player] Now player [red bold]will{"" if self.MUSIC.flag_repeat else " not"}[/red bold] repeat the song which is playing.')

    def _position(self, pos: float):
        asyncio.gather(self.MUSIC.position(pos if pos else None))

    def _unknown_cmd(self):
        run_in_terminal(
            self.console.print('Unknown command :question:'))

    def __init__(self):
        self.console = Console()
        self.dispatcher = Dispatcher() \
            .register(Command('p', 'play')
                      .argument((Ignore,), self._play)) \
            .register(Command('vol', 'volume')
                      .argument((Ignore,), self._volume)) \
            .register(Command('nowplaying', 'np')
                      .argument((),
                                lambda *_: self.console.print(self.MUSIC.nowplaying))) \
            .register(Command('queue', 'q')
                      .argument((),
                                lambda *_: self.console.print(self.MUSIC.playlist))) \
            .register(Command('skip')
                      .argument((),
                                lambda *_: asyncio.gather(self.MUSIC.skip()))) \
            .register(Command('clear')
                      .argument((),
                                lambda *_: asyncio.gather(self.MUSIC.clear()))) \
            .register(Command('stop')
                      .argument((), self._stop)) \
            .register(Command('pause', 'pa')
                      .argument((), self._pause)) \
            .register(Command('resume', 're')
                      .argument((), self._resume)) \
            .register(Command('loop')
                      .argument((), self._loop)) \
            .register(Command('repeat')
                      .argument((), self._repeat)) \
            .register(Command('position', 'pos')
                      .argument((int,), self._position)) \
            .register(Command('exit')
                      .argument((), lambda *_: sys.exit(0))) \
            .unknown_cmd(self._unknown_cmd)

    async def entrypoint(self):
        self.MUSIC = Player()

        while True:
            command = str(await inquirer.text(message="Music >", amark="", style=self._default_color).execute_async())
            try:
                self.dispatcher.execute(command)
            except KeyboardInterrupt:
                pass
            except Exception as e:
                print(f"\n{e}")

    def exiting(self):
        self.console.print(':wave: \nBye~ \nHave a great day~')

    def run(self):
        atexit.register(self.exiting)
        try:
            asyncio.run(self.entrypoint())
            asyncio.get_running_loop().run_forever()
        except KeyboardInterrupt:
            sys.exit(0)
