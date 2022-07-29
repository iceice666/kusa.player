
from dis import dis
from brigadier import CommandDispatcher
from brigadier.builder import literal, argument
from brigadier.arguments import *


class aq:
    async def command_map(self):
        dispatcher = CommandDispatcher()
        # exit
        dispatcher.register(literal('exit').executes(lambda: sys.exit(0)))
        dispatcher.register(literal('play'))
