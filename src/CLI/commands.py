from typing import Optional

from InquirerPy import inquirer
from InquirerPy.base import Choice
from prompt_toolkit.application import in_terminal
from rich.markdown import Markdown
from rich.style import Style
import json

from src.core import *
from src.core.fetch import *
from src.core.music import Player


class Commands:
    MUSIC = Player()
    with open('./config/quickplay_save.json', encoding='utf-8') as __f:
        quickplay_save: dict = json.loads(__f.read())

    @staticmethod
    async def unknown_cmd():
        async with in_terminal():
            console.print('Unknown command')

    @staticmethod
    def cmd_exit():
        console.print(
            'Thanks for using kusa! :partying_face: \n:party_popper: Bye~ Have a great day~ :party_popper:\nClose in 3 secs.')

    @staticmethod
    def cmd_help():
        console.print(Markdown(help_md, ))

    async def cmd_play(self, cmd_args):
        if not cmd_args:
            if not self.MUSIC.is_playing():
                return await self.MUSIC.play()

        _vc = 0
        with console.status(f"[light green]Fetching data...") as status:
            for url in cmd_args:

                if url == '':
                    pass

                elif 'youtube' in url and 'playlist' in url and config.YOUTUBE_API is not None:
                    playlist = await NetworkIO.fetch_youtube_playlist_info(url)
                    _pvc = 0
                    for t in playlist:
                        status.update(f"[green]Fetching data...(Total urls:{_vc}/{len(cmd_args)} "
                                      f"[yellow]playlist:{_pvc}/{len(playlist)}[/yellow])")
                        await self.MUSIC.add_track(t)
                        _pvc += 1

                else:
                    await self.MUSIC.add_track(Track(webpage_url=url))

                _vc += 1

            console.print(
                f'[Console] Added all requested urls (Total urls:{_vc}/{len(cmd_args)})')

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
            fetch_result = await NetworkIO.search_bilibili(keyword)

        elif website == "youtube":
            fetch_result = await NetworkIO.search_youtube(keyword)

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

        with open('./config/quickplay_save.json', encoding='utf-8', mode='w') as _f:
            _f.write(json.dumps(self.quickplay_save))

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
                _ic = 0
                with console.status(f"[light green]Fetching data...(Total {_ic}/{len(selections)})") as status:
                    for i in selections:
                        _jc = 0
                        _ljc = len(self.quickplay_save[i])
                        for j in self.quickplay_save[i]:
                            status.update(
                                f"[light green]Fetching data...(Total {_ic}/{len(selections)} {_jc}/{_ljc})")
                            await self.MUSIC.add_track(Track(webpage_url=j))
                            _jc += 1

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
