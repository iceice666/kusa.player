
from lib.CPD.cpd import *


def help_(): print('help')
def tp(player): print(f'tp {player}')
def tpp(x, y, z): print(f"tp to {x} {y} {z}")


cmd = Dispatcher()
cmd\
    .register(
        Command('tp')
        .option(Arguments().execute(help_))
        .option(Arguments(('name', str),).execute(tp))
        .option(Arguments(('x', int), ('y', int), ('z', int),).execute(tpp))
    )\
    .register(
        Command('kill')
        .option(Arguments().execute())
        .option(Arguments(('entity', str).execute()))
    )


# test
cmd.execute('tp')  # except 'help'
cmd.execute('tp 0 0 0')  # except 'tp to 0 0 0'
cmd.execute('tp noob')  # except 'tp noob'
cmd.execute('giya')  # except  None

cmd.execute('kill')  # except 'You killed your self'
cmd.execute('kill noob')  # except 'You killed a Noob'
