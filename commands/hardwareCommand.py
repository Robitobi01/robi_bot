import math
import psutil
import shutil

from .baseCommand import BaseCommand


class HardwareCommand(BaseCommand):
    command_text = "!!hardware"

    def __init__(self, client, command_cache):
        super().__init__(client, command_cache)

    def help(self):
        return '`' + self.command_text + '`  **-**  Displays currently used hardware recources\n'

    async def process(self, message, args):
        cpu_percentage = str(psutil.cpu_percent(interval=0.5))
        ram_usage = str(round(psutil.virtual_memory()[3] / 1073741824, 2))
        total, used, free = shutil.disk_usage("/")
        avaliable = math.ceil(used / ((used + free) / 100))

        if self.client:
            await message.channel.send('The current CPU usage is: **' + cpu_percentage +
                                       '%**\nThe current RAM usage is: **' + ram_usage +
                                       'GB**\nThe current HDD usage is: **' + str(used // (2**30)) + 'GB/' + str(used // (2**30) + free // (2**30)) + 'GB**')
        else:
            print('The current CPU usage is: **' + cpu_percentage + '%**\nThe current RAM usage is: **' +
                  ram_usage + 'GB** ')
