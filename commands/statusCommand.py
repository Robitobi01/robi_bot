import urllib.request

from .baseCommand import BaseCommand
from utils import *


class StatusCommand(BaseCommand):
    command_text = "!!status"

    def __init__(self, client, command_cache):
        super().__init__(client, command_cache)

    def help(self):
        return '`' + self.command_text + '`  **-**  Displays the current status of the Mojang services\n'

    async def process(self, message, args):
        api_url = 'https://status.mojang.com/check'
        api_request = urllib.request.urlopen(urllib.request.Request(api_url)).read()
        api_request = json.loads(api_request.decode("utf-8"))
        status = dict()
        for items in api_request:
            for key, value in items.items():
                if value == 'green': value = ':white_check_mark:'
                if value == 'yellow': value = ':warning:'
                if value == 'red': value = ':x:'
                status[key] = value
        em = generate_embed_table(
            list(status.keys()),
            list(status.values()))
        em.set_author(
            name='Mojang Status',
            icon_url='https://cdn.discordapp.com/icons/336592624624336896/31615259cca237257e3204767959a967.png')
        await message.channel.send(embed=em)
