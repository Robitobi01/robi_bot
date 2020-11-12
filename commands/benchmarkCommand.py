import datetime
import time
from difflib import get_close_matches

from utils import *
from .baseCommand import BaseCommand
from .commandCache import CommandCache


class StatData(object):
    def __init__(self, uuid, name, start_value, start_time):
        self.uuid = uuid
        self.name = name
        self.start_value = start_value
        self.start_time = start_time
        self.stop_value = 0
        self.stop_time = 0.0

    def calc_delta(self):
        return self.stop_value - self.start_value

    def calc_rate_per_hour(self):
        return int((self.stop_value - self.start_value) / ((self.stop_time - self.start_time) / 3600))


class Benchmark(object):
    def __init__(self, stat_id, stat_data):
        self.stat_id = stat_id
        self.stat_data = stat_data
        self.start_time = time.time()

    def stop(self):
        self.end_time = time.time()

    def elapsed_time(self, current_time=None):
        if current_time:
            return current_time - self.start_time
        else:
            return self.end_time - self.start_time


class BenchmarkCommand(BaseCommand):
    command_text = "!!benchmark"

    def __init__(self, client, command_cache, stat_folder):
        super().__init__(client, command_cache)

        self.stat_folder = stat_folder
        self.benchmarks = dict()

    def help(self):
        return ('`' + self.command_text + ' start <stat>`  **-**  Starts a benchmark for given stat\n' +
                '`' + self.command_text + ' stop <stat>`  **-**  Stops benchmark and displays results\n' +
                '`' + self.command_text + ' list`  **-**  Displays list of running benchmarks\n')

    async def process(self, message, args):
        # start
        if len(args) == 2 and args[0] == 'start':
            async with CommandCache.semaphore:
                try:
                    stat_id = 'stat.' + args[1] if not args[1].startswith('stat') else args[1]
                    stat_id = ''.join(get_close_matches(stat_id, self.cache.stat_ids, 1))

                    if stat_id == '':
                        if self.client:
                            await message.channel.send('Invalid stat')
                        else:
                            print('Invalid stat')

                    if stat_id in self.benchmarks:
                        if self.client:
                            await message.channel.send('Benchmark already started for: ' + stat_id)
                        else:
                            print('Benchmark already running for: ' + stat_id)

                        return

                    stat_data = []

                    for uuid in self.cache.uuids:
                        name = self.cache.names[self.cache.uuids.index(uuid)]

                        with open(os.path.join(self.stat_folder, convert_uuid(uuid) + '.json')) as json_data:
                            stats = json.load(json_data)

                        value = stats[stat_id] if stat_id in stats else 0
                        stat_data.append(StatData(uuid, name, value, time.time()))
                except:
                    if self.client:
                        await message.channel.send('Invalid stat')
                    else:
                        print('Invalid stat')

                    return

            self.benchmarks[stat_id] = Benchmark(stat_id, stat_data)

            if self.client:
                await message.channel.send('Benchmark started for: `' + stat_id + "`")
                await message.channel.send('Stop Command:\n!!benchmark stop `' + stat_id + "`")
                await message.channel.send('**Warning:** Benchmarks need to run atleast 1 minute to detect any changes')
            else:
                print('Benchmark started for: ' + stat_id)
                print('Stop Command: !!benchmark stop ' + stat_id)
                print('**Warning:** Benchmarks need to run atleast 1 minute to detect any changes')

        # stop
        elif len(args) == 2 and args[0] == 'stop':
            async with CommandCache.semaphore:
                try:
                    stat_id = 'stat.' + args[1] if not args[1].startswith('stat') else args[1]
                    stat_id = ''.join(get_close_matches(stat_id, self.cache.stat_ids, 1))

                    if stat_id == '':
                        if self.client:
                            await message.channel.send('Invalid stat')
                        else:
                            print('Invalid stat')
                except:
                    if self.client:
                        await message.channel.send('Invalid stat')
                    else:
                        print('Invalid stat')

                    return

            if not stat_id in self.benchmarks:
                if self.client:
                    await message.channel.send('No running benchmark found for: ' + stat_id)
                else:
                    print('No running benchmark found for: ' + stat_id)

                return

            benchmark = self.benchmarks[stat_id]

            for item in benchmark.stat_data:
                with open(os.path.join(self.stat_folder, convert_uuid(item.uuid) + '.json')) as json_data:
                    stats = json.load(json_data)

                item.stop_value = stats[stat_id] if stat_id in stats else 0
                item.stop_time = time.time()

            benchmark.stop()

            text1 = []
            text2 = []
            text3 = []

            for item in benchmark.stat_data:
                delta = item.calc_delta()

                if delta > 0:
                    text1.append(format_name_for_embed(item.name))
                    text2.append(str(delta))
                    text3.append(str(item.calc_rate_per_hour()))

            if text1:
                if self.client:
                    em = generate_embed_table(
                        ['Player', 'Delta', 'Per Hour'],
                        ['\n'.join(text1), '\n'.join(text2), '\n'.join(text3)],
                        True)
                    em.set_author(name='Benchmark',
                                  icon_url='https://cdn.discordapp.com/icons/336592624624336896/31615259cca237257e3204767959a967.png')
                    em.set_footer(
                        text='Total Time: ' + str(datetime.timedelta(seconds=round(benchmark.elapsed_time(), 0))))

                    await message.channel.send(embed=em)
                else:
                    print('Player, Delta, Per Hour')

                    for item in zip(text1, text2, text3):
                        print(item[0] + ', ' + item[1] + ', ' + item[2])

            else:
                if self.client:
                    await message.channel.send('No changes detected, stop being lazy!')
                else:
                    print('No changes detected, stop being lazy!')

            # results have been successfully reported so remove it from the list
            del self.benchmarks[stat_id]
        # list
        elif len(args) == 1 and args[0] == 'list':
            current_time = time.time()

            text1 = []
            text2 = []

            for k, v in self.benchmarks.items():
                text1.append(format_name_for_embed(k))
                text2.append(str(datetime.timedelta(seconds=round(v.elapsed_time(current_time), 0))))

            if not text1:
                if self.client:
                    await message.channel.send('No benchmarks currently running')
                else:
                    print('No benchmarks currently running')

            else:
                if self.client:
                    em = generate_embed_table(
                        ['Player', 'Running Time'],
                        ['\n'.join(text1), '\n'.join(text2)],
                        True)
                    em.set_author(name='Benchmark List',
                                  icon_url='https://cdn.discordapp.com/icons/336592624624336896/31615259cca237257e3204767959a967.png')
                    em.set_footer(text='Active: ' + str(len(self.benchmarks.keys())))
                    await message.channel.send(embed=em)
                else:
                    print('Stat, Running Time')
                    for item in zip(text1, text2):
                        print(item[0] + ', ' + item[1])

        else:
            if self.client:
                await message.channel.send('Invalid syntax')
            else:
                print('Invalid syntax')
