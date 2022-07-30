
# A command line parser and dispatcher


import asyncio
import re
from typing import *


# A command collection
class Dispatcher:
    command_mapping = {}

    def register(self, command: 'Command'):
        self.command_mapping[command.name] = command
        return self

    def execute(self, input):
        cmd_args = input.split(" ")
        _command = self.command_mapping.get(cmd_args.pop(0), None)
        if _command is not None:
            _command._execute(cmd_args)


class Arguments:
    class Checker:
        @staticmethod
        def is_integer(s: str) -> bool:
            try:
                int(s)
            except ValueError:
                return False
            return True

        @staticmethod
        def is_float(s: str) -> bool:
            if s.lower() in ["nan", "infinity"]:
                return False
            try:
                float(s)

            except ValueError:
                return False
            return True

    # tuple pass a name and type of argument

    def __init__(self, *args: List[tuple]):
        self.args = args
        self._len = len(args)

    def execute(self, callback: Callable or Coroutine):
        self.callback = callback
        return self

    def _check(self, obj, type_of_value):
        if isinstance(obj, str):
            if type_of_value is str:
                return True
            elif type_of_value is int:
                return self.Checker.is_integer(obj)
            elif type_of_value is float:
                return self.Checker.is_float(obj)

        elif isinstance(obj, type_of_value):
            return True

    def _execute(self, cmd_args: list):
        for input_arg, definition in zip(cmd_args, self.args):
            if not self._check(input_arg, definition[-1]):
                raise ValueError(f'Invalid value {input_arg}')

        self._run_func(cmd_args)

    def _run_func(self, cmd_args):
        if isinstance(self.callback, Awaitable):
            asyncio.gather(self.callback)
        elif isinstance(self.callback, Callable):
            self.callback(*cmd_args)


class Command:
    arguments_mapping = {}

    def __init__(self, name):
        self.name = name

    def option(self, arg: 'Arguments'):
        self.arguments_mapping[arg._len] = arg
        return self

    def _execute(self, cmd_args):
        self.arguments_mapping[len(cmd_args)]._execute(cmd_args)
