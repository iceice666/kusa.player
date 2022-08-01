import asyncio

from src.Music import Search

s = Search()


async def main():
    print(await s.bilibili('冬之花'))


asyncio.run(main())
