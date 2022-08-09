import asyncio

from src.cli import Interface

try:
    asyncio.run(Interface().entrypoint())
except:
    pass


