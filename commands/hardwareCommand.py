from .baseCommand import BaseCommand

import psutil

class HardwareCommand(BaseCommand):
    command_text = "!!hardware"

    def __init__(self, bot, command_cache):
        super().__init__(bot, command_cache)

    def help(self):
        return '`' + self.command_text + '`  **-**  Displays currently used hardware recources\n'

    async def process(self, message, args):
        cpu_percentage = str(psutil.cpu_percent(interval = 0.5))
        ram_usage = str(round(psutil.virtual_memory()[3] / 1073741824, 2))

        if self.bot:
            await self.bot.send_message(message.channel, 'The current CPU usage is: **' + cpu_percentage + '%**\nThe current RAM usage is: **' + ram_usage + 'GB** ')
        else:
            print('The current CPU usage is: **' + cpu_percentage + '%**\nThe current RAM usage is: **' + ram_usage + 'GB** ')
