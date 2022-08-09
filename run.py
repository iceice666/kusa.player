
import asyncio


async def main():
    from src.main import Interface
    await Interface().entrypoint()


try:
    asyncio.run(main())
except:
    pass
