from email import message
import sys
import asyncio
import aioconsole
from rich import Console
from src.Music import Player
from InquirerPy import inquirer


class Interface:

    async def cmd_invoke(self, cmd_args):
        if not cmd_args:
            return await self.MUSIC.help_cmd()
        try:
            match cmd_args.pop(0):

                case 'exit':
                    sys.exit(0)
                case 'exec':
                    await self.MUSIC.execute(cmd_args)
                case 'checkrl':
                    print(asyncio.all_tasks(asyncio.get_running_loop()))
                case 'play' | 'p':
                    for uri in cmd_args:
                        await self.MUSIC.add_track(uri)
                        if not self.MUSIC.player.is_playing():
                            await self.MUSIC.play()
                case 'vol' | 'volume':
                    await self.MUSIC.volume(int(cmd_args[0]) if cmd_args else None)
                case 'queue':
                    await self.MUSIC.queue()
                case 'skip':
                    await self.MUSIC.skip()
                case 'clear':
                    await self.MUSIC.clear()
                case 'stop':
                    await self.MUSIC.clear()
                    await self.MUSIC.skip()
                case 'pause' | 'pa':
                    await self.MUSIC.pause()
                case 'resume' | 're':
                    await self.MUSIC.resume()
                case 'nowplaying' | 'np':
                    pass
                case 'loop':
                    await self.MUSIC.loop()
                case 'repeat':
                    await self.MUSIC.repeat()
                case 'pos' | 'position':
                    await self.MUSIC.position(float(cmd_args[0]) if cmd_args else None)
                case '':
                    pass
                case _:
                    print('Unknow command: ')

        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"\n{e}")

    async def entrypoint(self):
        self.MUSIC = Player()
        self.console=Console()
        while True:
            command = await inquirer.text(message="Music >").execute_async()
            await asyncio.gather(self.cmd_invoke(command.split(" ")))

    def run(self):
        asyncio.run(self.entrypoint())
        asyncio.get_running_loop().run_forever()
