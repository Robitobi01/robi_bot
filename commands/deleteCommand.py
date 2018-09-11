from .baseCommand import BaseCommand
import discord

class DeleteCommand(BaseCommand):
    command_text = "!!delete"

    def help(self):
        return '`' + self.command_text + ' <n>`  **-**  Deletes the last n messages\n'

    async def process(self, message, args):
        if message.author.id in self.cache.admin_list:
            if len(args) != 1 or args[0] == '' or not args[0].isdigit():
                await self.bot.send_message(message.channel, 'Invalid number')
            elif int(args[0]) > 50:
                await self.bot.send_message(message.channel, 'Not more than 50 messages can be deleted at the same time')
            else:
                history = []
                async for msg in self.bot.logs_from(message.channel, limit = int(args[0])):
                    history.append(msg)
                if len(history) == 1:
                    await self.bot.delete_message(history[0])
                else:
                    await self.bot.delete_messages(history)
        else:
            await self.bot.send_message(message.channel, 'You dont have permissions to do that!')
