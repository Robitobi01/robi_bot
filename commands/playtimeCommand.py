from .baseCommand import BaseCommand
from .commandCache import CommandCache

from utils import *

from difflib import get_close_matches
from nbt import nbt

import discord
import os

class PlaytimeCommand(BaseCommand):
    command_text = "!!playtime"

    def __init__(self, bot, command_cache, stat_folder):
        super().__init__(bot, command_cache)

        self.stat_folder = stat_folder

    def help(self):
        return ('`' + self.command_text + ' `  **-**  Shows playtime for all players\n'
                '`' + self.command_text + ' <user_name> `  **-**  Shows playtime for specified player\n')

    async def process(self, message, args):
        if len(args) == 0:
            async with CommandCache.semaphore:
                try:
                    stat_id = 'stat.playOneMinute'
                    total_minutes = 0

                    text_names = []
                    text_years = []
                    text_days = []
                    text_hours = []
                    text_minutes = []
                    player_minutes = []

                    for item in self.cache.uuids:
                        with open(os.path.join(self.stat_folder, convert_uuid(item) + '.json')) as json_data:
                            stats = json.load(json_data)

                            if stat_id in stats:
                                played_minutes = stats[stat_id] // 1200 # playOneMinute is in ticks
                                played_days = played_minutes // 1440

                                total_minutes += played_minutes

                                value = played_days // 365
                                text_years.append(str(value) if value > 0 else '') 
                                
                                value = played_days % 365
                                text_days.append(str(value) if value > 0 else '')

                                value = played_minutes % 1440 // 60
                                text_hours.append(str(value) if value > 0 else '')

                                text_minutes.append(str(played_minutes % 60))
                                
                                text_names.append(self.cache.names[self.cache.uuids.index(item)])
                                player_minutes.append(played_minutes)
                except:
                    if self.bot:
                        await self.bot.send_message(message.channel, 'No playerfile or stat found')
                    else:
                        print('No playerfile or stat found')

                    return

            if text_names == []:
                if self.bot:
                    await self.bot.send_message(message.channel, 'No playerfile or stat found')
                else:
                    print('No playerfile or stat found')
            else:
                if self.bot:
                    player_minutes, text_names, text_years, text_days, text_hours, text_minutes = zip(*sorted(zip(player_minutes, text_names, text_years, text_days, text_hours, text_minutes), reverse = True))

                    text_names.append('=========================')
                    text_years.append('')
                    text_days.append('')
                    text_hours.append('')
                    text_minutes.append('')

                    total_days = total_minutes // 1440

                    text_names.append('Total')
                    
                    value = total_days // 365
                    text_years.append(str(value) if value > 0 else '')
                                
                    value = total_days % 365
                    text_days.append(str(value) if value > 0 else '')

                    value = total_minutes % 1440 // 60
                    text_hours.append(str(value) if value > 0 else '') 

                    text_minutes.append(str(total_minutes % 60))

                    em = discord.Embed(
                        description = '',
                        colour = 0x003763)

                    em.add_field(
                        name = 'Players',
                        inline = True,
                        value = '\n'.join(text_names[::]))
                    em.add_field(
                        name = 'Years',
                        inline = True,
                        value = '\n'.join(text_years[::]))
                    em.add_field(
                        name = 'Days',
                        inline = True,
                        value = '\n'.join(text_days[::]))
                    em.add_field(
                        name = 'Hours',
                        inline = True,
                        value = '\n'.join(text_hours[::]))
                    em.add_field(
                        name = 'Minutes',
                        inline = True,
                        value = '\n'.join(text_minutes[::]))
                            
                    em.set_author(
                        name = 'Total Playtime', 
                        icon_url = 'https://cdn.discordapp.com/icons/336592624624336896/31615259cca237257e3204767959a967.png')
                    em.set_footer(text = 'Total: {:,} minutes'.format(total_minutes))

                    await self.bot.send_message(message.channel, embed = em)
                else:
                    print('Total Playtime')
                    print('Name: Years, Days, Hours, Minutes')

                    for item in sorted(zip(player_minutes, text_names, text_years, text_days, text_hours, text_minutes), reverse = True):
                        print(item[1] + ": " + item[2] + ", " + item[3] + ", " + item[4] + ", " + item[5])
                        
                    total_days = total_minutes // 1440

                    text = ['Total: ']
                    
                    value = total_days // 365
                    text.append(str(value)) if value > 0 else text.append('')
                                
                    value = total_days % 365
                    text.append(', ' + str(value)) if value > 0 else text.append(', ')

                    value = total_minutes % 1440 // 60
                    text.append(', ' + str(value)) if value > 0 else text.append(', ')

                    text.append(', ' + str(total_minutes % 60))

                    print(''.join(text[::]))
                    print('Total: {:,} minutes'.format(total_minutes))        
        elif len(args) == 1:
            async with CommandCache.semaphore:
                try:
                    player_name = ''.join(get_close_matches(args[0], self.cache.names, 1))
                    uuid = convert_uuid(self.cache.uuids[self.cache.names.index(player_name)])

                    stat_id = 'stat.playOneMinute'

                    text_years = ''
                    text_days = ''
                    text_hours = ''
                    text_minutes = ''

                    with open(os.path.join(self.stat_folder, uuid + '.json')) as json_data:
                        stats = json.load(json_data)

                        if stat_id in stats:
                            played_minutes = stats[stat_id] // 1200 # playOneMinute is in ticks
                            played_days = played_minutes // 1440

                            value = played_days // 365
                            text_years = str(value) if value > 0 else ''
                                
                            value = played_days % 365
                            text_days = str(value) if value > 0 else ''

                            value = played_minutes % 1440 // 60
                            text_hours = str(value) if value > 0 else ''

                            text_minutes = str(played_minutes % 60)
                except:
                    if self.bot:
                        await self.bot.send_message(message.channel, 'No playerfile or stat found')
                    else:
                        print('No playerfile or stat found')

                    return

            if player_name == '':
                if self.bot:
                    await self.bot.send_message(message.channel, 'No playerfile or stat found')
                else:
                    print('No playerfile or stat found')
            else:
                if self.bot:
                    em = discord.Embed(
                        description = '',
                        colour = 0x003763)

                    em.add_field(
                        name = 'Player',
                        inline = True,
                        value = player_name)
                    em.add_field(
                        name = 'Years',
                        inline = True,
                        value = text_years)
                    em.add_field(
                        name = 'Days',
                        inline = True,
                        value = text_days)
                    em.add_field(
                        name = 'Hours',
                        inline = True,
                        value = text_hours)
                    em.add_field(
                        name = 'Minutes',
                        inline = True,
                        value = text_minutes)
                            
                    em.set_author(
                        name = 'Total Playtime', 
                        icon_url = 'https://cdn.discordapp.com/icons/336592624624336896/31615259cca237257e3204767959a967.png')
                    em.set_footer(text = 'Total: {:,} minutes'.format(played_minutes))

                    await self.bot.send_message(message.channel, embed = em)
                else:
                    print('Total Playtime')
                    print('Name: Years, Days, Hours, Minutes')
                    
                    print(player_name + ": " + text_years + ", " + text_days + ", " + text_hours + ", " + text_minutes)
                        
                    print('Total: {:,} minutes'.format(played_minutes))
        else:
            if self.bot:
                await self.bot.send_message(message.channel, 'Invalid syntax')
            else:
                print('Invalid syntax')
