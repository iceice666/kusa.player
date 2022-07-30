
# A command line parser and dispatcher


import asyncio
from typing import *


# A command collection
class Dispatcher:
    command_mapping = {}

    def register(self, command: 'Command'):
        self.command_mapping[command.name] = command

    def execute(self,input):
        cmd_args=input.split(" ")
        _command=self.command_mapping.get(cmd_args.pop(0),None)
        if _command is not None:
            _command._execute(cmd_args)


class Arguments:
    # tuple pass a name and type of argument
    def __init__(self, *args: List[tuple] ):
        self.args = args
        self._len=len(args)

    def execute(self, callback: Callable or Coroutine):
        self.callback = callback
        return self

    def _check(self,obj_1,obj_2):
        return True

    def _execute(self, cmd_args: list):
        for input_arg, definition in zip(cmd_args, self.args):
            self._check(input_arg, definition)

        self._run_func(cmd_args)

    def _run_func(self,cmd_args):
        if isinstance(self.callback, Awaitable):
            asyncio.gather(self.callback)
        elif isinstance(self.callback, Callable):
            self.callback(*cmd_args)



class Command:
    arguments_mapping={}
    def __init__(self, name):
        self.name = name

    def passing(self, arg: 'Arguments'):
        self.arguments_mapping[arg._len]=arg
        return self

    def _execute(self,cmd_args):
        self.arguments_mapping[len(cmd_args)]._execute(cmd_args)




