from Music import Player
import asyncio
import aioconsole


async def main():
    player = player()
    await player.add_track(
        "https://www.bilibili.com/video/BV1yJ411L7ip?spm_id_from=..search-card.all.click")

    # await player.play()
    await aioconsole.ainput()

asyncio.run(main())
