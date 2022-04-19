import base64
import json
import os

import discord
import requests


# toggles '-' in given uuid
def convert_uuid(uuid):
    if '-' in uuid:
        return uuid.split('.json', 1)[0].translate({ord(i): None for i in '-'})
    else:
        return uuid[:8] + '-' + uuid[8:12] + '-' + uuid[12:16] + '-' + uuid[16:20] + '-' + uuid[20:]


# The only markdown special character allowed in Minecraft username is '_'
# Discord does not allow using a backslash at the beginning to stop markdown if the value has an
#     underscore, so you have to escape the individual underscores.
def format_name_for_embed(name):
    return name.replace('_', '\\_')


# returns the total size of all files in given location
def get_size(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


# returns all names in the namehistory of a uuid without duplicates or the current name
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


# returns the name for a given uuid
def get_name_from_uuid(uuid):
    try:
        url = "https://sessionserver.mojang.com/session/minecraft/profile/" + uuid
        response = requests.get(url)
        response.raise_for_status
        response = json.loads(response.text)
        response = json.loads(base64.b64decode(response['properties'][0]['value']))
        return response['profileName']
    except:
        return None


# generates an embed Table from given columns and the corresponding values
def generate_embed_table(columns, values, line=False):
    em = discord.Embed(
        description='',
        colour=0x003763)
    for column in columns:
        em.add_field(
            name=column,
            inline=line,
            value=values[columns.index(column)])
    return em


def shorten_embed_lists(lists, chars_added=0):
    min_lengths = []
    for l in lists:
        i = 0
        min_length = 0
        for count, value in enumerate(l):
            i += len(value)
            i += chars_added
            if i <= 1005 and count > min_length:
                min_length = count
        min_lengths.append(min_length)
    shortened_lists = []
    for l in lists:
        new_list = list(l[:min(min_lengths)])
        remaining_entries_count = len(lists[0]) - min(min_lengths)
        new_list.append(f'...{remaining_entries_count} {"more entries" if remaining_entries_count != 1 else "more entry"}')
        shortened_lists.append(new_list)
    return shortened_lists
