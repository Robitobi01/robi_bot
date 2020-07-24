import discord
import os

from commands import *

client = discord.Client()

# Directories
#FOLDER = os.path.dirname(__file__)
FOLDER = '/home/robi/Desktop/code/robi_bot/servers/'

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

with open('token.txt', 'r') as f:
    token = f.read()


command_cache = commandCache.CommandCache(STAT_FOLDER, True)

commands = dict()
commands[benchmarkCommand.BenchmarkCommand.command_text] = benchmarkCommand.BenchmarkCommand(client, command_cache, STAT_FOLDER)
commands[deleteCommand.DeleteCommand.command_text] = deleteCommand.DeleteCommand(client, command_cache)
commands[hardwareCommand.HardwareCommand.command_text] = hardwareCommand.HardwareCommand(client, command_cache)
commands[helpCommand.HelpCommand.command_text] = helpCommand.HelpCommand(client, command_cache, commands)
commands[listCommand.ListCommand.command_text] = listCommand.ListCommand(client, command_cache, minecraft_ip, minecraft_port, os.path.dirname(__file__), PLAYERDATA_FOLDER)
commands[playtimeCommand.PlaytimeCommand.command_text] = playtimeCommand.PlaytimeCommand(client, command_cache, SURVIVAL_FOLDER, STAT_FOLDER)
commands[reloadCommand.ReloadCommand.command_text] = reloadCommand.ReloadCommand(client, command_cache, commands, STAT_FOLDER)
commands[scoreboardCommand.ScoreboardCommand.command_text] = scoreboardCommand.ScoreboardCommand(client, command_cache, DATA_FOLDER)
commands[statCommand.StatCommand.command_text] = statCommand.StatCommand(client, command_cache, STAT_FOLDER)
commands[statusCommand.StatusCommand.command_text] = statusCommand.StatusCommand(client, command_cache)
commands[structureCommand.StructureCommand.command_text] = structureCommand.StructureCommand(client, command_cache, STRUCTURE_FOLDER)
commands[synchronizeCommand.SynchronizeCommand.command_text] = synchronizeCommand.SynchronizeCommand(client, command_cache, DATA_FOLDER, STAT_FOLDER)
commands[tpsCommand.TpsCommand.command_text] = tpsCommand.TpsCommand(client, command_cache, SURVIVAL_FOLDER)
commands[worldsizeCommand.WorldsizeCommand.command_text] = worldsizeCommand.WorldsizeCommand(client, command_cache, SURVIVAL_FOLDER, OVERWORLD_FOLDER, NETHER_FOLDER, END_FOLDER)

initialized = False

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game(name='!!help', type=discord.ActivityType.listening))
    global initialized
    # on_ready can be called more than once so only run !!reload if this is the first time.
    if not initialized:
        print('reloading')
        initialized = True
        await commands[reloadCommand.ReloadCommand.command_text].process(None, None, force_reload=True)
    print('robi_bot is connected with ' + client.user.name)


@client.event
async def on_message(message):
    args = message.content.strip().lower().split(" ")

    if args:
        command_text = args[0]
        args = args[1:]
        if command_text in commands:
            await commands[command_text].process(message, args)


try:
    client.run(token)
except:
   print('A connection error occured')
