from commands import *

from discord.ext.commands import Bot

import discord
import os

# Directories
FOLDER = os.path.dirname(__file__)

CREATIVE_FOLDER = os.path.join(FOLDER, 'Creative', 'Creative')
SURVIVAL_FOLDER = os.path.join(FOLDER, 'Survival', 'Survival')

# Creative Directories
STRUCTURE_FOLDER = os.path.join(CREATIVE_FOLDER, 'structures')

# Survival Directories
DATA_FOLDER = os.path.join(SURVIVAL_FOLDER, 'data')
END_FOLDER = os.path.join(SURVIVAL_FOLDER, 'DIM1', 'region')
NETHER_FOLDER = os.path.join(SURVIVAL_FOLDER, 'DIM-1', 'region')
OVERWORLD_FOLDER = os.path.join(SURVIVAL_FOLDER, 'region')
PLAYERDATA_FOLDER = os.path.join(SURVIVAL_FOLDER, 'playerdata')
STAT_FOLDER = os.path.join(SURVIVAL_FOLDER, 'stats')

# Create missing directories
if not os.path.exists(STRUCTURE_FOLDER):
    os.makedirs(STRUCTURE_FOLDER)

# External stored data hidden from code
with open('minecraft_server.txt', 'r') as f:
    minecraft_ip, minecraft_port = f.read().split(':', 1)
    minecraft_port = int(minecraft_port)

with open('token.txt','r') as f:
    token = f.read()

bot = Bot(command_prefix = "!!")
command_cache = commandCache.CommandCache(STAT_FOLDER, False)

commands = dict()
commands[benchmarkCommand.BenchmarkCommand.command_text] = benchmarkCommand.BenchmarkCommand(bot, command_cache, STAT_FOLDER)
commands[hardwareCommand.HardwareCommand.command_text] = hardwareCommand.HardwareCommand(bot, command_cache)
commands[helpCommand.HelpCommand.command_text] = helpCommand.HelpCommand(bot, command_cache, commands)
commands[listCommand.ListCommand.command_text] = listCommand.ListCommand(bot, command_cache, minecraft_ip, minecraft_port, FOLDER, PLAYERDATA_FOLDER)
commands[playtimeCommand.PlaytimeCommand.command_text] = playtimeCommand.PlaytimeCommand(bot, command_cache, SURVIVAL_FOLDER, STAT_FOLDER)
commands[reloadCommand.ReloadCommand.command_text] = reloadCommand.ReloadCommand(bot, command_cache, commands, STAT_FOLDER)
commands[scoreboardCommand.ScoreboardCommand.command_text] = scoreboardCommand.ScoreboardCommand(bot, command_cache, DATA_FOLDER)
commands[statCommand.StatCommand.command_text] = statCommand.StatCommand(bot, command_cache, STAT_FOLDER)
commands[statusCommand.StatusCommand.command_text] = statusCommand.StatusCommand(bot, command_cache)
commands[structureCommand.StructureCommand.command_text] = structureCommand.StructureCommand(bot, command_cache, STRUCTURE_FOLDER)
commands[synchronizeCommand.SynchronizeCommand.command_text] = synchronizeCommand.SynchronizeCommand(bot, command_cache, DATA_FOLDER)
commands[tpsCommand.TpsCommand.command_text] = tpsCommand.TpsCommand(bot, command_cache, SURVIVAL_FOLDER)
commands[worldsizeCommand.WorldsizeCommand.command_text] = worldsizeCommand.WorldsizeCommand(bot, command_cache, SURVIVAL_FOLDER, OVERWORLD_FOLDER, NETHER_FOLDER, END_FOLDER)

@bot.event
async def on_ready():
    await bot.change_presence(game = discord.Game(name = '!!help'))

    if 'initialized' not in locals():
        initialized = True
        # on_ready can be called more than once so only run !!reload if this is the first time.
        await commands[reloadCommand.ReloadCommand.command_text].process(None, None, force_reload = True)

    print("Bot is connected")

@bot.event
async def on_message(message):
    args = message.content.strip().lower().split(" ")

    if args != []:
        command_text = args[0]
        args = args[1:]

        if command_text in commands:
            await commands[command_text].process(message, args)

bot.run(token)
