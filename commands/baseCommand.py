class BaseCommand(object):
    """Base class for commands"""

    def __init__(self, discord, client, message, command_cache):
        # cache of information available to all commands
        self.cache = command_cache
        # needed for embed()
        self.discord = discord
        # needed for send_message()
        self.client = client
        # needed for channel and attachments
        self.message = message

    async def process(self, args):
        pass

    async def load_files(self):
        pass

    def help(self):
        pass
