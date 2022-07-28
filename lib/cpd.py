
# A command line parser and dispatcher

import asyncio
import functools
from typing import *


class Root:
    def __init__(self, name):
        self.name = name
        self.command_map = []

    def add_cmd(self, cmd: 'Command'):
        self.command_map.append(cmd)


class Command:
    def __init__(self, name: str, callback: Callable or Coroutine):
        self.name = name
        self.callback = callback

    def _dsipatch(self, *args, **kwargs):
        if isinstance(self.callback, callable):
            self.callback(*args, **kwargs)
        elif asyncio.iscoroutinefunction(self.callback):
            asyncio.gather(functools.partial(self.callback, *args, **kwargs))
        elif asyncio.iscoroutine(self.callback):
            asyncio.gather(self.callback)

    def add_argument(self, arg: 'Argument'):
        return self


class Argument:
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def is_integer(self, s: str) -> bool:
        try:
            int(s)
        except:
            return False
        return True

    def is_float(self, s: str) -> bool:
        if s.lower() in ["nan", "infinity"]:
            return False
        try:
            float(s)
            return True
        except ValueError:
            return False

    def passing(self, input):
        # integer
        if (type in ['int', 'integer'] or isinstance(input, int)) and self.is_integer(input):
            return True
        # float
        elif (type in ['float', ] or isinstance(input, float)) and self.is_integer(input):
            return True
