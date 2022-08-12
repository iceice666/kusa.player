# vlc-player functions here
import asyncio
from typing import Optional

import vlc


class VLC:
    def __init__(self, args: tuple = ("--no-ts-trust-pcr", "--ts-seek-percent", "--no-video", "-q"), ):

        self._rl = asyncio.get_running_loop()

        self.player: vlc.MediaPlayer = vlc.Instance(args).media_player_new()
        self.player.audio_set_volume(20)

        self.player.event_manager().event_attach(vlc.EventType.MediaPlayerStopped,
                                                 lambda *_: asyncio.run_coroutine_threadsafe(self._playing_end(),
                                                                                             self._rl))

    async def _playing_end(self):
        pass

    '''Should be a coroutine method'''

    def volume(self, vol: Optional[int] = None):
        if vol is None:
            pass
        else:
            self.player.audio_set_volume(vol)
        return self.player.audio_get_volume()

    def position(self, pos: int | float):
        if 1 > pos >= 0:
            self.player.set_position(pos)
        elif 1 <= pos < self.player.get_length():
            self.player.set_position(pos / self.player.get_length())

    def skip(self):
        self.player.stop()

    def pause(self):
        self.player.set_pause(1)

    def resume(self):
        self.player.set_pause(0)

    def set_uri(self, uri):
        self.player.set_media(
            self.player.get_instance().media_new(uri))

    def play(self):
        self.player.play()

    def get_time(self):
        return self.player.get_time()

    def get_length(self):
        return self.player.get_length()

    def get_position(self):
        return self.player.get_position()

    def is_playing(self):
        return self.player.is_playing()

    def stop(self):
        self.player.stop()
