import asyncio
import importlib
import sys
from time import sleep


async def main():
    interface = importlib.import_module('.interface', 'src.CLI')
    await interface.Interface().entrypoint()
    return


asyncio.run(main())

# loop = asyncio.new_event_loop()
# loop.run_until_complete(main())

sleep(3)

sys.exit(0)
