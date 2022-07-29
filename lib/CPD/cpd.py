
# A command line parser and dispatcher


import asyncio


from typing import *


# A command collection
class Dispatcher:
    command_map = {}

    def register(self, command: 'Command'):
        c = command()
        self.command_map[c.name] = c


class Command:
    def __init__(self, name):
        self.name = name

    def argument(self, args: 'Arguments'):
        return self

    def execute(self, callback: Callable or Coroutine):
        self.callback = callback


class Arguments:
    pass

def tp(x,y,z): return
cmd = Dispatcher()
cmd.register(Command('tp')
             .argument(Arguments(('x', int), ('y', int), ('z', int))).execute(tp)
             )
cmd.execute('tp 0 0 0')


class BaseDispatch:
    command_map = {}

    def dispatch(self, input: str):
        self.split(input)

    def split(self, input):
        return input.split(' ')

    def execute(self, ):
        pass

    def add_command(name):
        print(name)

        def inner(func):
            def warpper(self, *args, **kwargs):
                self.command_map[name] = {'callback': func, }
            return warpper
        return inner

    @add_command('test')
    def test(self): pass


type('Dispatcher', (), {})
