from .baseCommand import BaseCommand

import discord
import os
import urllib.request

class StructureCommand(BaseCommand):
    command_text = "!!structure"

    def __init__(self, bot, command_cache, structure_folder):
        super().__init__(bot, command_cache)

        self.structure_folder = structure_folder

    def help(self):
        return '`' + self.command_text + ' <file[ATTACHED]>`  **-**  Uploads structure file to creative\n'

    async def process(self, message, args):
        attachment = message.attachments[0]

        filename = attachment['filename']
        filesize = attachment['size']
        url = attachment['url']

        _, extension = os.path.splitext(filename)

        if extension.casefold() == '.nbt':
            req = urllib.request.Request(url, headers = { 'User-Agent': 'Mozilla/5.0' })
            response = urllib.request.urlopen(req)
            response = response.read()
            
            with open(os.path.join(self.structure_folder, filename), 'wb') as f:
                f.write(response)

            em = discord.Embed(
                description = 'Filename: ' + filename,
                colour = 0x003763)

            em.set_author(name = 'Structure file uploaded', icon_url = 'https://cdn.discordapp.com/icons/336592624624336896/31615259cca237257e3204767959a967.png')
            em.set_footer(text = 'Filesize: ' + str(round(filesize / 1000, 2)) + 'KB')

            await self.bot.send_message(message.channel, embed = em)
        else:
            await self.bot.send_message(message.channel, 'No nbt file detected')
