import asyncio
import atexit

from rich.traceback import install

from src.cli.Music import Commands
from .cmd_invoke import Command

install(show_locals=True)


class Exit(Exception):
    pass


class Interface:
    # https://inquirerpy.readthedocs.io/en/latest/pages/style.html

    interface = Command(Commands)

    async def dispatch(self, cmd_args):
        if not cmd_args:
            return self.interface.cmd_help()

        match cmd_args.pop(0):
            case 'help' | 'h':
                self.interface.cmd_help()

            # Music player command
            case 'play' | 'p':
                await self.interface.cmd_play(cmd_args)

            case 'vol' | 'volume':
                self.interface.cmd_volume(cmd_args)

            case 'nowplaying' | 'np':
                self.interface.cmd_nowplaying()

            case 'queue' | 'q':
                self.interface.cmd_queue()

            case 'skip' | 'sk':
                self.interface.cmd_skip()

            case 'clear' | 'c':
                self.interface.cmd_clear()

            case 'stop' | 'st':
                self.interface.cmd_stop()

            case 'pause' | 'pa':
                self.interface.cmd_pause()

            case 'resume' | 're':
                self.interface.cmd_resume()

            case 'loop' | 'l':
                self.interface.cmd_loop()

            case 'repeat' | 'r':
                self.interface.cmd_repeat()

            case 'position' | 'pos':
                self.interface.cmd_position(cmd_args)

            case 's' | 'search':
                await self.interface.cmd_search(cmd_args)

            case 'sa' | 'save':
                self.interface.cmd_save(cmd_args)

            case 'quickplay' | 'qp':
                await self.interface.cmd_quickplay(cmd_args)

            # exit
            case 'exit':
                self.interface.exit_()
                raise Exit()

            case '':
                pass
            case _:
                self.interface.unknown_cmd()

    def exit(self):
        pass

    async def entrypoint(self):

        atexit.register(self.exit)

        while True:
            try:
                command = await self.interface.ask()
                await asyncio.gather(self.dispatch(command.split(" ")))

            except Exit:
                break

            except:
                pass
