from difflib import get_close_matches

from utils import *
from .baseCommand import BaseCommand
from .commandCache import CommandCache


class StatCommand(BaseCommand):
    command_text = "!!stat"

    def __init__(self, client, command_cache, stat_folder):
        super().__init__(client, command_cache)

        self.stat_folder = stat_folder

    def help(self):
        return ('`' + self.command_text + ' player <user_name> <stat_name>`  **-**  Shows player statistic value\n' +
                '`' + self.command_text + ' list <stat_name>`  **-**  Shows statistics ranking\n' +
                '`' + self.command_text + ' total <stat_name>`  **-**  Shows statistic total\n')

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
                        if self.client:
                            await message.channel.send('Invalid stat')
                        else:
                            print('Invalid stat')
                except:
                    if self.client:
                        await message.channel.send('Invalid username or stat')
                    else:
                        print('Invalid username or stat')

                    return

            try:
                with open(os.path.join(self.stat_folder, uuid + '.json')) as json_data:
                    stats = json.load(json_data)

                stat_value = str(stats[stat_id]) if stat_id in stats else str(0)
            except:
                if self.client:
                    await message.channel.send('No playerfile or stat found')
                else:
                    print('No playerfile or stat found')

            if self.client:
                em = generate_embed_table(
                    ['Stat', 'Result'],
                    [stat_id, stat_value],
                    True)
                em.set_author(
                    name=player_name + ' - Statistics',
                    icon_url='https://crafatar.com/avatars/' + uuid)
                await message.channel.send(embed=em)

            else:
                print('Stat = ' + stat_id + ', Value = ' + stat_value + ', ' + player_name + ' - Statistics')

        # stat list
        elif len(args) == 2 and args[0] == 'list':
            async with CommandCache.semaphore:
                try:
                    stat_id = 'stat.' + args[1] if not args[1].startswith('stat') else args[1]
                    stat_id = ''.join(get_close_matches(stat_id, self.cache.stat_ids, 1))

                    if stat_id == '':
                        if self.client:
                            await message.channel.send('Invalid stat')
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
                                text2.append(format_name_for_embed(self.cache.names[self.cache.uuids.index(item)]))
                                total += stats[stat_id]
                except:
                    if self.client:
                        await message.channel.send('No playerfile or stat found')
                    else:
                        print('No playerfile or stat found')

                    return

            if not text1:
                if self.client:
                    await message.channel.send('No playerfile or stat found')
                else:
                    print('No playerfile or stat found')
            else:
                if self.client:
                    text1, text2 = zip(*sorted(zip(text1, text2), reverse=True))
                    shortened_lists = shorten_embed_lists([text2, [str(x) for x in text1]], 2)
                    player_names, results = shortened_lists[0], shortened_lists[1]
                    em = generate_embed_table(
                        ['Players', 'Result'],
                        ['\n'.join(player_names), '\n'.join(results)],
                        True)
                    em.set_author(
                        name=stat_id + ' - Ranking',
                        icon_url='https://redirect.dugged.net:8443/logo_full.png')
                    em.set_footer(text='Total: ' + str(total) + '    |    ' + str(round((total / 1000000), 2)) + ' M')
                    await message.channel.send(embed=em)

                else:
                    print(stat_id + ' Ranking')
                    for item in sorted(zip(text1, text2), reverse=True):
                        print(str(item[0]) + ', ' + item[1])

                    print('Total: ' + str(total) + '    |    ' + str(round((total / 1000000), 2)) + ' M')

        # stat total
        elif len(args) == 2 and args[0] == 'total':
            async with CommandCache.semaphore:
                try:
                    stat_id = 'stat.' + args[1] if not args[1].startswith('stat') else args[1]
                    stat_id = ''.join(get_close_matches(stat_id, self.cache.stat_ids, 1))

                    if stat_id == '':
                        if self.client:
                            await message.channel.send('Invalid stat')
                        else:
                            print('Invalid stat')

                        return

                    total = 0

                    for item in self.cache.uuids:
                        with open(os.path.join(self.stat_folder, convert_uuid(item) + '.json')) as json_data:
                            stats = json.load(json_data)

                            if stat_id in stats:
                                total += stats[stat_id]
                except:
                    if self.client:
                        await message.channel.send('No playerfile or stat found')
                    else:
                        print('No playerfile or stat found')

                    return

            if self.client:
                em = discord.Embed(
                    description='',
                    colour=0x003763)
                em.add_field(
                    name='Result',
                    inline=True,
                    value='Total: ' + str(total) + '    |    ' + str(round((total / 1000000), 2)) + ' M')

                em.set_author(
                    name=stat_id + ' - Total',
                    icon_url='https://redirect.dugged.net:8443/logo_full.png')

                await message.channel.send(embed=em)
            else:
                print('Stat: ' + stat_id)
                print('Total: ' + str(total) + '    |    ' + str(round((total / 1000000), 2)) + ' M')
        else:
            if self.client:
                await message.channel.send('Invalid syntax')
            else:
                print('Invalid syntax')
