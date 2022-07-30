
from lib.CPD.cpd import *

def help_(): return 'help'
def tp(player): print(f'tp {player}')
def tpp(x, y, z): print(f"tp to {x} {y} {z}")

cmd = Dispatcher()
cmd.register(Command('tp')
             .passing(Arguments().execute(help_))
             .passing(Arguments(('name', str),).execute(tp))
             .passing(Arguments(('x', int), ('y', int), ('z', int),).execute(tpp))
             )

# test
cmd.execute('tp')      #except 'help'
cmd.execute('tp 0 0 0')  #except 'tp to 0 0 0'
cmd.execute('tp noob')   #except 'tp noob'
cmd.execute('giya')      #except  None