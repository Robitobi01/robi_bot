from .baseCommand import BaseCommand

from utils import *

import discord
import os

class WorldsizeCommand(BaseCommand):
    command_text = "!!worldsize"

    def __init__(self, discord, client, message, command_cache, survival_folder, overworld_folder, nether_folder, end_folder):
        super().__init__(discord, client, message, command_cache)

        self.survival_folder = survival_folder
        self.overworld_folder = overworld_folder
        self.nether_folder = nether_folder
        self.end_folder = end_folder

    def help(self):
        return '`' + self.command_text + '`  **-**  Shows current world sizes\n'
    
    async def process(self, args):
        try:
            # Get sizes in GB
            total_size = round(get_size(self.survival_folder) / 1073741824, 2)
            overworld_size = round(get_size(self.overworld_folder) / 1073741824, 2)
            nether_size = round(get_size(self.nether_folder) / 1073741824, 2)
            end_size = round(get_size(self.end_folder) / 1073741824, 2)
            
            if self.client == None:
                print('Overworld = ' + str(overworld_size) + ' GB')
                print('Nether = ' + str(nether_size) + ' GB')
                print('End = ' + str(end_size) + ' GB')
                print('Total = ' + str(total_size) + ' GB')
            else:
                em = discord.Embed(
                    description = '',
                    colour = 0x003763)
            
                em.add_field(
                    name = 'Dimension',
                    inline = True,
                    value = 'Overworld\nNether\nEnd')
                em.add_field(
                    name = 'Size',
                    inline = True,
                    value = '**' + str(overworld_size) +  ' **GB**\n' + str(nether_size) +  ' **GB**\n' + str(end_size) + ' **GB')
            
                em.set_author(name = 'World Size:', icon_url = 'https://cdn.discordapp.com/icons/336592624624336896/31615259cca237257e3204767959a967.png')
                em.set_footer(text = 'Total World Size: ' + str(total_size) + 'GB')
            
                await self.client.send_message(self.message.channel, embed = em)
        except:
            if self.client == None:
                print('An error occurred while calculating world size')
            else:
                await self.client.send_message(self.message.channel, 'An error occurred while calculating world size')

