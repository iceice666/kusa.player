import asyncio

import InquirerPy
from InquirerPy import inquirer

from .commands import Commands
from .core import console


class Exit(Exception):
    pass


class Interface:
    # https://inquirerpy.readthedocs.io/en/latest/pages/style.html

    commands = Commands()

    async def dispatch(self, cmd_args):
        if not cmd_args:
            return self.commands.cmd_help()

        match cmd_args.pop(0):
            case 'help' | 'h':
                self.commands.cmd_help()

            # Music player command
            case 'play' | 'p':
                await self.commands.cmd_play(cmd_args)

            case 'vol' | 'volume':
                self.commands.cmd_volume(cmd_args)

            case 'nowplaying' | 'np':
                self.commands.cmd_nowplaying()

            case 'queue' | 'q':
                self.commands.cmd_queue()

            case 'skip' | 'sk':
                self.commands.cmd_skip()

            case 'clear' | 'c':
                self.commands.cmd_clear()

            case 'stop' | 'st':
                self.commands.cmd_stop()

            case 'pause' | 'pa':
                self.commands.cmd_pause()

            case 'resume' | 're':
                self.commands.cmd_resume()

            case 'loop' | 'l':
                self.commands.cmd_loop()

            case 'repeat' | 'r':
                self.commands.cmd_repeat()

            case 'position' | 'pos':
                self.commands.cmd_position(cmd_args)

            case 's' | 'search':
                await self.commands.cmd_search(cmd_args)

            case 'sa' | 'save':
                self.commands.cmd_save(cmd_args)

            case 'quickplay' | 'qp':
                await self.commands.cmd_quickplay(cmd_args)

            case 'exit':
                self.commands.cmd_stop()
                self.commands.cmd_exit()
                raise Exit

            case '':
                pass

            case _:
                await self.commands.unknown_cmd()

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

    async def entrypoint(self):

        while True:
            try:
                command = (str(await inquirer.text(
                    message="Music >",
                    amark="", style=self._default_color,
                    raise_keyboard_interrupt=False,
                    mandatory=True, mandatory_message='If you want to close the music player, type "exit" to do.'
                ).execute_async()))

                await asyncio.gather(self.dispatch(command.split(" ")))

            except Exit:
                break

            except BaseException as e:
                console.print_exception(show_locals=True)
