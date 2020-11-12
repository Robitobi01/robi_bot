from json_minify import json_minify
from mcstatus import MinecraftServer
from nbt import nbt

from utils import *
from .baseCommand import BaseCommand
from .commandCache import CommandCache


def first(iterable, condition=lambda x: True):
    for i in iterable:
        if condition(i):
            return i


class KnownLocation:
    # Contains information such as name and 2D bounding box for a known location on the Dugged server.

    @staticmethod
    def parse(values):
        dimension, location_name, x1, z1, x2, z2 = values

        # Skip locations with incomplete coords
        if x1 != 0 and z1 != 0 and x2 != 0 and z2 != 0:
            min_x = x1 if x1 < x2 else x2
            min_z = z1 if z1 < z2 else z2
            max_x = x2 if x2 > x1 else x1
            max_z = z2 if z2 > z1 else z1

            return KnownLocation(dimension, location_name, min_x, min_z, max_x, max_z)
        return None

    def __init__(self, dimension, location_name, min_x, min_z, max_x, max_z):
        self.dimension = dimension
        self.location_name = location_name
        self.min_x = min_x
        self.min_z = min_z
        self.max_x = max_x
        self.max_z = max_z

    def is_contained(self, x, z):
        # Determine whether the point is contained in the locations 2D bounding box
        return self.min_x <= x <= self.max_x and self.min_z <= z <= self.max_z


class ListCommand(BaseCommand):
    command_text = "!!list"
    dimensions = {-1: 'N', 0: 'O', 1: 'E'}
    known_locations = {-1: [], 0: [], 1: []}

    def __init__(self, client, command_cache, minecraft_ip, minecraft_port, current_folder, playerdata_folder):
        super().__init__(client, command_cache)

        self.minecraft_ip = minecraft_ip
        self.minecraft_port = minecraft_port
        self.current_folder = current_folder
        self.playerdata_folder = playerdata_folder

    def help(self):
        return '`' + self.command_text + '`  **-**  Displays currently online players and their dimension\n'

    async def load_files(self):
        file = os.path.join(self.current_folder, 'known_locations.json')

        with open(file, 'r') as f:
            json_data = json.loads(json_minify(f.read(None)))

            for entry in json_data:
                known_location = KnownLocation.parse(entry)

                if known_location is not None:
                    ListCommand.known_locations[known_location.dimension].append(known_location)

    async def process(self, message, args):
        try:
            server = MinecraftServer(self.minecraft_ip, self.minecraft_port)
            query = server.query()

            if query.players.online > 0:
                online_list = query.players.names
                text1 = []

                async with CommandCache.semaphore:
                    for item in online_list:
                        nbt_file = nbt.NBTFile(os.path.join(self.playerdata_folder, convert_uuid(
                            self.cache.uuids[self.cache.names.index(item)]) + '.dat'))
                        # nbt_file = nbt.NBTFile(os.path.join(self.playerdata_folder, '33804744-b7a3-4816-8ddc-02ac2d8c80cf.dat'))

                        dimension = nbt_file['Dimension'].value
                        x, y, z = (int(i.value) for i in nbt_file['Pos'])
                        known_location = first(ListCommand.known_locations[dimension], lambda i: i.is_contained(x, z))

                        text1.append(
                            '**' + format_name_for_embed(item) + '** (' + ListCommand.dimensions.get(dimension, '?') + (
                                '' if known_location is None else '@*' + known_location.location_name + '*') + ')')

                if self.client:
                    await message.channel.send('Players: ' + ', '.join(text1))
                else:
                    print('Players: ' + ', '.join(text1))
            else:
                if self.client:
                    await message.channel.send('No Player is currently online :sob:')
                else:
                    print('No Player is currently online')
        except Exception as e:
            if self.client:
                await message.channel.send('An error occured while trying to reach the server: ' + e)
            else:
                print('An error occured while trying to reach the server:' + e)
