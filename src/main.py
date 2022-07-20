import os
import discord
import dotenv
import json

from discord.ext import tasks
from discord.ext import commands

dotenv.load_dotenv()

"""
remember time stamp should be like this.
"timestamp": "2021-12-09T11:36:00.000+00:00",
"""

# Enable all Intents
intents = discord.Intents.all()
intents.members = True
client = discord.Client(intents=intents)

BOT_TOKEN = os.getenv("BOT_TOKEN")
MESSAGE_CHANNEL_ID = os.getenv("MESSAGE_CHANNEL_ID")
WELCOME_CHANNEL_ID = os.getenv("WELCOME_CHANNEL_ID")

@client.event
async def on_ready():
    #await client.change_presence(activity=discord.Game(name="with code!"))
    print(f"Logged in as {client.user} (ID: {client.user.id})")

@client.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name="Role-Name")
    await member.add_roles(role)
    welcome_msg = "Hey, <@" + str(member.id) + "> welcome to **Server!**, pick your #roles and do write suggestion in #suggestion-box if you have any!"
    channel = await client.fetch_channel(WELCOME_CHANNEL_ID)
    await channel.send(welcome_msg)

# content message(normal message)
content_file = open("./content.txt", "r+")
content_msg = content_file.read()

# embed message
embed_file = open("./embed.json", "r+")

if_auto_message_sended = True

# this code is used when send embed message without command
@tasks.loop(seconds=60)
async def message_send():

    global if_auto_message_sended

    if if_auto_message_sended == False:

        channel = await client.fetch_channel(MESSAGE_CHANNEL_ID)  # find channel to send message

        # if embed.json is not empty then send this message
        if os.stat("embed.json").st_size != 0:
            embed = discord.Embed.from_dict(json.load(embed_file))
            await channel.send(content=content_msg, embed=embed)

            # clear both message files
            content_file.truncate(0)
            embed_file.truncate(0)

        elif os.stat("content.txt").st_size != 0:
            await channel.send(content=content_msg)

            content_file.truncate(0)


        if_auto_message_sended = True

# This code is used when we have to give command and then bot will send embed message
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith("^send"):

        # if embed.json is not empty then send this message
        if os.stat("embed.json").st_size != 0:
            embed = discord.Embed.from_dict(json.load(embed_file))
            await message.channel.send(content=content_msg, embed=embed)

            # clear both message files
            content_file.truncate(0)
            embed_file.truncate(0)

        elif os.stat("content.txt").st_size != 0:
            await message.channel.send(content=content_msg)

            content_file.truncate(0)


message_send.start()

client.run(BOT_TOKEN)