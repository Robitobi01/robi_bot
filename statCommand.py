from .baseCommand import BaseCommand
from .commandCache import CommandCache

from utils import *

from difflib import get_close_matches
from nbt import nbt

import asyncio
import discord
import os

class StatCommand(BaseCommand):
    command_text = "!!stat"

    def __init__(self, discord, client, message, command_cache, stat_folder):
        super().__init__(discord, client, message, command_cache)

        self.stat_folder = stat_folder

    def help(self):
        return ('`' + self.command_text + ' player <user_name> <stat_name>`  **-**  Shows statistics value\n'
                '`' + self.command_text + ' list <stat_name>`  **-**  Shows statistics ranking\n')

    async def process(self, args):
        # stat player
        if len(args) == 4 and args[1] == 'player':
            async with CommandCache.semaphore:
                try:
                    player_name = ''.join(get_close_matches(args[2], self.cache.names, 1))
                    uuid = convert_uuid(self.cache.uuids[self.cache.names.index(player_name)])

                    try:
                        with open(os.path.join(self.stat_folder, uuid + '.json')) as json_data:
                            stats = json.load(json_data)

                        stat_id = ''.join(get_close_matches('stat.' + args[3], self.cache.stat_ids, 1))
                        stat_value = str(stats[stat_id]) if stat_id in stats else str(0)

                        if self.client == None:
                            print('Stat = ' + stat_id + ', Value = ' + stat_value + ', ' + player_name + ' - Statistics')
                        else:
                            em = discord.Embed(
                                description = '',
                                colour = 0x003763)

                            em.add_field(
                                name = 'Stat',
                                inline = True,
                                value = stat_id)
                            em.add_field(
                                name = 'Result',
                                inline = True,
                                value = stat_value)

                            em.set_author(
                                name = player_name + ' - Statistics', 
                                icon_url = 'https://crafatar.com/avatars/' + uuid)
                        
                            await self.client.send_message(self.message.channel, embed = em)
                    except:
                        if self.client == None:
                            print('No playerfile or stat found')
                        else:
                            await self.client.send_message(self.message.channel, 'No playerfile or stat found')
                except:
                    if self.client == None:
                        print('Invalid username')
                    else:
                        await self.client.send_message(self.message.channel, 'Invalid username')

        # stat list
        elif len(args) == 3 and args[1] == 'list':
            async with CommandCache.semaphore:
                try:
                    stat_id = ''.join(get_close_matches('stat.' + args[2], self.cache.stat_ids, 1))
                    text1 = []
                    text2 = []
                    total = 0

                    for item in self.cache.uuids:
                        with open(os.path.join(self.stat_folder, convert_uuid(item) + '.json')) as json_data:
                            stats = json.load(json_data)

                            if stat_id in stats:
                                text1.append(stats[stat_id])
                                text2.append(self.cache.names[self.cache.uuids.index(item)])
                                total += stats[stat_id]

                    if text1 == []:
                        if self.client == None:
                            print('No playerfile or stat found')
                        else:
                            await self.client.send_message(self.message.channel, 'No playerfile or stat found')
                    else:
                        if self.client == None:
                            print(stat_id + ' Ranking')

                            for item in reversed(sorted(zip(text1, text2))):
                                print(str(item[0]) + ", " + item[1])

                            print('Total: ' + str(total) + '    |    ' + str(round((total / 1000000), 2)) + ' M')
                        else:
                            text1, text2 = zip(*sorted(zip(text1, text2)))

                            em = discord.Embed(
                                description = '',
                                colour = 0x003763)

                            em.add_field(
                                name = 'Players',
                                inline = True,
                                value = '\n'.join(text2[::-1]))
                            em.add_field(
                                name = 'Result',
                                inline = True,
                                value = '\n'.join(str(x) for x in text1[::-1]))
                            
                            em.set_author(
                                name = stat_id + ' - Ranking', 
                                icon_url = 'https://cdn.discordapp.com/icons/336592624624336896/31615259cca237257e3204767959a967.png')
                            em.set_footer(text = 'Total: ' + str(total) + '    |    ' + str(round((total / 1000000), 2)) + ' M')

                            await self.client.send_message(self.message.channel, embed = em)
                except:
                    if self.client == None:
                        print('No playerfile or stat found')
                    else:
                        await self.client.send_message(self.message.channel, 'No playerfile or stat found')
        else:
            if self.client == None:
                print('Invalid syntax')
            else:
                await self.client.send_message(self.message.channel, 'Invalid syntax')
