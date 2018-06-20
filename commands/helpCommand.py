from .baseCommand import BaseCommand

from json_minify import json_minify
from mcstatus import MinecraftServer
from nbt import nbt

import discord
import json
import os

class HelpCommand(BaseCommand):
    command_text = "!!help"

    def __init__(self, bot, command_cache, commands):
        super().__init__(bot, command_cache)

        self.commands = commands

    async def process(self, message, args):
        help_text = []

        for k in self.commands.keys():
            if k != self.command_text:
                help_text.append(self.commands[k].help())

        help_text = ''.join(help_text)

        if self.bot:
            em = discord.Embed(
                description = 'This bot provides general information about the Dugged server. \nThe command prefix is **!!**.\n Addition `[A]` is only possible for administrators',
                colour = 0x003763)

            em.add_field(name = 'Commands', inline = False, value = help_text)
            em.set_author(name = 'Help',  url = 'https://twitter.com/Robitobi01', icon_url = 'https://cdn.discordapp.com/icons/336592624624336896/31615259cca237257e3204767959a967.png')
            em.set_footer(text = 'Made by Robitobi01', icon_url = 'https://pbs.twimg.com/profile_images/924434100441755649/MZOP8WK7.jpg')

            await self.bot.send_message(message.channel, embed = em)
        else:
            print(help_text)
