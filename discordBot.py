from discord.ext.commands import Bot
from discord.ext import commands
from difflib import get_close_matches
from mcstatus import MinecraftServer
from nbt import *
import requests
import discord
import glob
import asyncio
import io
import json
import time
import urllib.request
import datetime
import os
import base64


Client = discord.Client()
client = commands.Bot(command_prefix = "!!")


FOLDER = os.path.dirname(__file__)
CREATIVE_FOLDER = os.path.join(os.path.join(FOLDER, 'Creative'), 'Creative')
SURVIVAL_FOLDER =os.path.join(os.path.join(FOLDER, 'Survival'), 'Survival')
STAT_FOLDER = os.path.join(SURVIVAL_FOLDER,'stats')
DATA_FOLDER = os.path.join(SURVIVAL_FOLDER,'data')
PLAYERDATA_FOLDER = os.path.join(SURVIVAL_FOLDER,'playerdata')
STRUCTURE_FOLDER = os.path.join(CREATIVE_FOLDER, 'structures')
OVERWORLD_FOLDER = os.path.join(SURVIVAL_FOLDER, 'region')
NETHER_FOLDER = os.path.join(os.path.join(SURVIVAL_FOLDER, 'DIM-1'), 'region')
END_FOLDER = os.path.join(os.path.join(SURVIVAL_FOLDER, 'DIM1'), 'region')

if not os.path.exists(STRUCTURE_FOLDER):
    os.makedirs(STRUCTURE_FOLDER)

#External stored data hidden from code
ip = open('ip.txt','r')
ip = ip.read()
token = open('token.txt','r')
token = token.read()

#global variables and lists
uuids = []                      #uuids from stat files
names = []                      #names converted from uuid
stat_list = []                  #list of stat objectives
skins = []                      #links to skin on mojang servers
benchmark_results = []          #contains stats from starting benchmark
benchmark_stat = ""             #contains the benchmarked stat objective
benchmark_start_time = ""       #contains benchmark starting time

#toggles '-' in given uuid
def convert_uuid(uuid):
    if '-' in uuid:
        return uuid.split('.json', 1)[0].translate({ord(i):None for i in '-'})
    else:
        return uuid[:8] + '-' + uuid[8:12] + '-' + uuid[12:16] + '-' + uuid[16:20] + '-' + uuid[20:]

#returns the total size of all files in given location
def get_size(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

#returns all names in the namehistory of a uuid without duplicates or the current name
def get_name_history(uuid):
    url = "https://api.mojang.com/user/profiles/" + uuid + "/names"
    response = requests.get(url)
    response.raise_for_status
    response = json.loads(response.text)
    current_name = response[-1]['name']
    del response[-1]
    if response != []:
        for name in response:
            if name['name'] == current_name:
                del response[response.index(name)]
    return response

#loads all files and performs uuid & username caching
def load_files():
    #caching stat objectives
    global uuids, names, skins, stat_list
    uuids = []
    names = []
    stat_list = []
    f = open('statslist.txt','r')
    f = f.read().translate({ord(c): None for c in '"'})
    s = f.split(',')
    for item in s:
        stat_list.append(item)

    #caching usernames to uuid
    files = glob.glob(str(os.path.join(STAT_FOLDER, '*.json')))
    for item in files:
        filename = item[-41:]
        uuids.append(convert_uuid(filename.split('.json', 1)[0]))
    for item in uuids:
        try:
            url = "https://sessionserver.mojang.com/session/minecraft/profile/" + item
            response = requests.get(url)
            response.raise_for_status
            response = json.loads(response.text)
            response = json.loads(base64.b64decode(response['properties'][0]['value']))
            names.append(response['profileName'])
        except:
            pass


@client.event
async def on_ready():
    load_files()
    await client.change_presence(game = discord.Game(name = '!!help'))
    print("Bot is connected")

@client.event
async def on_message(message):

    #!!reload
    if message.content.startswith('!!reload'):
        await client.send_message(message.channel, '**Warning:** all files reloading, this might take a moment')
        starttime = time.time()
        load_files()
        em = discord.Embed(
            description = 'Reloaded: **' + str(len(uuids)) + '** files',
            colour = 0x003763)
        em.set_author(name = 'File Reload', icon_url = 'https://cdn.discordapp.com/icons/336592624624336896/31615259cca237257e3204767959a967.png')
        em.set_footer(text = 'Time: ' + str(round(time.time() - starttime, 2)) + 's')
        await client.send_message(message.channel, embed = em)


    #!!stat player NAME STAT  |  stats list STAT
    elif message.content.startswith('!!stat'):
            args = message.content.split(" ")
            #stat player
            if len(args) == 4 and args[1] == 'player':
                try:
                    name = ''.join(get_close_matches(args[2], names, 1))
                    uuid = convert_uuid(uuids[names.index(name)])
                    try:
                        with open(os.path.join(STAT_FOLDER, uuid + '.json')) as json_data:
                            stats = json.load(json_data)
                        stat = ''.join(get_close_matches('stat.' + args[3], stat_list, 1))
                        try:
                            stat_result = str(stats[stat])
                        except:
                            stat_result = str(0)
                        em = discord.Embed(
                            description = '',
                            colour=0x003763)
                        em.add_field(
                            name = 'Stat',
                            inline = True,
                            value = stat)
                        em.add_field(
                            name = 'Result',
                            inline = True,
                            value = stat_result)
                        em.set_author(name = name + ' - Statistics', icon_url = 'https://crafatar.com/avatars/' + uuid)
                        await client.send_message(message.channel, embed = em)
                    except:
                        await client.send_message(message.channel, 'No playerfile or stat found')
                except:
                    await client.send_message(message.channel, 'Invalid username')
            #stat list
            elif len(args) == 3 and args[1] == 'list':
                try:
                    stat = ''.join(get_close_matches('stat.' + args[2], stat_list, 1))
                    text1 = []
                    text2 = []
                    total = 0
                    for item in uuids:
                        with open(os.path.join(STAT_FOLDER, convert_uuid(item) + '.json')) as json_data:
                            stats = json.load(json_data)
                            try:
                                text1.append(stats[stat])
                                text2.append(names[uuids.index(item)])
                                total += stats[stat]
                            except:
                                pass
                    text1, text2 = zip(*sorted(zip(text1, text2)))
                    if not text1 == []:
                        em = discord.Embed(
                            description = '',
                            colour = 0x003763)
                        em.add_field(
                            name = 'Players',
                            inline = True,
                            value = '\n'.join(text2[::-1]))
                        em.add_field(
                            name = 'Result',
                            inline = True,
                            value = '\n'.join(str(x) for x in text1[::-1]))
                        em.set_author(name = stat + ' - Ranking', icon_url = 'https://cdn.discordapp.com/icons/336592624624336896/31615259cca237257e3204767959a967.png')
                        em.set_footer(text = 'Total: ' + str(total) + '    |    ' + str(round((total / 1000000), 2)) + ' M')
                        await client.send_message(message.channel, embed = em)
                except:
                    await client.send_message(message.channel, 'No playerfile or stat found')
            else:
                await client.send_message(message.channel, 'Invalid syntax')


    #!!scoreboard NAME
    elif message.content.startswith('!!scoreboard'):
            nbtfile = nbt.NBTFile(os.path.join(DATA_FOLDER, 'scoreboard.dat'), 'rb')
            args = message.content.split(" ")
            scoreboard_objectives = []
            for tag in nbtfile['data']['Objectives']:
                scoreboard_objectives.append(str(tag["Name"]))
            if len(args) == 2:
                objective_name = get_close_matches(args[1], scoreboard_objectives, 1)
                text1 = []
                text2 = []
                total = 0
                if not objective_name == []:
                    scoreboard = dict()
                    for tag in nbtfile["data"]["PlayerScores"]:
                      if str(tag["Objective"]) == ''.join(objective_name):
                        scoreboard[str(tag["Name"])] = int(str(tag["Score"]))
                    scoreboard = sorted(scoreboard.items(), key=lambda x:x[1])
                    scoreboard.reverse()
                    for item in scoreboard:
                        name, amount = item
                        if not name == 'Total':
                            text1.append(name)
                            text2.append(str(amount))
                            total += amount
                    em = discord.Embed(
                        description = '',
                        colour = 0x003763)
                    em.add_field(
                        name = 'Players',
                        inline = True,
                        value = '\n'.join(text1))
                    em.add_field(
                        name = 'Amount',
                        inline = True,
                        value = '\n'.join(text2))
                    em.set_author(name = 'Scoreboard: ' + ''.join(objective_name), icon_url = 'https://cdn.discordapp.com/icons/336592624624336896/31615259cca237257e3204767959a967.png')
                    em.set_footer(text = 'Total: ' + str(total) + '    |    ' + str(round((total / 1000000), 2)) + ' M')
                    await client.send_message(message.channel, embed = em)
                else:
                    await client.send_message(message.channel, 'Scoreboard not found')
            else:
                await client.send_message(message.channel, 'Invalid syntax')


    #!!help
    elif message.content.startswith('!!help'):
        em = discord.Embed(
            description = 'This bot provides general information about the Dugged server. \nThe command prefix is **!!**.\n ',
            colour = 0x003763)
        em.add_field(
            name = 'Commands',
            inline = False,
            value = (
                    '`!!reload`  **-**  Reloads all files\n'
                    '`!!help`  **-**  Shows this page\n'
                    '`!!worldsize`  **-**  Shows current worldsize\n'
                    '`!!tps`  **-**  Shows average TPS from the last 45 seconds\n'
                    '`!!list`  **-**  Displays currently online players and their dimension\n'
                    '`!!stat player <user_name> <stat_name>`  **-**  Shows statistics value\n'
                    '`!!stat list <stat_name>`  **-**  Shows statistics ranking\n'
                    '`!!structure <file[ATTACHED]>`  **-**  Uploads structure file to creative\n'
                    '`!!scoreboard <scoreboard_name>`  **-**  Displays scoreboard\n'
                    '`!!benchmark <start> <stat_name>`  **-**  Starts a benchmark for given stat\n'
                    '`!!benchmark <stop>`  **-**  Displays benchmark results\n'
                    ))
        em.set_author(name = 'Help',  url = 'https://twitter.com/Robitobi01', icon_url = 'https://cdn.discordapp.com/icons/336592624624336896/31615259cca237257e3204767959a967.png')
        em.set_footer(text = 'Made by Robitobi01', icon_url = 'https://pbs.twimg.com/profile_images/924434100441755649/MZOP8WK7.jpg')
        await client.send_message(message.channel, embed = em)


    #!!structure FILE[attached]
    elif message.content.startswith('!!structure'):
        data = message.attachments
        url = data[0]['url']
        filename = data[0]['filename']
        filesize = str(data[0]['size'])
        if filename.rsplit('.', 1)[1] == 'nbt':
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(req)
            response = response.read()
            f = open(os.path.join(STRUCTURE_FOLDER, filename), 'wb')
            f.write(response)
            f.close
            em = discord.Embed(
                description = 'Filename: ' + filename,
                colour = 0x003763)
            em.set_author(name = 'Structure file uploaded', icon_url = 'https://cdn.discordapp.com/icons/336592624624336896/31615259cca237257e3204767959a967.png')
            em.set_footer(text = 'Filesize: ' + str(round(int(filesize) / 1000, 2)) + 'KB')
            await client.send_message(message.channel, embed = em)
        else:
            await client.send_message(message.channel, 'No nbt file detected')


    #!!tps
    elif message.content.startswith('!!tps'):
        level_file = nbt.NBTFile(os.path.join(SURVIVAL_FOLDER, 'level.dat'), 'rb')
        time_start = int(level_file['Data']['LastPlayed'].value)
        level_file = nbt.NBTFile(os.path.join(SURVIVAL_FOLDER, 'level.dat'), 'rb')
        time_current = int(level_file['Data']['LastPlayed'].value)
        level_file = nbt.NBTFile(os.path.join(SURVIVAL_FOLDER, 'level.dat_old'), 'rb')
        time_old = int(level_file['Data']['LastPlayed'].value)
        tps = time_current - time_old
        tps = 45 / (tps / 1000) * 20
        if tps > 20: tps = float(20)
        if tps < 0: tps = float(0)
        await client.send_message(message.channel, 'The Current TPS is: **' + str(round(tps, 2)) + '** | TPS only updates roughly every 45 seconds')


    #!!benchmark start STAT
    elif message.content.startswith('!!benchmark'):
        args = message.content.split(" ")
        global benchmark_started, benchmark_results, benchmark_start_time, benchmark_stat
        if len(args) == 3 and args[1] == 'start' and benchmark_stat == '':
            benchmark_results = []
            benchmark_stat = ''.join(get_close_matches('stat.' + args[2], stat_list, 1))
            for item in uuids:
                with open(os.path.join(STAT_FOLDER, convert_uuid(item) + '.json')) as json_data:
                    stats = json.load(json_data)
                    try:
                        benchmark_results.append(stats[benchmark_stat])
                    except:
                        benchmark_results.append(str(0))
            benchmark_start_time = time.time()
            await client.send_message(message.channel, 'Benchmark started for: ' + benchmark_stat)
            await client.send_message(message.channel, '**Warning:** Benchmarks need to run atleast 1 minute to detect any changes')


        #!!benchmark stop
        elif len(args) == 2 and args[1] == 'stop' and benchmark_stat != '':
            benchmark_results_final = []
            for item in uuids:
                with open(os.path.join(STAT_FOLDER, convert_uuid(item) + '.json')) as json_data:
                    stats = json.load(json_data)
                    try:
                        benchmark_results_final.append(stats[benchmark_stat])
                    except:
                        benchmark_results_final.append(str(0))
            benchmark_time = int(time.time() - benchmark_start_time)
            benchmark_stat = ''
            text1 = []
            text2 = []
            for i in range(0, len(uuids)):
                benchmark_result = int(benchmark_results_final[i]) - int(benchmark_results[i])
                if benchmark_result > 0:
                    text1.append(names[i] + ': ' + str(benchmark_result))
                    text2.append(str(int(benchmark_result / (benchmark_time / 3600))) + ' per hour')
            if not text1 == []:
                em = discord.Embed(
                    description = '',
                    colour = 0x003763)
                em.add_field(
                    name = 'Players',
                    inline = True,
                    value = '\n'.join(text1))
                em.add_field(
                    name = 'Per Hour',
                    inline = True,
                    value = '\n'.join(text2))
                em.set_author(name = 'Benchmark', icon_url = 'https://cdn.discordapp.com/icons/336592624624336896/31615259cca237257e3204767959a967.png')
                em.set_footer(text = 'Total Time: ' + str(datetime.timedelta(seconds = benchmark_time)))
                await client.send_message(message.channel, embed = em)
            else:
                await client.send_message(message.channel, 'No changes detected')
        else:
            await client.send_message(message.channel, 'Invalid syntax or benchmark currently running')


    #!!list
    elif message.content.startswith('!!list'):
        try:
            server = MinecraftServer(ip, 25565)
            query = server.query()
            online_list = query.players.names
            if online_list != []:
                text1 = []
                for item in online_list:
                    nbtfile = nbt.NBTFile(os.path.join(PLAYERDATA_FOLDER, convert_uuid(uuids[names.index(item)]) + '.dat'), 'rb')
                    if int(nbtfile['Dimension'].value) == -1: text1.append('**' + item + '**(N)')
                    elif int(nbtfile['Dimension'].value) == 0: text1.append('**' + item + '**(O)')
                    elif int(nbtfile['Dimension'].value) == 1: text1.append('**' + item + '**(E)')
                await client.send_message(message.channel, 'Players: ' + ", ".join(text1))
            else:
                await client.send_message(message.channel, 'No Player is currently online')
        except:
            await client.send_message(message.channel, 'An error occurred while loading playerlist')


    #!!worldsize
    elif message.content.startswith('!!worldsize'):
        try:
            total_size = get_size(SURVIVAL_FOLDER)
            ow_size = get_size(OVERWORLD_FOLDER)
            nether_size = get_size(NETHER_FOLDER)
            end_size = get_size(END_FOLDER)
            em = discord.Embed(
                description = '',
                colour = 0x003763)
            em.add_field(
                name = 'Dimension',
                inline = True,
                value = 'Overworld\nNether\nEnd')
            em.add_field(
                name = 'Size',
                inline = True,
                value = '**' + str(round(ow_size / 1000000000, 2)) +  ' **GB**\n' + str(round(nether_size / 1000000000, 2)) +  ' **GB**\n' + str(round(end_size / 1000000000, 2)) + ' **GB')
            em.set_author(name = 'Worldsize:', icon_url = 'https://cdn.discordapp.com/icons/336592624624336896/31615259cca237257e3204767959a967.png')
            em.set_footer(text = 'Total Worldsize: ' + str(round(total_size / 1000000000, 2)) + 'GB')
            await client.send_message(message.channel, embed = em)
        except:
            await client.send_message(message.channel, 'An error occurred while calculating worldsize')


    #!!synchronize
    elif message.content.startswith('!!synchronize'):
            #removes entries that store namehistory usernames
            nbtfile = nbt.NBTFile(os.path.join(DATA_FOLDER, 'scoreboard.dat'), 'rb')
            for uuid in uuids:
                history = get_name_history(uuid)
                for i, tag in zip(range(len(nbtfile['data']['PlayerScores'])-1, -1, -1), reversed(nbtfile['data']['PlayerScores'])):
                    if any(d['name'] == str(tag['Name']) for d in history):
                        del nbtfile['data']['PlayerScores'][i]
            nbtfile.write_file(os.path.join(DATA_FOLDER, 'scoreboard.dat'))

            #updates all playerscores to stat value if objective does not contain a number
            nbtfile = nbt.NBTFile(os.path.join(DATA_FOLDER, 'scoreboard.dat'), 'rb')
            for i, tag in zip(range(len(nbtfile['data']['PlayerScores'])-1, -1, -1), reversed(nbtfile['data']['PlayerScores'])):
                for objective in nbtfile['data']['Objectives']:
                    if tag['Objective'].value == objective['DisplayName'].value and not any(char.isdigit() for char in objective['DisplayName'].value):
                        try:
                            uuid = uuids[names.index(tag['Name'].value)]
                            with open(os.path.join(STAT_FOLDER, convert_uuid(uuid) + '.json')) as json_data:
                                stats = json.load(json_data)
                            nbtfile['data']['PlayerScores'][i]['Score'].value = stats[objective['CriteriaName'].value]
                            print(str(stats[objective['CriteriaName'].value]) + "        " + str(tag) + "       " + str(objective))
                        except:
                            pass
            nbtfile.write_file(os.path.join(DATA_FOLDER, 'scoreboard.dat'))
            await client.send_message(message.channel, 'Scoreboard and Statistics are now synchronized')

client.run(token)
