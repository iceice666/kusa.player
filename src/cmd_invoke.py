class Command:
    def __init__(self, core):
        self.commands = core()

    def cmd_help(self):
        self.commands.cmd_help(self)

    async def cmd_play(self, cmd_args):
        await self.commands.cmd_play(cmd_args)

    def cmd_volume(self, cmd_args):
        self.commands.cmd_volume(cmd_args)

    def cmd_nowplaying(self):
        self.commands.cmd_nowplaying()

    def cmd_queue(self):
        self.commands.cmd_queue()

    def cmd_skip(self):
        self.commands.cmd_skip()

    def cmd_clear(self):
        self.commands.cmd_clear()

    def cmd_stop(self, ):
        self.commands.cmd_stop()

    def cmd_pause(self, ):
        self.commands.cmd_pause()

    def cmd_resume(self, ):
        self.commands.cmd_resume()

    def cmd_loop(self, ):
        self.commands.cmd_loop()

    def cmd_repeat(self, ):
        self.commands.cmd_repeat()

    def cmd_position(self, cmd_args):
        self.commands.cmd_position(cmd_args)

    async def cmd_search(self, cmd_args):
        await self.commands.cmd_search(cmd_args)

    def cmd_save(self, cmd_args):
        self.commands.cmd_save(cmd_args)

    async def cmd_quickplay(self, cmd_args):
        await self.commands.cmd_quickplay(cmd_args)

    def exit_(self, ):
        self.commands.exit_()

    def unknown_cmd(self, ):
        self.commands.unknown_cmd()

    async def ask(self):
        return self.commands.ask()
