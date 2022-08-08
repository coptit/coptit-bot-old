import json
import os
from datetime import datetime

import discord
import dotenv
import requests
from discord.ext import commands, tasks

dotenv.load_dotenv()

# Enable all Intents
intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix="$", intents=intents)

BOT_TOKEN = os.getenv("BOT_TOKEN")
MESSAGE_CHANNEL_ID = os.getenv("MESSAGE_CHANNEL_ID")
WELCOME_CHANNEL_ID = os.getenv("WELCOME_CHANNEL_ID")
AUDIT_LOG_CHANNEL_ID = os.getenv("AUDIT_LOG_CHANNEL_ID")


@client.event
async def on_ready():
    """Event happens when bot become live."""
    # await client.change_presence(activity=discord.Game(name="with code!"))
    print(f"Logged in as {client.user} (ID: {client.user.id})")


@client.event
async def on_member_join(member):
    """Event happens when a new member join the server."""
    role = discord.utils.get(member.guild.roles, name="Role-Name")
    await member.add_roles(role)
    welcome_msg = ("Hey, <@" + str(member.id) +
                   "> welcome to **Server!**, pick your #roles and do write \
        suggestion in #suggestion-box if you have any!")
    channel = await client.fetch_channel(WELCOME_CHANNEL_ID)
    await channel.send(welcome_msg)


if_auto_message_sended = True
audit_message_to_send = False


# this code is used when send embed message without command
@tasks.loop(seconds=60)
async def message_send():
    """Tasks loop for sending message."""
    global if_auto_message_sended

    if if_auto_message_sended is False:

        channel = await client.fetch_channel(MESSAGE_CHANNEL_ID
                                             )  # find channel to send message

        if os.stat("embed.json").st_size != 0:
            embed = discord.Embed.from_dict(
                json.load(open("./embed.json", "r+")))
            await channel.send(content=open("./content.txt", "r+").read(),
                               embed=embed)

            # clear both message files
            open("./content.txt", "r+").truncate(0)
            open("./embed.json", "r+").truncate(0)

        # if embed.json is not empty then send this message
        elif os.stat("content.txt").st_size != 0:
            await channel.send(content=open("./content.txt", "r+").read())
            open("./content.txt", "r+").truncate(0)

        if_auto_message_sended = True


message_send.start()


@client.command(name="send")
@commands.has_role("Coordinator")
async def send(ctx):
    """$send command for predefined messages."""
    # if embed.json is not empty then send this message
    # embed message

    if os.stat("embed.json").st_size != 0:
        embed = discord.Embed.from_dict(json.load(open("./embed.json", "r+")))
        await ctx.channel.send(content=open("./content.txt", "r+").read(),
                               embed=embed)

        # clear both message files
        open("./content.txt", "r+").truncate(0)
        open("./embed.json", "r+").truncate(0)

    elif os.stat("content.txt").st_size != 0:
        await ctx.channel.send(content=open("./content.txt", "r+").read())
        open("./content.txt", "r+").truncate(0)

    if ctx.message.content == "$send":
        await ctx.message.delete()


@client.command(name="clear")
@commands.has_role("Coordinator")
async def clear(ctx, num=1):
    """$clear command for purgeing messages."""
    num += 1
    await ctx.channel.purge(limit=num)


@client.command(name="meme")
async def send_meme(ctx):
    """$meme command for sending memes.api github : https://github.com/D3vd/Meme_Api"""
    response = requests.get(
        "https://meme-api.herokuapp.com/gimme/ProgrammerHumor")
    dict_res = response.json()
    await ctx.channel.send(dict_res["preview"][2])


@client.event
async def on_guild_channel_create(channel):
    """Audit log send to channel when a new channel got created."""
    if audit_message_to_send:
        audit_ch = client.get_channel(int(AUDIT_LOG_CHANNEL_ID))

        if channel.type == discord.ChannelType.text:
            # new text channel created
            title_x = ":ledger: New Text channel created: #" + channel.name

        elif channel.type == discord.ChannelType.voice:
            # new voice channel created
            title_x = ":microphone2: New voice channel created:  :sound:" + channel.name

        elif channel.type == discord.ChannelType.news:
            # new update channel created
            title_x = ":loudspeaker: New News channel created: " + channel.name

        elif channel.type == discord.ChannelType.forum:
            # new forum channel created
            title_x = ":flags: New Forum created: " + channel.name

        elif channel.type == discord.ChannelType.stage_voice:
            # new stage channel created
            title_x = ":flags: New Stage created: " + channel.name

        elif channel.type == discord.ChannelType.category:
            # new category created
            title_x = ":card_index_dividers: New category created: " + channel.name

        embed_x = discord.Embed(title=title_x,
                                timestamp=datetime.now(),
                                color=0x95F985)
        embed_x.set_footer(text=f"Channel ID: {channel.id}")
        await audit_ch.send(embed=embed_x)


@client.event
async def on_guild_channel_delete(channel):
    """Audit log send to channel when a channel got deleted"""
    if audit_message_to_send:
        audit_ch = client.get_channel(int(AUDIT_LOG_CHANNEL_ID))

        title_x = f":wastebasket: {str(channel.type).capitalize()} channel deleted"

        embed_x = discord.Embed(title=title_x,
                                timestamp=datetime.now(),
                                color=0xFF0000)

        embed_x.set_footer(text=f"Channel ID: {channel.id}")

        embed_x.add_field(name="Name", value=channel.name)
        if channel.type not in (
                discord.ChannelType.voice,
                discord.ChannelType.category,
        ):
            embed_x.add_field(name="Topic", value=channel.topic)

        await audit_ch.send(embed=embed_x)


@client.event
async def on_guild_channel_update(channel_before, channel_after):
    """Audit log send to channel on channnel update."""
    if audit_message_to_send:
        any_update = False
        audit_ch = client.get_channel(int(AUDIT_LOG_CHANNEL_ID))

        title_x = f":tools: {str(channel_after.type).capitalize()} channel updated: {channel_before.name}"

        embed_x = discord.Embed(title=title_x,
                                timestamp=datetime.now(),
                                color=0xFFFF00)

        if channel_before.name != channel_after.name:
            embed_x.add_field(name="Renamed",
                              value=channel_before.name + " -> " +
                              channel_after.name)
            any_update = True

        if channel_before.topic != channel_after.topic:
            if channel_before.topic is None:
                embed_x.add_field(name="Topic",
                                  value="None -> " + channel_after.topic)
            else:
                embed_x.add_field(
                    name="Topic",
                    value=channel_before.topic + " -> " + channel_after.topic,
                )
            any_update = True

        embed_x.set_footer(text=f"Channel ID: {channel_after.id}")

        if any_update:
            await audit_ch.send(embed=embed_x)


@client.event
async def on_guild_role_create(role):
    """Audit log on new role created."""
    if audit_message_to_send:
        audit_ch = client.get_channel(int(AUDIT_LOG_CHANNEL_ID))

        title_x = ":screwdriver: Role created: " + role.name

        embed_x = discord.Embed(title=title_x,
                                timestamp=datetime.now(),
                                color=0x95F985)
        embed_x.set_footer(text=f"Role ID: {role.id}")

        await audit_ch.send(embed=embed_x)


@client.event
async def on_guild_role_delete(role):
    """Audit log on role delete"""
    if audit_message_to_send:
        audit_ch = client.get_channel(int(AUDIT_LOG_CHANNEL_ID))

        title_x = ":wastebasket: Role deleted: " + role.name
        embed_x = discord.Embed(title=title_x,
                                timestamp=datetime.now(),
                                color=0xFF0000)

        embed_x.add_field(name="Color", value=role.color)
        embed_x.add_field(name="Hoisted",
                          value="Yes" if role.hoist is True else "No")
        embed_x.add_field(name="Mentionable",
                          value="Yes" if role.mentionable is True else "No")

        embed_x.set_footer(text=f"Role ID: {role.id}")

        await audit_ch.send(embed=embed_x)


@client.event
async def on_guild_role_update(role_before, role_after):
    """Audit log on role update."""
    if audit_message_to_send:
        audit_ch = client.get_channel(int(AUDIT_LOG_CHANNEL_ID))

        title_x = ":hammer_and_wrench: Role updated: " + role_before.name

        embed_x = discord.Embed(title=title_x,
                                timestamp=datetime.now(),
                                color=0xFFFF00)

        is_updated = False

        if role_before.name != role_after.name:
            is_updated = True
            embed_x.add_field(name="Name",
                              value=str(role_before.name) + " -> " +
                              str(role_after.name))

        if role_before.color != role_after.color:
            is_updated = True
            embed_x.add_field(
                name="Color",
                value=str(role_before.color) + " -> " + str(role_after.color),
            )

        embed_x.set_footer(text=f"Role ID: {role_after.id}")

        if is_updated:
            await audit_ch.send(embed=embed_x)


@client.event
async def on_guild_update(guild_before, guild_after):
    """Audit log on server update."""
    if audit_message_to_send:
        audit_ch = client.get_channel(int(AUDIT_LOG_CHANNEL_ID))

        title_x = ":hammer_and_wrench: Server information updated!"

        embed_x = discord.Embed(title=title_x,
                                timestamp=datetime.now(),
                                color=0xFFFF00)

        embed_x.set_thumbnail(url=guild_after.icon)

        major_upadate = False

        if guild_before.name != guild_after.name:
            embed_x.add_field(
                name="Name",
                value=str(guild_before.name) + " -> " + str(guild_after.name),
            )
            major_upadate = True

        if guild_before.icon != guild_after.icon:
            embed_x.add_field(name="Icon", value="Changed")
            major_upadate = True

        if guild_before.description != guild_after.description:
            embed_x.add_field(
                name="Description",
                value=str(guild_before.description) + " -> " +
                str(guild_after.description),
            )
            major_upadate = True

        if not major_upadate:
            embed_x.add_field(name="Other", value="Yes")

        await audit_ch.send(embed=embed_x)


client.run(BOT_TOKEN)
