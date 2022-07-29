
# A command line parser and dispatcher

import asyncio
import functools
from typing import *


class ArgumentError(Exception):
    pass


# A command collection
class Root:
    command_map = {}

    def __init__(self, name):
        self.name = name

    def add_cmd(self, *cmds: List['Command']):
        for cmd in cmds:
            c = cmd()
            self.command_map[c.name] = c

    def spliter(self, input: str,): return input.split(" ")

    def dispatcher(self, input):
        cmd_args = self.spliter(input)
        self.command_map[cmd_args.pop(0)]._dispatcher(
            {'args': cmd_args, 'raw': input})


class Command:
    args = []

    def __init__(self, name: str, callback: Callable or Coroutine, description=""):
        self.name = name
        self.callback = callback
        self.description = description

    def _run(self, *args, **kwargs):
        if isinstance(self.callback, callable):
            self.callback(*args, **kwargs)
        elif asyncio.iscoroutinefunction(self.callback):
            asyncio.gather(functools.partial(self.callback, *args, **kwargs))
        elif asyncio.iscoroutine(self.callback):
            asyncio.gather(self.callback)

    def _dispatcher(self, context):
        if self.args:
            for i, arg in enumerate(context['args']):
                if not self.args[i].passing(arg):
                    raise ArgumentError(
                        f"Invalid argument {arg} passed, except {self.args[i].type} ({self.args[i].name})")

        self._run(*context['args'])

    def add_argument(self, *args: List['Argument']):
        self.args.append(*args)
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

    def is_boolean(self, s: str) -> bool:
        return True if s.lower() in ['false', 'true'] else False

    def is_string(self, s: str) -> bool:
        return True if isinstance(input, str) else False

    def passing(self, input):
        # integer
        if self.is_integer(input):
            return True
        # float
        if self.is_float(input):
            return True
        # string
        if self.is_string(input):
            return True
        # boolean
        if self.is_boolean(input):
            return True
