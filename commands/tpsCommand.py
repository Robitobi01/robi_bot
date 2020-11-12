import os

from nbt import nbt

from .baseCommand import BaseCommand


class TpsCommand(BaseCommand):
    command_text = "!!tps"

    def __init__(self, client, command_cache, survival_folder):
        super().__init__(client, command_cache)

        self.survival_folder = survival_folder

    def help(self):
        return '`' + self.command_text + '`  **-**  Shows average TPS from the last 45 seconds\n'

    async def process(self, message, args):
        last_played = []

        for file in ['level.dat', 'level.dat_old']:
            last_played.append(nbt.NBTFile(os.path.join(self.survival_folder, file))['Data']['LastPlayed'].value)

        tps = 45.0 / ((last_played[0] - last_played[1]) / 1000.0) * 20.0

        if tps > 20.0:
            tps = 20.0
        if tps < 0.0:
            tps = 0.0

        if self.client:
            await message.channel.send('The current TPS is: **' + str(
                round(tps, 2)) + '** | TPS only updates roughly every 45 seconds')
        else:
            print('The current TPS is: **' + str(round(tps, 2)) + '** | TPS only updates roughly every 45 seconds')
