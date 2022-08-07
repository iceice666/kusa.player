import asyncio

from src.cli import Interface

try:
    asyncio.run(Interface().entrypoint())
    asyncio.get_running_loop().run_forever()
except:
    pass


