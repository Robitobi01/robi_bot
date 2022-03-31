from difflib import get_close_matches

from nbt import nbt

from utils import *
from .baseCommand import BaseCommand


class ScoreboardCommand(BaseCommand):
    command_text = "!!scoreboard"

    def __init__(self, client, command_cache, data_folder):
        super().__init__(client, command_cache)

        self.data_folder = data_folder

    def help(self):
        return ('`' + self.command_text + ' <scoreboard_name>`  **-**  Shows scoreboard ranking\n'
                                          '`' + self.command_text + ' total <scoreboard_name>`  **-**  Shows scoreboard total\n')

    async def process(self, message, args):
        if len(args) == 1:
            nbt_file = nbt.NBTFile(os.path.join(self.data_folder, 'scoreboard.dat'))
            scoreboard_objectives = [tag['Name'].value.casefold() for tag in nbt_file['data']['Objectives']]
            objective_name = ''.join(get_close_matches(args[0], scoreboard_objectives, 1))

            if objective_name == '':
                if self.client:
                    await message.channel.send('Scoreboard not found')
                else:
                    print('Scoreboard not found')

                return

            scoreboard = dict()

            for tag in nbt_file['data']['PlayerScores']:
                if tag['Objective'].value.casefold() == objective_name:
                    scoreboard[tag['Name'].value] = tag['Score'].value

            scoreboard = sorted(scoreboard.items(), key=lambda x: x[1], reverse=True)

            text1 = []
            text2 = []
            total = 0

            for name, amount in scoreboard:
                if not name == 'Total':
                    text1.append(format_name_for_embed(name))
                    text2.append(str(amount))
                    total += amount

            if self.client:
                em = generate_embed_table(
                    ['Players', 'Amount'],
                    ['\n'.join(text1), '\n'.join(text2)],
                    True)
                em.set_author(
                    name='Scoreboard: ' + objective_name,
                    icon_url='https://redirect.dugged.net:8443/logo_full.png')
                em.set_footer(text='Total: ' + str(total) + '    |    ' + str(round(total / 1000000, 2)) + ' M')

                await message.channel.send(embed=em)
            else:
                for name, amount in scoreboard:
                    print('name = ' + name + ', amount = ' + str(amount))

                print('Total: ' + str(total) + '    |    ' + str(round(total / 1000000, 2)) + ' M')

        # scoreboard total
        elif len(args) == 2 and args[0] == 'total':
            nbt_file = nbt.NBTFile(os.path.join(self.data_folder, 'scoreboard.dat'))
            scoreboard_objectives = [tag['Name'].value.casefold() for tag in nbt_file['data']['Objectives']]
            objective_name = ''.join(get_close_matches(args[1], scoreboard_objectives, 1))

            if objective_name == '':
                if self.client:
                    await message.channel.send('Scoreboard not found')
                else:
                    print('Scoreboard not found')

                return

            total = 0

            for tag in nbt_file['data']['PlayerScores']:
                if tag['Objective'].value.casefold() == objective_name:
                    total += tag['Score'].value

            if self.client:
                em = discord.Embed(
                    description='',
                    colour=0x003763)
                em.add_field(
                    name='Total',
                    inline=True,
                    value='`' + str(total) + '    |    ' + str(round(total / 1000000, 2)) + ' M`')
                em.set_author(
                    name='Scoreboard: ' + objective_name,
                    icon_url='https://redirect.dugged.net:8443/logo_full.png')
                await message.channel.send(embed=em)

            else:
                print('Scoreboard: ' + objective_name)
                print('Total: ' + str(total) + '    |    ' + str(round(total / 1000000, 2)) + ' M')
        else:
            if self.client:
                await message.channel.send('Invalid syntax')
            else:
                print('Invalid syntax')
