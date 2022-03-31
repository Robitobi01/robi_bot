from difflib import get_close_matches

from nbt import nbt

from utils import *
from .baseCommand import BaseCommand
from .commandCache import CommandCache


def ticks_to_minutes(ticks):
    return ticks // 1200  # 1200 = 60 * 20


def minutes_to_hours(minutes):
    return minutes % 1440 // 60  # 1440 = 24 * 60


def minutes_to_days(minutes):
    return minutes // 1440  # 1440 = 24 * 60


def days_to_years(days):
    return days // 365


def minutes_of_hour(minutes):
    return minutes % 60


def days_of_year(days):
    return days % 365


def format_playtime_for_total(years, days, hours, minutes):
    if years + days + hours + minutes == 0:
        return ''

    buffer = '' if years <= 0 else '{0}y '.format(years)

    return buffer + '{0:0>3} {1:0>2}:{2:0>2}'.format(days, hours, minutes)


def format_playtime_for_embed(years, days, hours, minutes, use_code_block=False):
    if years + days + hours + minutes == 0:
        buffer = ''
    else:
        buffer = '{0:0>3} {1:0>2}:{2:0>2}'.format(days, hours, minutes)

        if years > 0:
            buffer += ' {0}y'.format(years)

    if use_code_block:
        buffer = '`' + buffer + '`'

    return buffer


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

    def set_playtime(self, ticks):
        self.played_minutes = ticks_to_minutes(ticks)
        self.played_days = minutes_to_days(self.played_minutes)

        self.years = days_to_years(self.played_days)
        self.days = days_of_year(self.played_days)
        self.hours = minutes_to_hours(self.played_minutes)
        self.minutes = minutes_of_hour(self.played_minutes)


class PlaytimeCommand(BaseCommand):
    command_text = "!!playtime"

    def __init__(self, client, command_cache, survival_folder, stat_folder):
        super().__init__(client, command_cache)

        self.survival_folder = survival_folder
        self.stat_folder = stat_folder

    def help(self):
        return ('`' + self.command_text + ' [<user_name> [<user_name> ...]]`  **-**  Shows playtime for players\n'
                                          '`' + self.command_text + ' server`  **-**  Shows survival world times\n')

    async def process_players(self, message, players):
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

                player.set_playtime(stat_value)

                total_ticks += stat_value

            if not players:
                if self.client:
                    await message.channel.send('No playerfile or stat found')
                else:
                    print('No playerfile or stat found')
            else:
                # sort players in descending order based on total playtime in minutes
                players = sorted(players, key=lambda p: p.played_minutes, reverse=True)

                total_info = PlayerInfo('', '')
                total_info.set_playtime(total_ticks)

                if self.client:
                    player_names, playtimes = zip(*list(
                        (format_name_for_embed(p.player_name),
                         format_playtime_for_embed(p.years, p.days, p.hours, p.minutes))
                        for p in players))
                    shortened_lists = shorten_embed_lists([player_names, playtimes], 2)
                    player_names, playtimes = shortened_lists[0], shortened_lists[1]
                    em = generate_embed_table(
                        ['Player', 'Playtime'],
                        ['\n'.join(player_names), '\n'.join(playtimes)],
                        True)
                    em.set_author(
                        name='Total Playtime',
                        icon_url='https://redirect.dugged.net:8443/logo_full.png')

                    if len(players) > 1:
                        em.set_footer(text='Total: {0}'.format(
                            format_playtime_for_total(total_info.years, total_info.days, total_info.hours,
                                                      total_info.minutes)))

                    await message.channel.send(embed=em)
                else:
                    print('Player: Playtime')
                    for p in players:
                        print('{0:<20}: {1}'.format(p.player_name,
                                                    format_playtime_for_embed(p.years, p.days, p.hours, p.minutes,
                                                                              False)))

                    if len(players) > 1:
                        print('Total: {0}'.format(
                            format_playtime_for_total(total_info.years, total_info.days, total_info.hours,
                                                      total_info.minutes)))
        except Exception as e:
            if self.client:
                await message.channel.send('No playerfile or stat found ' + str(e))
            else:
                print('No playerfile or stat found')

    async def process(self, message, args):
        if len(args) == 0:
            # process all players
            try:
                players = []

                async with CommandCache.semaphore:
                    for item in zip(self.cache.names, self.cache.uuids):
                        players.append(PlayerInfo(item[0], convert_uuid(item[1])))

                await self.process_players(message, players)
            except:
                if self.client:
                    await message.channel.send('No playerfile or stat found')
                else:
                    print('No playerfile or stat found')
        elif len(args) == 1 and args[0] == 'server':
            # process server times
            try:
                nbt_data = nbt.NBTFile(os.path.join(self.survival_folder, 'level.dat'))['Data']

                text_names = []
                text_times = []

                data_time = nbt_data['Time'].value
                data_daytime = nbt_data['DayTime'].value

                # Total Time IRL
                text_names.append('Total Time (IRL)')

                total_minutes = ticks_to_minutes(data_time)
                total_days = minutes_to_days(total_minutes)

                years = days_to_years(total_days)
                days = days_of_year(total_days)
                hours = minutes_to_hours(total_minutes)
                minutes = minutes_of_hour(total_minutes)

                text_times.append(format_playtime_for_total(years, days, hours, minutes))

                # Total Time In-Game
                text_names.append('Total Time (IG)')

                total_minutes = ticks_to_minutes(data_time)
                total_days = data_time // 24000  # DayTime is in ticks, 24000 = 1 Minecraft Day

                years = days_to_years(total_days)
                days = days_of_year(total_days)
                hours = data_time % 24000 // 1000  # 1 hour in-game is 1000 ticks
                minutes = 0

                text_times.append(format_playtime_for_total(years, days, hours, minutes))

                # World Time IRL
                text_names.append('World Time (IRL)')

                world_minutes = ticks_to_minutes(data_daytime)
                world_days = minutes_to_days(world_minutes)

                years = days_to_years(world_days)
                days = days_of_year(world_days)
                hours = minutes_to_hours(world_minutes)
                minutes = minutes_of_hour(world_minutes)

                text_times.append(format_playtime_for_total(years, days, hours, minutes))

                # World Time In-Game
                text_names.append('World Time (IG)')

                world_days = data_daytime // 24000  # DayTime is in ticks, 24000 = 1 Minecraft Day

                years = days_to_years(world_days)
                days = days_of_year(world_days)
                hours = data_daytime % 24000 // 1000  # 1 hour in-game is 1000 ticks
                minutes = 0

                text_times.append(format_playtime_for_total(years, days, hours, minutes))
            except:
                if self.client:
                    await message.channel.send('No level data found')
                else:
                    print('No level data found')

                return

            if self.client:
                em = generate_embed_table(
                    ['Name', 'Time'],
                    ['\n'.join(text_names), '\n'.join(text_times)],
                    True)
                em.set_author(
                    name='Server Times',
                    icon_url='https://redirect.dugged.net:8443/logo_full.png')
                em.set_footer(text='World Time is used for daylight cycle.')

                await message.channel.send(embed=em)
            else:
                print('Name: Time')

                for item in zip(text_names, text_times):
                    print(item[0] + ': ' + item[1])

        elif len(args) >= 1:
            # process args as player names
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

                await self.process_players(message, players)
            except:
                if self.client:
                    await message.channel.send('No playerfile or stat found')
                else:
                    print('No playerfile or stat found')
        else:
            if self.client:
                await message.channel.send('Invalid syntax')
            else:
                print('Invalid syntax')
