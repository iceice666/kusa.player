import asyncio
import atexit
import sys
from typing import Optional

import InquirerPy
import urllib3
from InquirerPy import inquirer
from InquirerPy.base import Choice
from prompt_toolkit.application import in_terminal
from rich.console import Console
from rich.markdown import Markdown
from rich.style import Style

from CONFIG import help_md
from src.Music import Player, Search


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

    def __init__(self):
        pass

    async def dispatch(self, cmd_args):
        if not cmd_args:
            return await self.MUSIC.help_cmd()

        match cmd_args.pop(0).lower():
            case 'help' | 'h':
                self.console.print(Markdown(help_md, ))

            # Music player command
            case 'play' | 'p':
                if not cmd_args:
                    if not self.MUSIC.player.is_playing():
                        return await self.MUSIC.play()

                with self.console.status(f"[light green]Fetching data...(Total {len(cmd_args)})") as status:
                    for url in cmd_args:
                        if url == '':
                            continue

                        parse = urllib3.util.parse_url(url)
                        if parse.host.lower() == "www.bilibili.com":
                            await self.MUSIC.add_track(webpage_url=url, website='bilibili')
                        elif parse.host.lower() in ['www.youtube.com', 'youtu.be']:
                            await self.MUSIC.add_track(webpage_url=url, website='youtube')
                        else:
                            await self.MUSIC.add_track(webpage_url=url)

                    self.console.print('[Console] Added all requested urls')

                if not self.MUSIC.player.is_playing():
                    return await self.MUSIC.play()

            case 'vol' | 'volume':
                if not cmd_args:
                    self.console.print(f"[Console] Volume: {await self.MUSIC.volume(None)}")
                    return
                else:
                    vol = int(cmd_args[0])
                    prev_vol = await self.MUSIC.volume()
                    if vol > 0:
                        await self.MUSIC.volume(vol)
                        self.console.print(
                            f"[Console] Volume: {prev_vol} => {vol}")
                    else:
                        self.console.print(f"[Console] Volume: {await self.MUSIC.volume(None)}")
                        return

            case 'nowplaying' | 'np':
                np = self.MUSIC.nowplaying
                self.console.print('[Console] Nowplaying:')
                if np["website"].lower() == 'bilibili':
                    line1 = f'[blue]Bilibili @ {np["author"]}[/blue]'
                elif np["website"].lower() == 'youtube':
                    line1 = f'[red]Youtube @ {np["author"]}[/red]'
                else:
                    line1 = f'{np["website"]} @ {np["author"]}'

                self.console.print(line1, )
                self.console.print(np['title'], style=Style(color='#D670B3'))
                self.console.print(np['webpage_url'], style=Style(color='blue', underline=True))

            case 'queue' | 'q':
                self.console.print("[Console] Queue")
                for n, i in enumerate(self.MUSIC.playlist):
                    if i["website"].lower() == 'bilibili':
                        line1 = f'[blue]Bilibili @ {i["author"]}[/blue]'
                    elif i["website"].lower() == 'youtube':
                        line1 = f'[red]Youtube @ {i["author"]}[/red]'
                    else:
                        line1 = f'{i["website"]} @ {i["author"]}'

                    self.console.print(f'{n}. {line1}')
                    self.console.print(f'{i["title"]}', style=Style(color='#D670B3'))
                    self.console.print(i['webpage_url'], style=Style(color='blue', underline=True))

            case 'skip' | 'sk':
                await self.MUSIC.skip()

            case 'clear' | 'c':
                await self.MUSIC.clear()

            case 'stop' | 'st':
                await self.MUSIC.clear()
                await self.MUSIC.skip()

            case 'pause' | 'pa':
                self.console.print('[Console] Paused')
                await self.MUSIC.pause()

            case 'resume' | 're':
                self.console.print('[Console] Resumed')
                await self.MUSIC.resume()

            case 'loop' | 'l':
                await self.MUSIC.loop()
                self.console.print(
                    '[Console] Now player [red bold]will {}[/red bold] loop the queue.'.format(
                        "" if self.MUSIC.flag_loop else "not"))

            case 'repeat' | 'r':
                await self.MUSIC.repeat()
                self.console.print(
                    '[Console] Now player [red bold]will {}[/red bold] repeat the song which is playing.'.format(
                        "" if self.MUSIC.flag_repeat else "not"))

            case 'position' | 'pos':
                if not cmd_args:
                    print(
                        "[Console] Position {}s / {}s ({}%)".format(
                            int(self.MUSIC.player.get_time() / 1000),
                            int(self.MUSIC.player.get_length() / 1000),
                            int(self.MUSIC.player.get_position() * 100)
                        ))
                else:
                    await self.MUSIC.position(float(cmd_args[0]))

            case 's' | 'search':
                # init
                b = False
                y = True
                keyword = ''
                choices: list[Choice] = [Choice('Cancel', enabled=True)]
                fetch_result = {}

                if '-y' in cmd_args or '-yt' in cmd_args or '--youtube' in cmd_args:
                    y = True
                elif '-b' in cmd_args or '--bilibili' in cmd_args:
                    b = True

                for i in cmd_args:
                    if i.startswith('-'):
                        continue
                    else:
                        keyword += i + ' '

                if b:
                    fetch_result = await Search.bilibili(keyword)
                elif y:
                    fetch_result = await Search.youtube(keyword)

                for n, info in enumerate(fetch_result):
                    if info["website"].lower() == 'bilibili':
                        url = f'https://www.bilibili.com/video/{info["vid_id"]}'
                    elif info["website"].lower() == 'youtube':
                        url = f'https://youtu.be/{info["vid_id"]}'

                    choices.append(
                        Choice(name=f'{info["title"]}\n         {url}', value=n))

                selections: Optional[list] = await inquirer.checkbox(message=f'Select one > (Press Space to select and press Enter to enter.)',
                                                                     choices=choices,
                                                                     raise_keyboard_interrupt=False,
                                                                     mandatory=False, ).execute_async()

                if (selections == 'Cancel' and len(selections) == 1) or selections is None:
                    return self.console.print('Selection cancelled.')

                with self.console.status(f"[light green]Fetching data...(Total {len(selections)})") as status:
                    for s in selections:
                        if s == 'Cancel':
                            continue
                        selection = fetch_result[s]
                        await self.MUSIC.add_track(vid_id=selection["vid_id"], website=selection['website'])

                    self.console.print('[Console] Added all searched results')

                if not self.MUSIC.nowplaying:
                    await self.MUSIC.play()

            case 'sa' | 'save':
                pass
            # exit
            case 'exit':
                sys.exit(0)

            # for debug commands
            case '_exec':
                for cmd in cmd_args:
                    exec(cmd)
            case '_music_exec':
                await self.MUSIC.execute(cmd_args)
            case '':
                pass
            case _:
                async with in_terminal():
                    self.console.print('Unknown command')

    async def entrypoint(self):
        atexit.register(lambda: self.console.print(
            'Thanks for using kusa! :partying_face: \n:party_popper: Bye~ Have a great day~ :party_popper:'))

        asyncio.get_running_loop()  # checking is there an event loop running

        self.console = Console()
        self.MUSIC = Player(rich_console=self.console)

        while True:
            try:
                command = (str(await inquirer.text(
                    message="Music >",
                    amark="", style=self._default_color,
                    raise_keyboard_interrupt=False,
                    mandatory=True, mandatory_message='If you want to close the music player, type "exit" to do.'
                ).execute_async()))
                await asyncio.gather(self.dispatch(command.split(" ")))

            except Exception as e:
                print(f"\n{e}")
