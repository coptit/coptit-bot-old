import os
import discord
import json
from discord.ext import tasks 
from keep_alive import keep_alive

"""
remember time stamp should be like this.
"timestamp": "2021-12-09T11:36:00.000+00:00",
"""

keep_alive() # make bot alive 24/7

response = open('embed.json')

client = discord.Client()

BOT_TOKEN = os.environ['BOT_TOKEN']
CHANNEL_ID = os.environ['CHANNEL_ID']

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')


# this code is used when send embed message without command
one_time_message_send = False
if_message_to_send = False

@tasks.loop(seconds=5)
async def check_for_message_send():
  global one_time_message_send
  global if_message_to_send
  if one_time_message_send == False and if_message_to_send == True:
    embed = discord.Embed.from_dict(json.load(response))
    channel = await client.fetch_channel(CHANNEL_ID)
    await channel.send(embed=embed)
    one_time_message_send = True


# either above witll work or bellow both will not work together.
"""
# This code is used when we have to give command and then bot will send embed message

@client.event
async def on_message(message):
   
    if message.author == client.user:
        return

    if message.content.startswith('$embed'):
        embed = discord.Embed.from_dict(json.load(response))
        await message.channel.send(embed=embed)
"""

check_for_message_send.start()

client.run(BOT_TOKEN)