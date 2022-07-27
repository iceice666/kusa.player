
# A command line parser and dispatcher

import asyncio
from typing import Optional

class Root:
    def __init__(self,name):
        self.command_map={}

    def add_option(self,name,callback:callable,alias:Optional[list|tuple]):
        self.command_map[name] = callback()