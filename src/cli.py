import asyncio
import atexit
import sys

import InquirerPy
from InquirerPy import inquirer
from prompt_toolkit.application import in_terminal
from rich.console import Console

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

    async def dispatch(self, cmd_args):
        if not cmd_args:
            return await self.MUSIC.help_cmd()
        try:
            match cmd_args.pop(0).lower():

                # Music player command
                case 'play' | 'p':
                    if not cmd_args: return
                    for uri in cmd_args:
                        if uri == '':
                            continue

                        await self.MUSIC.add_track(uri)
                        self.console.print(
                            f'[Player] Add Track: Parsing uri {uri}')

                        if not self.MUSIC.player.is_playing():
                            await self.MUSIC.play()

                case 'vol' | 'volume':
                    if not cmd_args:  # cmd_args is []
                        self.console.print(f"[Player] Volume: {await self.MUSIC.volume(None)}")
                        return
                    else:
                        vol = int(cmd_args[0])
                        prev_vol = await self.MUSIC.volume()
                        if vol > 0:
                            await self.MUSIC.volume(vol)
                            self.console.print(
                                f"[Player] Volume: {prev_vol} => {vol}")
                        else:
                            self.console.print(f"[Player] Volume: {await self.MUSIC.volume(None)}")
                            return

                case 'nowplaying' | 'np':
                    self.console.print(self.MUSIC.nowplaying)

                case 'queue':
                    self.console.print("[Player] Queue \n")
                    self.console.print(self.MUSIC.playlist)

                case 'skip':
                    await self.MUSIC.skip()

                case 'clear':
                    await self.MUSIC.clear()

                case 'stop':
                    await self.MUSIC.clear()
                    await self.MUSIC.skip()

                case 'pause' | 'pa':
                    self.console.print('[Player] Paused')
                    await self.MUSIC.pause()

                case 'resume' | 're':
                    self.console.print('[Player] Resumed')
                    await self.MUSIC.resume()

                case 'loop':
                    await self.MUSIC.loop()
                    self.console.print(
                        '[Player] Now player [red bold]will{}[/red bold]loop the queue.'.format(
                            " " if self.MUSIC.flag_loop else " not "))

                case 'repeat':
                    await self.MUSIC.repeat()
                    self.console.print(
                        '[Player] Now player [red bold]will{}[/red bold]repeat the song which is playing.'.format(
                            "" if self.MUSIC.flag_repeat else " not "))

                case 'pos' | 'position':
                    pos = float(cmd_args[0])
                    if pos is None:
                        print(
                            "[Player] Position {}s / {}s ({}%)".format(
                                int(self.MUSIC.player.get_time() / 1000),
                                int(self.MUSIC.player.get_length() / 1000),
                                int(self.MUSIC.player.get_position() * 100)
                            ))
                    else:
                        await self.MUSIC.position(pos)

                case 's' | 'search':
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
                case '_checkrl':
                    print(asyncio.all_tasks(asyncio.get_running_loop()))
                case '':
                    pass
                case _:
                    async with in_terminal():
                        self.console.print('Unknown command')

        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"\n{e}")

    async def entrypoint(self):
        self.console = Console()
        self.MUSIC = Player()

        while True:
            command = str(await inquirer.text(message="Music >", amark="", style=self._default_color).execute_async())
            await asyncio.gather(self.dispatch(command.split(" ")))

    def run(self):
        atexit.register(lambda: self.console.print('Bye~ Have a great day~'))
        try:
            asyncio.run(self.entrypoint())
            asyncio.get_running_loop().run_forever()
        except KeyboardInterrupt:
            sys.exit(0)
