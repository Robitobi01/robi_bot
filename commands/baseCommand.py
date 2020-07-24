# Base class for commands
class BaseCommand(object):

    def __init__(self, client, command_cache):
        # cache of information available to all commands
        self.cache = command_cache

        # needed for send_message()
        self.client = client

    async def process(self, message, args):
        pass

    async def load_files(self):
        pass

    def help(self):
        pass
