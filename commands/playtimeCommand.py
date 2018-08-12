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

def formatPlaytimeForEmbed(years, days, hours, minutes):
    if years + days + hours + minutes == 0:
        return ''

    buffer = '`   ' if years <= 0 else '`{0}y '.format(years)
    
    return buffer + '{0:>3} {1:0>2}:{2:0>2}`'.format(days, hours, minutes)

class PlayerInfo:
    """Contains playtime information about a player."""
    def __init__(self, player_name, uuid):
        self.player_name = player_name
        self.uuid = uuid

        self.played_minutes = 0
        self.played_days = 0
        self.years = 0
        self.days = 0
        self.hours = 0
        self.minutes = 0

    def setPlaytime(self, ticks):
        self.played_minutes = ticksToMinutes(ticks)
        self.played_days = minutesToDays(self.played_minutes)

        self.years = daysToYears(self.played_days)
        self.days = daysOfYear(self.played_days)
        self.hours = minutesToHours(self.played_minutes)
        self.minutes = minutesOfHour(self.played_minutes)

class PlaytimeCommand(BaseCommand):
    command_text = "!!playtime"

    def __init__(self, bot, command_cache, survival_folder, stat_folder):
        super().__init__(bot, command_cache)

        self.survival_folder = survival_folder
        self.stat_folder = stat_folder

    def help(self):
        return ('`' + self.command_text + ' [<user_name> [<user_name> ...]]`  **-**  Shows playtime for players\n'
                '`' + self.command_text + ' server`  **-**  Shows survival world times\n')

    async def processPlayers(self, message, players):
        try:
            stat_id = 'stat.playOneMinute'
            total_ticks = 0

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

            if players == []:
                if self.bot:
                    await self.bot.send_message(message.channel, 'No playerfile or stat found')
                else:
                    print('No playerfile or stat found')
            else:
                # Sort players in descending order based on total playtime in minutes.
                players = sorted(players, key = lambda p: p.played_minutes, reverse = True)

                total_info = PlayerInfo('', '')
                total_info.setPlaytime(total_ticks)

                if self.bot:
                    player_names, playtimes = zip(*list((formatNameForEmbed(p.player_name), formatPlaytimeForEmbed(p.years, p.days, p.hours, p.minutes)) for p in players))

                    em = discord.Embed(
                        description = '',
                        colour = 0x003763)

                    em.add_field(
                        name = 'Player',
                        inline = True,
                        value = '\n'.join(player_names))
                    em.add_field(
                        name = 'Playtime',
                        inline = True,
                        value = '\n'.join(playtimes))
                    
                    em.set_author(
                        name = 'Total Playtime', 
                        icon_url = 'https://cdn.discordapp.com/icons/336592624624336896/31615259cca237257e3204767959a967.png')

                    if len(players) > 1:
                        em.set_footer(text = 'Total: {0}'.format(formatPlaytimeForEmbed(total_info.years, total_info.days, total_info.hours, total_info.minutes)))

                    await self.bot.send_message(message.channel, embed = em)
                else:
                    print('Player: Playtime')

                    for p in players:
                        print('{0:<20}: {1}'.format(p.player_name, formatPlaytimeForEmbed(p.years, p.days, p.hours, p.minutes)))

                    if len(players) > 1:
                        print('Total: {0}'.format(formatPlaytimeForEmbed(total_info.years, total_info.days, total_info.hours, total_info.minutes)))
        except:
            if self.bot:
                await self.bot.send_message(message.channel, 'No playerfile or stat found')
            else:
                print('No playerfile or stat found')

    async def process(self, message, args):
        if len(args) == 0:
            # Process all players
            try:
                players = []

                async with CommandCache.semaphore:
                    for item in zip(self.cache.names, self.cache.uuids):
                        players.append(PlayerInfo(item[0], convert_uuid(item[1])))

                await self.processPlayers(message, players)
            except:
                if self.bot:
                    await self.bot.send_message(message.channel, 'No playerfile or stat found')
                else:
                    print('No playerfile or stat found')
        elif len(args) == 1 and args[0] == 'server':
            # Process server times
            try:
                nbt_data = nbt.NBTFile(os.path.join(self.survival_folder, 'level.dat'))['Data']
                
                text_names = []
                text_times = []

                data_time = nbt_data['Time'].value
                data_daytime = nbt_data['DayTime'].value
                
                # Total Time IRL
                text_names.append('Total Time (IRL)')

                total_minutes = ticksToMinutes(data_time)
                total_days = minutesToDays(total_minutes)

                years = daysToYears(total_days)
                days = daysOfYear(total_days)
                hours = minutesToHours(total_minutes)
                minutes = minutesOfHour(total_minutes)

                text_times.append(formatPlaytimeForEmbed(years, days, hours, minutes))

                # Total Time In-Game
                text_names.append('Total Time (IG)')

                total_minutes = ticksToMinutes(data_time)
                total_days = data_time // 24000 # DayTime is in ticks, 24000 = 1 Minecraft Day

                years = daysToYears(total_days)
                days = daysOfYear(total_days)
                hours = data_time % 24000 // 1000 # 1 hour in-game is 1000 ticks
                minutes = 0

                text_times.append(formatPlaytimeForEmbed(years, days, hours, minutes))
                
                # World Time IRL
                text_names.append('World Time (IRL)')
                
                world_minutes = ticksToMinutes(data_daytime)
                world_days = minutesToDays(world_minutes)
                
                years = daysToYears(world_days)
                days = daysOfYear(world_days)
                hours = minutesToHours(world_minutes)
                minutes = minutesOfHour(world_minutes)

                text_times.append(formatPlaytimeForEmbed(years, days, hours, minutes))

                # World Time In-Game
                text_names.append('World Time (IG)')

                world_days = data_daytime // 24000 # DayTime is in ticks, 24000 = 1 Minecraft Day

                years = daysToYears(world_days)
                days = daysOfYear(world_days)
                hours = data_daytime % 24000 // 1000 # 1 hour in-game is 1000 ticks
                minutes = 0

                text_times.append(formatPlaytimeForEmbed(years, days, hours, minutes))
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
                    value = '\n'.join(text_names))
                em.add_field(
                    name = 'Time',
                    inline = True,
                    value = '\n'.join(text_times))
                
                em.set_author(
                    name = 'Server Times', 
                    icon_url = 'https://cdn.discordapp.com/icons/336592624624336896/31615259cca237257e3204767959a967.png')
                em.set_footer(text = 'World Time is used for daylight cycle.')

                await self.bot.send_message(message.channel, embed = em)
            else:
                print('Name: Time')
                
                for item in zip(text_names, text_times):
                    print(item[0] + ': ' + item[1])
        elif len(args) >= 1:
            # Process args as player names
            try:
                players = []

                async with CommandCache.semaphore:
                    for arg in args:
                        lower_name = ''.join(get_close_matches(arg, self.cache.lower_names, 1))

                        if lower_name == '':
                            continue

                        uuid = convert_uuid(self.cache.uuids[self.cache.lower_names.index(lower_name)])
                        player_name = self.cache.names[self.cache.lower_names.index(lower_name)]

                        players.append(PlayerInfo(player_name, uuid))

                await self.processPlayers(message, players)
            except:
                if self.bot:
                    await self.bot.send_message(message.channel, 'No playerfile or stat found')
                else:
                    print('No playerfile or stat found')
        else:
            if self.bot:
                await self.bot.send_message(message.channel, 'Invalid syntax')
            else:
                print('Invalid syntax')
