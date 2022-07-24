from Music import music
import asyncio
import aioconsole


async def main():
    player = music()
    await player.add_track(
        "https://www.youtube.com/watch?v=e97w-GHsRMY")

    #await player.play()
    await aioconsole.ainput()

asyncio.run(main())
