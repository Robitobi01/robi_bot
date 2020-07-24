from .baseCommand import BaseCommand


class DeleteCommand(BaseCommand):
    command_text = "!!delete"

    def help(self):
        return '`' + self.command_text + ' <n>`  **-**  Deletes the last n messages\n'

    async def process(self, message, args):
        if str(message.author.id) in self.cache.admin_list:
            if len(args) != 1 or args[0] == '' or not args[0].isdigit():
                await message.channel.send('Invalid number')
            elif int(args[0]) > 100:
                await message.channel.send('Not more than 100 messages can be deleted at the same time')
            else:
                await message.channel.delete_messages(await message.channel.history(limit=int(args[0])).flatten())
        else:
            await message.channel.send('You dont have permissions to do that!')
