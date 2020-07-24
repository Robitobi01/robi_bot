import time
import discord

from .baseCommand import BaseCommand
from .commandCache import CommandCache


class ReloadCommand(BaseCommand):
    command_text = "!!reload"

    def __init__(self, client, command_cache, commands, stat_folder):
        super().__init__(client, command_cache)

        self.commands = commands
        self.stat_folder = stat_folder

    def help(self):
        return '`' + self.command_text + '`  **-**  Reloads all files`[A]`\n'

    async def load_files(self):
        # refresh the cache available to all commands
        await self.cache.load_files()

        # refresh command specific information
        for k, v in self.commands.items():
            if k != self.command_text:
                await v.load_files()

    async def process(self, message, args, force_reload=False):
        async with CommandCache.semaphore:
            if self.client:
                if message is not None and not str(message.author.id) in self.cache.admin_list and not force_reload:
                    await message.channel.send('You dont have permissions to do that!')
                    return

        if self.client and message is not None:
            await message.channel.send('**Warning:** all files reloading, this might take a moment')
        else:
            print('Warning: all files reloading, this might take a moment')

        start_time = time.time()

        await self.load_files()

        async with CommandCache.semaphore:
            if self.client and message is not None:
                em = discord.Embed(
                    description='Reloaded: **' + str(len(self.cache.uuids)) + '** files',
                    colour=0x003763)

                em.set_author(name='File Reload',
                              icon_url='https://cdn.discordapp.com/icons/336592624624336896/31615259cca237257e3204767959a967.png')
                em.set_footer(text='Time: ' + str(round(time.time() - start_time, 2)) + 's')

                await message.channel.send(embed=em)
            else:
                print('Reloaded: ' + str(len(self.cache.uuids)) + ' files')
                print('Time: ' + str(round(time.time() - start_time, 2)) + 's')
