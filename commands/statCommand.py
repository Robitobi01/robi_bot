from .baseCommand import BaseCommand
from .commandCache import CommandCache

from utils import *

from difflib import get_close_matches
from nbt import nbt

import discord
import os

class StatCommand(BaseCommand):
    command_text = "!!stat"

    def __init__(self, bot, command_cache, stat_folder):
        super().__init__(bot, command_cache)

        self.stat_folder = stat_folder

    def help(self):
        return ('`' + self.command_text + ' player <user_name> <stat_name>`  **-**  Shows statistics value\n'
                '`' + self.command_text + ' list <stat_name>`  **-**  Shows statistics ranking\n')

    async def process(self, message, args):
        # stat player
        if len(args) == 3 and args[0] == 'player':
            async with CommandCache.semaphore:
                try:
                    lower_name = ''.join(get_close_matches(args[1], self.cache.lower_names, 1))
                    uuid = convert_uuid(self.cache.uuids[self.cache.lower_names.index(lower_name)])
                    player_name = self.cache.names[self.cache.lower_names.index(lower_name)]

                    stat_id = 'stat.' + args[2] if not args[2].startswith('stat') else args[2]
                    stat_id = ''.join(get_close_matches(stat_id, self.cache.stat_ids, 1))

                    if stat_id == '':
                        if self.bot:
                            await self.bot.send_message(message.channel, 'Invalid stat')
                        else:
                            print('Invalid stat')
                except:
                    if self.bot:
                        await self.bot.send_message(message.channel, 'Invalid username or stat')
                    else:
                        print('Invalid username or stat')

                    return

            try:
                with open(os.path.join(self.stat_folder, uuid + '.json')) as json_data:
                    stats = json.load(json_data)

                stat_value = str(stats[stat_id]) if stat_id in stats else str(0)
            except:
                if self.bot:
                    await self.bot.send_message(message.channel, 'No playerfile or stat found')
                else:
                    print('No playerfile or stat found')

            if self.bot:
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

                await self.bot.send_message(message.channel, embed = em)
            else:
                print('Stat = ' + stat_id + ', Value = ' + stat_value + ', ' + player_name + ' - Statistics')

        # stat list
        elif len(args) == 2 and args[0] == 'list':
            async with CommandCache.semaphore:
                try:
                    stat_id = 'stat.' + args[1] if not args[1].startswith('stat') else args[1]
                    stat_id = ''.join(get_close_matches(stat_id, self.cache.stat_ids, 1))

                    if stat_id == '':
                        if self.bot:
                            await self.bot.send_message(message.channel, 'Invalid stat')
                        else:
                            print('Invalid stat')

                    text1 = []
                    text2 = []
                    total = 0

                    for item in self.cache.uuids:
                        with open(os.path.join(self.stat_folder, convert_uuid(item) + '.json')) as json_data:
                            stats = json.load(json_data)

                            if stat_id in stats:
                                text1.append(stats[stat_id])
                                text2.append(formatNameForEmbed(self.cache.names[self.cache.uuids.index(item)]))
                                total += stats[stat_id]
                except:
                    if self.bot:
                        await self.bot.send_message(message.channel, 'No playerfile or stat found')
                    else:
                        print('No playerfile or stat found')

                    return

            if text1 == []:
                if self.bot:
                    await self.bot.send_message(message.channel, 'No playerfile or stat found')
                else:
                    print('No playerfile or stat found')
            else:
                if self.bot:
                    text1, text2 = zip(*sorted(zip(text1, text2), reverse = True))

                    em = discord.Embed(
                        description = '',
                        colour = 0x003763)

                    em.add_field(
                        name = 'Players',
                        inline = True,
                        value = '\n'.join(text2))
                    em.add_field(
                        name = 'Result',
                        inline = True,
                        value = '\n'.join(str(x) for x in text1))

                    em.set_author(
                        name = stat_id + ' - Ranking',
                        icon_url = 'https://cdn.discordapp.com/icons/336592624624336896/31615259cca237257e3204767959a967.png')
                    em.set_footer(text = 'Total: ' + str(total) + '    |    ' + str(round((total / 1000000), 2)) + ' M')

                    await self.bot.send_message(message.channel, embed = em)
                else:
                    print(stat_id + ' Ranking')

                    for item in sorted(zip(text1, text2), reverse = True):
                        print(str(item[0]) + ', ' + item[1])

                    print('Total: ' + str(total) + '    |    ' + str(round((total / 1000000), 2)) + ' M')

        #total
        elif len(args) == 2 and args[0] == 'total':
            async with CommandCache.semaphore:
                try:
                    stat_id = 'stat.' + args[1] if not args[1].startswith('stat') else args[1]
                    stat_id = ''.join(get_close_matches(stat_id, self.cache.stat_ids, 1))
                    if stat_id == '':
                        if self.bot:
                            await self.bot.send_message(message.channel, 'Invalid stat')
                        else:
                            print('Invalid stat')

                    total = 0
                    for item in self.cache.uuids:
                        with open(os.path.join(self.stat_folder, convert_uuid(item) + '.json')) as json_data:
                            stats = json.load(json_data)
                            if stat_id in stats:
                                total += stats[stat_id]
                except:
                    if self.bot:
                        await self.bot.send_message(message.channel, 'No playerfile or stat found')
                    else:
                        print('No playerfile or stat found')

                    return

                em = discord.Embed(
                    description = '',
                    colour = 0x003763)
                em.add_field(
                    name = 'Result',
                    inline = True,
                    value = 'Total: ' + str(total) + '    |    ' + str(round((total / 1000000), 2)) + ' M')

                em.set_author(
                    name = stat_id + ' - Ranking',
                    icon_url = 'https://cdn.discordapp.com/icons/336592624624336896/31615259cca237257e3204767959a967.png')
                await self.bot.send_message(message.channel, embed = em)

        else:
            if self.bot:
                await self.bot.send_message(message.channel, 'Invalid syntax')
            else:
                print('Invalid syntax')
