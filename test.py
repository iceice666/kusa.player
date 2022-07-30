
from GIYA import *


def help_(): print('help')
def tp(player): print(f'tp {player}')
def tpp(x, y, z): print(f"tp to {x} {y} {z}")


cmd = Dispatcher()


cmd.register(Command('tp', 'teleport')
             .argument([], help_)
             .argument([str, ], tp)
             .argument([int, int, int], tpp))\
    .register(Command('kill')
              .argument([], (lambda *_: print('You killed your self')))
              .argument([str],
                        (lambda *_: print(f'You killed a Noob'))))


# test
cmd.execute('tp')  # except 'help'
cmd.execute('tp 0 0 0')  # except 'tp to 0 0 0'
cmd.execute('teleport noob')  # except 'tp noob'
cmd.execute('giya')  # except

cmd.execute('kill')  # except
cmd.execute('kill noob')
