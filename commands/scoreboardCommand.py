from .baseCommand import BaseCommand
from .commandCache import CommandCache

from utils import *

from difflib import get_close_matches
from nbt import nbt

import discord
import os

class ScoreboardCommand(BaseCommand):
    command_text = "!!scoreboard"

    def __init__(self, bot, command_cache, data_folder):
        super().__init__(bot, command_cache)

        self.data_folder = data_folder

    def help(self):
        return '`' + self.command_text + ' <scoreboard_name>`  **-**  Displays scoreboard\n'

    async def process(self, message, args):
        if len(args) == 1:
            nbt_file = nbt.NBTFile(os.path.join(self.data_folder, 'scoreboard.dat'))
            scoreboard_objectives = [tag["Name"].value.casefold() for tag in nbt_file['data']['Objectives']]
            objective_name = ''.join(get_close_matches(args[0], scoreboard_objectives, 1))

            if objective_name != '':
                scoreboard = dict()
                
                for tag in nbt_file["data"]["PlayerScores"]:
                    if tag["Objective"].value.casefold() == objective_name:
                        scoreboard[tag["Name"].value] = tag["Score"].value

                scoreboard = sorted(scoreboard.items(), key = lambda x:x[1], reverse = True)

                text1 = []
                text2 = []
                total = 0

                for name, amount in scoreboard:
                    if not name == 'Total':
                        text1.append(formatNameForEmbed(name))
                        text2.append(str(amount))
                        total += amount

                if self.bot:
                    em = discord.Embed(
                        description = '',
                        colour = 0x003763)

                    em.add_field(name = 'Players',
                        inline = True,
                        value = '\n'.join(text1))
                    em.add_field(name = 'Amount',
                        inline = True,
                        value = '\n'.join(text2))

                    em.set_author(name = 'Scoreboard: ' + objective_name, icon_url = 'https://cdn.discordapp.com/icons/336592624624336896/31615259cca237257e3204767959a967.png')
                    em.set_footer(text = 'Total: ' + str(total) + '    |    ' + str(round(total / 1000000, 2)) + ' M')

                    await self.bot.send_message(message.channel, embed = em)
                else:
                    for name, amount in scoreboard:
                        print("name = " + name + ", amount = " + str(amount))

                    print('Total: ' + str(total) + '    |    ' + str(round(total / 1000000, 2)) + ' M')
            else:
                if self.bot:
                    await self.bot.send_message(message.channel, 'Scoreboard not found')
                else:
                    print('Scoreboard not found')
        else:
            if self.bot:
                await self.bot.send_message(message.channel, 'Invalid syntax')
            else:
                print('Invalid syntax')
