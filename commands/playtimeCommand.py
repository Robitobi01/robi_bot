from .baseCommand import BaseCommand
from .commandCache import CommandCache

from utils import *

from difflib import get_close_matches
from nbt import nbt

import discord
import os

def ticksToMinutes(ticks):
    return ticks // 1200 # 1200 = 60 * 20

def minutesToHours(minutes):
    return minutes % 1440 // 60 # 1440 = 24 * 60

def minutesToDays(minutes):
    return minutes // 1440 # 1440 = 24 * 60

def daysToYears(days):
    return days // 365

def minutesOfHour(minutes):
    return minutes % 60

def daysOfYear(days):
    return days % 365

def formatNameForEmbed(name):
    # The only special character allowed in Minecraft username is '_'
    return name.replace('_', '\\_')

class PlayerInfo:
    """Contains playtime information about a player."""
    def __init__(self, player_name, uuid):
        self.player_name = player_name
        self.uuid = uuid

        self.played_minutes = 0
        self.played_days = 0
        self.years = ''
        self.days = ''
        self.hours = ''
        self.minutes = ''

    def setPlaytime(self, ticks):
        self.played_minutes = ticksToMinutes(ticks)
        self.played_days = minutesToDays(self.played_minutes)

        value = daysToYears(self.played_days)
        self.years = str(value) if value > 0 else ''
                                
        value = daysOfYear(self.played_days)
        self.days = str(value) if value > 0 else ''

        value = minutesToHours(self.played_minutes)
        self.hours = str(value) if value > 0 else ''

        self.minutes = str(minutesOfHour(self.played_minutes)) if self.played_minutes > 0 else ''

class PlaytimeCommand(BaseCommand):
    command_text = "!!playtime"
    divider_player_name = '========================='

    def __init__(self, bot, command_cache, survival_folder, stat_folder):
        super().__init__(bot, command_cache)

        self.survival_folder = survival_folder
        self.stat_folder = stat_folder

    def help(self):
        return ('`' + self.command_text + ' [<user_name> [<user_name> ...]]`  **-**  Shows playtime for players\n'
                '`' + self.command_text + ' server`  **-**  Shows survival world times\n')

    async def process(self, message, args):
        if len(args) == 0:
            try:
                players = []
                stat_id = 'stat.playOneMinute'
                total_minutes = 0
                total_ticks = 0

                async with CommandCache.semaphore:
                    for item in zip(self.cache.names, self.cache.uuids):
                        players.append(PlayerInfo(item[0], convert_uuid(item[1])))
                
                for player in players:
                    file = os.path.join(self.stat_folder, player.uuid + '.json')

                    if not os.path.exists(file):
                        continue

                    with open(file) as json_data:
                        stats = json.load(json_data)

                    if not stat_id in stats:
                        continue

                    stat_value = stats[stat_id]

                    player.setPlaytime(stat_value)

                    total_ticks += stat_value

                if players != []:
                    total_minutes = ticksToMinutes(total_ticks)
    
                    # Sort players in descending order based on total playtime in minutes.
                    players = sorted(players, key = lambda p: p.played_minutes, reverse = True)

                    temp_player = PlayerInfo(PlaytimeCommand.divider_player_name, '')
                    temp_player.setPlaytime(0)

                    players.append(temp_player)

                    temp_player = PlayerInfo('Total', '')
                    temp_player.setPlaytime(total_ticks)

                    players.append(temp_player)
            except:
                if self.bot:
                    await self.bot.send_message(message.channel, 'No playerfile or stat found')
                else:
                    print('No playerfile or stat found')

                return

            if players == []:
                if self.bot:
                    await self.bot.send_message(message.channel, 'No playerfile or stat found')
                else:
                    print('No playerfile or stat found')
            else:
                if self.bot:
                    player_names, years, days, hours, minutes = zip(*list((formatNameForEmbed(p.player_name), p.years, p.days, p.hours, p.minutes) for p in players))

                    em = discord.Embed(
                        description = '',
                        colour = 0x003763)

                    em.add_field(
                        name = 'Players',
                        inline = True,
                        value = '\n'.join(player_names))
                    em.add_field(
                        name = 'Years',
                        inline = True,
                        value = '\n'.join(years))
                    em.add_field(
                        name = 'Days',
                        inline = True,
                        value = '\n'.join(days))
                    em.add_field(
                        name = 'Hours',
                        inline = True,
                        value = '\n'.join(hours))
                    em.add_field(
                        name = 'Minutes',
                        inline = True,
                        value = '\n'.join(minutes))
                    
                    em.set_author(
                        name = 'Total Playtime', 
                        icon_url = 'https://cdn.discordapp.com/icons/336592624624336896/31615259cca237257e3204767959a967.png')
                    em.set_footer(text = 'Total: {:,} minutes'.format(total_minutes))

                    await self.bot.send_message(message.channel, embed = em)
                else:
                    print('Total Playtime')
                    print('Name: Years, Days, Hours, Minutes')

                    for p in players:
                        if p.player_name == PlaytimeCommand.divider_player_name:
                            print(p.player_name)
                        else:
                            print(p.player_name + ': ' + p.years + ', ' + p.days + ', ' + p.hours + ', ' + p.minutes)
                    
                    print('Total: {:,} minutes'.format(total_minutes))
        elif len(args) == 1 and args[0] == 'server':
            try:
                nbt_data = nbt.NBTFile(os.path.join(self.survival_folder, 'level.dat'))['Data']
                
                text_names = []
                text_years = []
                text_days = []
                text_hours = []
                text_minutes = []

                data_time = nbt_data['Time'].value
                data_daytime = nbt_data['DayTime'].value
                
                # Total Time IRL
                text_names.append('Total Time (IRL)')

                total_minutes = ticksToMinutes(data_time)
                total_days = minutesToDays(total_minutes)

                value = daysToYears(total_days)
                text_years.append(str(value) if value > 0 else '')
                
                value = daysOfYear(total_days)
                text_days.append(str(value) if value > 0 else '')

                value = minutesToHours(total_minutes)
                text_hours.append(str(value) if value > 0 else '')

                text_minutes.append(str(minutesOfHour(total_minutes)))

                # World Time In-Game
                text_names.append('World Time (IG)')

                world_days = data_daytime // 24000 # DayTime is in ticks, 24000 = 1 Minecraft Day

                value = daysToYears(world_days)
                text_years.append(str(value) if value > 0 else '')
                
                value = daysOfYear(world_days)
                text_days.append(str(value) if value > 0 else '')

                value = data_daytime % 24000 // 1000 # 1 hour in-game is 1000 ticks
                text_hours.append(str(value) if value > 0 else '')

                text_minutes.append('0')
                
                # World Time IRL
                text_names.append('World Time (IRL)')
                
                world_minutes = ticksToMinutes(data_daytime)
                world_days = minutesToDays(world_minutes)

                value = daysToYears(world_days)
                text_years.append(str(value) if value > 0 else '')
                
                value = daysOfYear(world_days)
                text_days.append(str(value) if value > 0 else '')

                value = minutesToHours(world_minutes)
                text_hours.append(str(value) if value > 0 else '')

                text_minutes.append(str(minutesOfHour(world_minutes)))
            except:
                if self.bot:
                    await self.bot.send_message(message.channel, 'No level data found')
                else:
                    print('No level data found')

                return

            if self.bot:
                em = discord.Embed(
                    description = '',
                    colour = 0x003763)
                
                em.add_field(
                    name = 'Name',
                    inline = True,
                    value = text_names)
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
                    name = 'Server Times', 
                    icon_url = 'https://cdn.discordapp.com/icons/336592624624336896/31615259cca237257e3204767959a967.png')
                em.set_footer(text = 'World Time is used for daylight cycle.')

                await self.bot.send_message(message.channel, embed = em)
            else:
                print('Server Times')
                print('Name: Years, Days, Hours, Minutes')
                
                for item in zip(text_names, text_years, text_days, text_hours, text_minutes):
                    print(item[0] + ': ' + item[1] + ', ' + item[2] + ', ' + item[3] + ', ' + item[4])
        elif len(args) >= 1:
            try:
                players = []
                stat_id = 'stat.playOneMinute'
                total_minutes = 0
                total_ticks = 0

                async with CommandCache.semaphore:
                    for arg in args:
                        lower_name = ''.join(get_close_matches(arg, self.cache.lower_names, 1))

                        if lower_name == '':
                            continue

                        uuid = convert_uuid(self.cache.uuids[self.cache.lower_names.index(lower_name)])
                        player_name = self.cache.names[self.cache.lower_names.index(lower_name)]

                        players.append(PlayerInfo(player_name, uuid))
                
                for player in players:
                    file = os.path.join(self.stat_folder, player.uuid + '.json')

                    if not os.path.exists(file):
                        continue

                    with open(file) as json_data:
                        stats = json.load(json_data)

                    if not stat_id in stats:
                        continue

                    stat_value = stats[stat_id]
                    
                    player.setPlaytime(stat_value)

                    total_ticks += stat_value

                if players != []:
                    total_minutes = ticksToMinutes(total_ticks)

                    # Sort players in descending order based on total playtime in minutes.
                    players = sorted(players, key = lambda p: p.played_minutes, reverse = True)

                    temp_player = PlayerInfo(PlaytimeCommand.divider_player_name, '')
                    temp_player.setPlaytime(0)

                    players.append(temp_player)

                    temp_player = PlayerInfo('Total', '')
                    temp_player.setPlaytime(total_ticks)

                    players.append(temp_player)
            except:
                if self.bot:
                    await self.bot.send_message(message.channel, 'No playerfile or stat found')
                else:
                    print('No playerfile or stat found')

                return

            if players == []:
                if self.bot:
                    await self.bot.send_message(message.channel, 'No playerfile or stat found')
                else:
                    print('No playerfile or stat found')
            else:
                player_names, years, days, hours, minutes = zip(*list((formatNameForEmbed(p.player_name), p.years, p.days, p.hours, p.minutes) for p in players))
                
                if self.bot:
                    em = discord.Embed(
                        description = '',
                        colour = 0x003763)

                    em.add_field(
                        name = 'Player',
                        inline = True,
                        value = '\n'.join(player_names))
                    em.add_field(
                        name = 'Years',
                        inline = True,
                        value = '\n'.join(years))
                    em.add_field(
                        name = 'Days',
                        inline = True,
                        value = '\n'.join(days))
                    em.add_field(
                        name = 'Hours',
                        inline = True,
                        value = '\n'.join(hours))
                    em.add_field(
                        name = 'Minutes',
                        inline = True,
                        value = '\n'.join(minutes))
                            
                    em.set_author(
                        name = 'Total Playtime', 
                        icon_url = 'https://cdn.discordapp.com/icons/336592624624336896/31615259cca237257e3204767959a967.png')
                    em.set_footer(text = 'Total: {:,} minutes'.format(total_minutes))

                    await self.bot.send_message(message.channel, embed = em)
                else:
                    print('Total Playtime')
                    print('Player: Years, Days, Hours, Minutes')
                    
                    for p in players:
                        if p.player_name == PlaytimeCommand.divider_player_name:
                            print(p.player_name)
                        else:
                            print(p.player_name + ': ' + p.years + ', ' + p.days + ', ' + p.hours + ', ' + p.minutes)

                    print('Total: {:,} minutes'.format(total_minutes))
        else:
            if self.bot:
                await self.bot.send_message(message.channel, 'Invalid syntax')
            else:
                print('Invalid syntax')
