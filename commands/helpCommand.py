from .baseCommand import BaseCommand

from json_minify import json_minify
from mcstatus import MinecraftServer
from nbt import nbt

import json
import os

class HelpCommand(BaseCommand):
    command_text = "!!help"

    def __init__(self, discord, client, message, command_cache, commands):
        super(HelpCommand, self).__init__(discord, client, message, command_cache)

        self.commands = commands

    async def process(self, args):
        help_text = []

        for k in self.commands.keys():
            if k != self.command_text:
                help_text.append(self.commands[k].help()) 

        if self.client == None:
            print(''.join(help_text))
        else:
            em = discord.Embed(
                description = 'This bot provides general information about the Dugged server. \nThe command prefix is **!!**.\n ',
                colour = 0x003763)

            em.add_field(name = 'Commands', inline = False, value = help_text)
            em.set_author(name = 'Help',  url = 'https://twitter.com/Robitobi01', icon_url = 'https://cdn.discordapp.com/icons/336592624624336896/31615259cca237257e3204767959a967.png')
            em.set_footer(text = 'Made by Robitobi01', icon_url = 'https://pbs.twimg.com/profile_images/924434100441755649/MZOP8WK7.jpg')

            await self.client.send_message(self.message.channel, embed = em)
