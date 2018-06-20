class BaseCommand(object):
    """Base class for commands"""

    def __init__(self, bot, command_cache):
        # cache of information available to all commands
        self.cache = command_cache

        # needed for send_message()
        self.bot = bot

    async def process(self, message, args):
        pass

    async def load_files(self):
        pass

    def help(self):
        pass
