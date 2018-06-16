from .baseCommand import BaseCommand
from .commandCache import CommandCache

from utils import *

import time

class ReloadCommand(BaseCommand):
    command_text = "!!reload"

    def __init__(self, discord, client, message, command_cache, commands, stat_folder):
        super().__init__(discord, client, message, command_cache)

        self.commands = commands
        self.stat_folder = stat_folder

    def help(self):
        return '`' + self.command_text + '`  **-**  Displays currently online players and their dimension\n'
    
    async def load_files(self):
        # refresh the cache available to all commands
        await self.cache.load_files()

        # refresh command specific information
        for k, v in self.commands.items():
            if k != self.command_text:
                await v.load_files()

    async def process(self, args):
        if self.client == None:
            print('**Warning:** all files reloading, this might take a moment')
        else:
            await self.client.send_message(self.message.channel, '**Warning:** all files reloading, this might take a moment')

        start_time = time.time()

        await self.load_files()

        async with CommandCache.semaphore:
            if self.client == None:
                print('Reloaded: **' + str(len(self.cache.uuids)) + '** files')
                print('Time: ' + str(round(time.time() - start_time, 2)) + 's')
            else:
                em = discord.Embed(
                    description = 'Reloaded: **' + str(len(self.cache.uuids)) + '** files', 
                    colour = 0x003763)

                em.set_author(name = 'File Reload', icon_url = 'https://cdn.discordapp.com/icons/336592624624336896/31615259cca237257e3204767959a967.png')
                em.set_footer(text = 'Time: ' + str(round(time.time() - start_time, 2)) + 's')

                await self.client.send_message(self.message.channel, embed = em)
