import discord

from .baseCommand import BaseCommand


class HelpCommand(BaseCommand):
    command_text = "!!help"

    def __init__(self, client, command_cache, commands):
        super().__init__(client, command_cache)

        self.commands = commands

    async def process(self, message, args):
        if args == '' or len(args) > 1 or not ''.join(args).isdigit():
            args = 1
        else:
            args = int(''.join(args))
        all_help_texts = []
        help_text = []
        avaliable_pages = [1]
        if args not in avaliable_pages:
            help_text.append('This page doesnt exist yet!')

        for k in self.commands.keys():
            if k != self.command_text:
                all_help_texts.append(self.commands[k].help())

        for l in range(7 * (args - 1), 7 * args):
            if l < len(all_help_texts):
                help_text.append(all_help_texts[l])

        help_text = ''.join(help_text)

        if self.client:
            em = discord.Embed(
                description='This bot provides general information about the Dugged server. \nThe command prefix is **!!**.\nAddition `[A]` is only possible for administrators\nAdd number of page as argument to show other pages',
                colour=0x003763)
            em.add_field(name='Commands - Page: ' + str(args) + ' / ' + str(
                int(len(all_help_texts) / 7) + (len(all_help_texts) % 7 > 0)), inline=False, value=help_text)
            em.set_author(name='Help', url='https://github.com/Robitobi01/robi_bot',
                          icon_url='https://redirect.dugged.net:8443/logo_full.png')
            em.set_footer(text='Made by Robitobi01 and veirden',
                          icon_url='https://cdn.discordapp.com/avatars/400833990359253002/74b8b6de441bce1a59f9c4ac74f666e6.png')

            await message.channel.send(embed=em)
        else:
            print(help_text)
