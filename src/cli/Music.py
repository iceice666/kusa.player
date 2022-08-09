import asyncio
from typing import Optional

import InquirerPy
from InquirerPy import inquirer
from InquirerPy.base import Choice
from prompt_toolkit.application import in_terminal
from rich.console import Console
from rich.markdown import Markdown
from rich.style import Style
from rich.traceback import install

from src.cli.core import *
from src.core.vlc_core import VLC

install(show_locals=True)

console = Console()


class Player:
    flag_repeat: bool = False
    flag_loop: bool = False
    flag_skip: bool = False
    _finish_signal_passed: bool = False

    queue: list[Track] = []
    nowplaying: Optional[Track] = None

    def __init__(self):
        self._rl = asyncio.get_running_loop()

        _v = VLC()
        _v._playing_end = self._playing_end

        self.player = _v

    def execute(self, cmd_args):
        for c in cmd_args:
            exec(c.replace("$", "self."))

    def volume(self, vol: Optional[int] = None):
        return self.player.volume(vol)

    def position(self, pos: int | float):
        self.player.position(pos)

    def repeat(self):
        self.flag_repeat = not self.flag_repeat

    def loop(self):
        self.flag_loop = not self.flag_loop

    def skip(self):
        self.player.stop()

    def pause(self):
        self.player.pause()

    def resume(self):
        self.player.resume()

    def clear(self):
        self.queue = []

    async def add_track(self, track):

        fetched_info = await Fetch.fetch_info(track)

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
            console.print(
                '[Player] [yellow]This link expired, re-fetching...[/yellow]')
            self.nowplaying.source_url = (await Fetch.fetch_info(self.nowplaying))[0].source_url

            self.nowplaying.expired_time = time.time() + 3600

        self.player.set_uri(self.nowplaying.source_url)

        async with in_terminal():
            console.print('[Player] ', end='')
            console.print(
                'Nowplaying: ', self.nowplaying.title, style=Style(color='#D670B3'))

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


class Commands:
    YOUTUBE_API = config.get('YOUTUBE_API', None)
    MUSIC = Player()
    with open('./config/quickplay_save.json', encoding='utf-8') as __f:
        quickplay_save: dict = json.loads(__f.read())

    @staticmethod
    async def unknown_cmd():
        async with in_terminal():
            console.print('Unknown command')

    def exit_(self):
        with open('./config/quickplay_save.json', encoding='utf-8', mode='w') as __f:
            __f.write(json.dumps(self.quickplay_save))
        console.print(
            'Thanks for using kusa! :partying_face: \n:party_popper: Bye~ Have a great day~ :party_popper:')

    @staticmethod
    def cmd_help():
        console.print(Markdown(help_md, ))

    async def cmd_play(self, cmd_args):
        if not cmd_args:
            if not self.MUSIC.is_playing():
                return await self.MUSIC.play()

        with console.status(f"[light green]Fetching data...(Total {len(cmd_args)})"):
            for url in cmd_args:
                if url == '':
                    continue

                if 'youtube' in url and 'playlist' in url and self.YOUTUBE_API is not None:
                    for t in await Fetch.fetch_youtube_playlist_info(url):
                        await self.MUSIC.add_track(t)

                await self.MUSIC.add_track(Track(webpage_url=url))

            console.print('[Console] Added all requested urls')

        if self.MUSIC.nowplaying is None:
            await self.MUSIC.play()

    def cmd_volume(self, cmd_args):
        vol = self.MUSIC.volume()
        console.print(f"[Console] Volume: {vol} ", end='')

        if cmd_args:
            for i in cmd_args:
                if i != '':
                    vol = int(cmd_args[0])

            if vol > 0:
                self.MUSIC.volume(vol)
                console.print(
                    f"=> {vol}")
        else:
            console.print()

    def cmd_nowplaying(self):
        np = self.MUSIC.nowplaying
        console.print('[Console] Nowplaying:', end=' ')
        if not np:
            return console.print('None', style=Style(color='#D670B3'))
        elif np.website == 'bilibili':
            line1 = f'[#00FFFF]Bilibili @ {np.author}[/#00FFFF]'
        elif np.website == 'youtube':
            line1 = f'[red]Youtube @ {np.author}[/red]'
        else:
            line1 = f'{np.website} @ {np.author}'

        console.print(line1, )
        console.print(np.title, style=Style(color='#D670B3'))
        console.print(np.webpage_url, style=Style(
            color='blue', underline=True))

    def cmd_queue(self):
        console.print("[Console] Queue")
        for n, i in enumerate(self.MUSIC.queue):
            if i.website == 'bilibili':
                _l = f'[#00FFFF]{i.website} @ {i.author}[/#00FFFF]'
            elif i.website == 'youtube':
                _l = f'[red]{i.website} @ {i.author}[/red]'
            else:
                _l = f'{i.website} @ {i.author}'

            console.print(f'{n}. {_l}')
            console.print(
                f'{i.title}', style=Style(color='#D670B3'))
            console.print(i.webpage_url, style=Style(
                color='blue', underline=True))

    def cmd_skip(self):
        self.MUSIC.skip()

    def cmd_clear(self):
        self.MUSIC.clear()

    def cmd_stop(self):
        self.cmd_clear()
        self.cmd_skip()

    def cmd_pause(self):
        console.print('[Console] Paused')
        self.MUSIC.pause()

    def cmd_resume(self):
        console.print('[Console] Resumed')
        self.MUSIC.resume()

    def cmd_loop(self):
        self.MUSIC.loop()
        console.print(
            '[Console] Now player [red bold]will{}[/red bold] loop the queue.'.format(
                "" if self.MUSIC.flag_loop else " not "))

    def cmd_repeat(self):
        self.MUSIC.repeat()
        console.print(
            '[Console] Now player [red bold]will {}[/red bold] repeat the song which is playing.'.format(
                "" if self.MUSIC.flag_repeat else " not "))

    def cmd_position(self, cmd_args):
        if not cmd_args:
            print(
                "[Console] Position {}s / {}s ({}%)".format(
                    int(self.MUSIC.player.get_time() / 1000),
                    int(self.MUSIC.player.get_length() / 1000),
                    int(self.MUSIC.player.get_position() * 100)
                ))
        else:
            self.MUSIC.position(float(cmd_args[0]))

    async def cmd_search(self, cmd_args):
        website = "youtube"
        keyword = ''
        choices: list[Choice] = []
        fetch_result: list['Track'] = []

        if '-y' in cmd_args or '-yt' in cmd_args or '--youtube' in cmd_args:
            website = "youtube"
        elif '-b' in cmd_args or '--bilibili' in cmd_args:
            website = "bilibili"

        for i in cmd_args:
            if i.startswith('-'):
                continue
            else:
                keyword += i + ' '

        if website == "bilibili":
            fetch_result = await Fetch.search_bilibili(keyword)

        elif website == "youtube":
            fetch_result = await Fetch.search_youtube(keyword)

        for info in fetch_result:
            choices.append(
                Choice(name=f'{info.title}\n         {info.webpage_url}', value=info))

        selections: Optional[list] = await inquirer.checkbox(message=f'Press Space to select and press Enter to enter. >',
                                                             choices=choices,
                                                             raise_keyboard_interrupt=False,
                                                             mandatory=False, ).execute_async()

        if selections is None:
            return console.print('Selection cancelled.')

        with console.status(f"[light green]Fetching data...(Total {len(selections)})"):
            for track in selections:
                if track == 'Cancel':
                    continue
                track.website = website
                await self.MUSIC.add_track(track=track)

            console.print('[Console] Added all requested results')

        if self.MUSIC.nowplaying is None:
            await self.MUSIC.play()

    def cmd_save(self, cmd_args):
        if not cmd_args:
            return

        name = ""
        _r = ""

        if '-c' in cmd_args or '-d' in cmd_args:
            for i in cmd_args:
                if i.startswith('-'):
                    _r = i
                else:
                    name += i + ' '

            if _r == '-c':
                _s = []

                for i in self.MUSIC.queue + [self.MUSIC.nowplaying]:
                    _s.append(i.webpage_url)

                self.quickplay_save[name] = _s
            elif _r == '-d':
                del self.quickplay_save[name]

        else:
            while True:
                i = cmd_args.pop(0)
                if i == '-':
                    break
                else:
                    name += i + ' '

            self.quickplay_save[name] = cmd_args

    async def cmd_quickplay(self, cmd_args):
        if not cmd_args:
            choices = []

            for i in self.quickplay_save:
                render_text = i
                for j in self.quickplay_save[i]:
                    render_text += f'\n       {j}'

                choices.append(Choice(name=render_text, value=i))

            selections: Optional[list] = await inquirer.checkbox(message=f'Press Space to select and press Enter to enter. >',
                                                                 choices=choices,
                                                                 raise_keyboard_interrupt=False,
                                                                 mandatory=False, ).execute_async()
            if not selections:
                console.print('Selection cancelled.')
            else:
                with console.status(f"[light green]Fetching data...(Total {len(cmd_args)})"):
                    for i in selections:
                        for j in self.quickplay_save[i]:
                            await self.MUSIC.add_track(Track(webpage_url=j))

                    console.print(
                        '[Console] Added all selected quickplay urls')

                if self.MUSIC.nowplaying is None:
                    await self.MUSIC.play()

        else:
            key = cmd_args.pop(0)
            playlist = self.quickplay_save.get(key, None)
            if playlist is None:
                return console.print(f'[Console] Quickplay: Unknown keyword {playlist}')
            else:
                pass

        if not self.MUSIC.player.is_playing():
            return await self.MUSIC.play()

    _default_color = InquirerPy.utils.get_style({
        "questionmark": "#ff4500",
        "answermark": "",
        "answer": "#267cd8",
        "input": "#006400",
        "question": "",
        "answered_question": "",
        "instruction": "#abb2bf",
        "long_instruction": "#abb2bf",
        "pointer": "#8f1eec",
        "checkbox": "#8fce00",
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

    async def ask(self, ):
        return (str(await inquirer.text(
            message="Music >",
            amark="", style=self._default_color,
            raise_keyboard_interrupt=False,
            mandatory=True, mandatory_message='If you want to close the music player, type "exit" to do.'
        ).execute_async()))
