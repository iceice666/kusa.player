import asyncio
import atexit
import sys

import InquirerPy
from InquirerPy import inquirer
from InquirerPy.base import Choice
from prompt_toolkit.application import in_terminal
from rich.console import Console

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

    def __init__(self):
        pass

    async def dispatch(self, cmd_args):
        if not cmd_args:
            return await self.MUSIC.help_cmd()

        match cmd_args.pop(0).lower():

            # Music player command
            case 'play' | 'p':
                if not cmd_args:
                    return
                for uri in cmd_args:
                    if uri == '':
                        continue

                    await self.MUSIC.add_track(uri)
                    self.console.print(
                        f'[Console] Add Track: Parsing uri {uri}')

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
                self.console.print(self.MUSIC.nowplaying)

            case 'queue' | 'q':
                self.console.print("[Console] Queue \n")
                self.console.print(self.MUSIC.playlist)

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
                    '[Console] Now player [red bold]will{}[/red bold] loop the queue.'.format(
                        " " if self.MUSIC.flag_loop else " not"))

            case 'repeat' | 'r':
                await self.MUSIC.repeat()
                self.console.print(
                    '[Console] Now player [red bold]will{}[/red bold] repeat the song which is playing.'.format(
                        "" if self.MUSIC.flag_repeat else " not"))

            case  'position' | 'pos':
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

                for i in cmd_args:
                    if i.startswith('-'):
                        match i.split('-')[-1].lower():
                            case 'b' | 'bili' | 'bilibili':
                                b = True
                            case 'y' | 'yt' | 'youtube':
                                y = True
                    else:
                        keyword = keyword + i + ' '
                if keyword is None:
                    return
                elif b:
                    fetch_result = await Search.bilibili(keyword)
                elif y:
                    fetch_result = await Search.youtube(keyword)

                for i in fetch_result:
                    choices.append(Choice(i))

                selection = await inquirer.select(message=f'Select one > ', choices=choices, raise_keyboard_interrupt=False,
                                                  mandatory=False).execute_async()
                if selection == 'Cancel' or selection is None:
                    return self.console.print('Selection cancelled.')
                selection = fetch_result[selection]
                await self.MUSIC.add_track(vid_id=selection["vidId"], website=selection['platform'])

            case 'sa' | 'song_alias' | 'songalias':
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
        self.MUSIC = Player()

        while True:
            try:
                command = str(await inquirer.text(
                    message="Music >", amark="", style=self._default_color,
                    raise_keyboard_interrupt=False,
                    mandatory=True, mandatory_message='If you want to close the music player, type "exit" to do.'
                ).execute_async())
                await asyncio.gather(self.dispatch(command.split(" ")))
            except Exception as e:
                print(f"\n{e}")
