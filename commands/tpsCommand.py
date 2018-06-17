from .baseCommand import BaseCommand

from nbt import nbt

import discord
import os

class TpsCommand(BaseCommand):
    command_text = "!!tps"

    def __init__(self, discord, client, message, command_cache, survival_folder):
        super().__init__(discord, client, message, command_cache)

        self.survival_folder = survival_folder

    def help(self):
        return '`' + self.command_text + '`  **-**  Shows average TPS from the last 45 seconds\n'

    async def process(self, args):
        last_played = []

        for file in ['level.dat', 'level.dat_old']:
            last_played.append(nbt.NBTFile(os.path.join(self.survival_folder, file))['Data']['LastPlayed'].value)
        
        tps = 45.0 / ((last_played[0] - last_played[1]) / 1000.0) * 20.0
        
        if tps > 20.0: tps = 20.0
        if tps < 0.0: tps = 0.0
        
        if self.client == None:
            print('The Current TPS is: **' + str(round(tps, 2)) + '** | TPS only updates roughly every 45 seconds')
        else:
            await self.client.send_message(self.message.channel, 'The Current TPS is: **' + str(round(tps, 2)) + '** | TPS only updates roughly every 45 seconds')
