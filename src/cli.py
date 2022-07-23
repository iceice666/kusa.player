
import asyncio
from Music import Player
import aioconsole


class cli:
    command_map=[]


    def registrar(self,*func):

        self.command_map[type(func).__name__] = func()

    async def invoke(self,cmd_args):
        func=self.command_map[(cmd_args.pop())]
        await func.invoke(cmd_args)

    async def entrypoint(self):
        while True:
            command=await aioconsole.ainput()
            try:
                asyncio.gather(self.invoke(command.split('')))
            except KeyboardInterrupt:
                asyncio.get_event_loop().close()
                break
            except:
                pass

    asyncio.run(entrypoint())
