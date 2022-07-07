import os
import discord
import dotenv
import json

from discord.ext import tasks
from keep_alive import keep_alive

"""
keep_alive() is usefull only when bot is diployed in Replit.com
"""
# from keep_alive import keep_alive
# keep_alive() # make bot alive 24/7

dotenv.load_dotenv()

"""
remember time stamp should be like this.
"timestamp": "2021-12-09T11:36:00.000+00:00",
"""

client = discord.Client()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

print(BOT_TOKEN)

@client.event
async def on_ready():
    # await client.change_presence(activity=discord.Game(name="with code!"))
    print(f"Logged in as {client.user} (ID: {client.user.id})")

# content message(normal message)
content_file = open("../content.txt", "r+")
content_msg = content_file.read()

# embed message
embed_file = open("../embed.json", "r+")

if_message_sended = False

# this code is used when send embed message without command
@tasks.loop(seconds=60)
async def message_send():

    global if_message_sended

    if if_message_sended == False:

        channel = await client.fetch_channel(CHANNEL_ID)  # find channel to send message

        # if embed.json is not empty then send this message
        if os.stat("embed.json").st_size != 0:
            embed = discord.Embed.from_dict(json.load(embed_file))
            await channel.send(content=content_msg, embed=embed)
            print("Message send successfully !")
        elif os.stat("content.txt").st_size != 0:
            await channel.send(content=content_msg)
            print("Message send successfully !")

        # clear both message files
        content_file.truncate(0)
        embed_file.truncate(0)

        if_message_sended = True


# either above will work or bellow both will not work together.

# This code is used when we have to give command and then bot will send embed message
"""
@client.event
async def on_message(message):

    if message.author == client.user:
        return

    if message.content.startswith('^send_msg'):
        embed = discord.Embed.from_dict(json.load(embed_file))
        await message.channel.send(content=content_msg, embed=embed)
"""

message_send.start()

client.run(BOT_TOKEN)
