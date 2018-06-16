from .basecmd import basecmd
import psutil

class HardwareCommand(basecmd):
    command_text = "!!hardware"

    def __init__(self, discord, client, message, command_cache):
        super(HardwareCommand, self).__init__(discord, client, message, command_cache)

    def process(self, args):
        await client.send_message(message.channel, 'The current CPU usage is: **' + str(psutil.cpu_percent(interval=0.5)) + '%**\n The current RAM usage is: **' + str(round(psutil.virtual_memory()[3] / 1073741824, 2)) + 'GB** ')
    def help(self):
        return '`' + self.command_text + '`  **-**  Displays currently used hardware recources\n'
