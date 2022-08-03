import asyncio

from src.cli import Interface


asyncio.run(Interface().entrypoint())
asyncio.get_running_loop().run_forever()
