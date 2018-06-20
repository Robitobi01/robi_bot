from utils import *

from threading import Lock

import asyncio
import glob
import json
import os

# Class to get away from using global variables in commands which is a PITA with python modules
class CommandCache(object):
    semaphore = asyncio.Semaphore()

    def __init__(self, stat_folder, is_online):
        self.stat_folder = stat_folder
        self.is_online = is_online

    async def load_files(self):
        if not self.is_online:
            await asyncio.sleep(5)

        temp_admin_list = []
        temp_names = []
        temp_uuids = []
        temp_stat_ids = []

        # load stat names
        with open('stat_ids.txt', 'r') as stream:
            buffer = stream.read().translate({ ord(c): None for c in '"' })

        temp_stat_ids = buffer.split(',')

        # load discord id's with administrator permissions
        with open('admin_list.txt', 'r') as stream:
            buffer = stream.read().translate({ ord(c): None for c in '"' }).rstrip()

        temp_admin_list = buffer.split(',')

        # caching usernames to uuid
        files = glob.glob(os.path.join(self.stat_folder, '*.json'))

        for item in files:
            filename = item[-41:]
            temp_uuids.append(convert_uuid(filename.split('.json', 1)[0]))

        #if self.is_online:
        for item in temp_uuids:
            try:
                # http://wiki.vg/Mojang_API
                url = 'https://sessionserver.mojang.com/session/minecraft/profile/' + item

                response = requests.get(url)
                response.raise_for_status

                response = json.loads(response.text)
                value = response['properties'][0]['value']
                textures = json.loads(base64.b64decode(value).decode('UTF-8'))

                temp_names.append(textures['profileName'])
                #print(textures['profileName'])
            except:
                pass
        # else:
        #     temp_names.append('TIGuardian')
        #     temp_names.append('TheBikerExtreme')
        #     temp_names.append('KFabian97')
        #     temp_names.append('Gamemode3')
        #     temp_names.append('SpoonMor')
        #     temp_names.append('fougu44')
        #     temp_names.append('JeWe37')
        #     temp_names.append('Rays')
        #     temp_names.append('PrivateChankey')
        #     temp_names.append('RidPMC')
        #     temp_names.append('Syndicate101')
        #     temp_names.append('BlueBarret99')
        #     temp_names.append('veirden')

        # Only modify the cache values after getting the semaphore
        async with CommandCache.semaphore:
            self.admin_list = temp_admin_list
            self.names = temp_names
            self.uuids = temp_uuids
            self.stat_ids = temp_stat_ids
