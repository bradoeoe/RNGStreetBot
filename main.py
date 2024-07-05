from datetime import datetime, timedelta
import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
import json

# import bingo
import taskgenerator
import gun_game
import bingo
import os
import sqlite3
from flask import Flask, request
import re
import requests

mod_role = "Tileracemod"

# TestToken
# Token = ''
Prefix = "$"

# RNG Token
Token = os.getenv("DISCORD_TOKEN")

# #default is RNGStreet
guild = os.getenv("GUILD_ID", "532377514975428628")

intents = discord.Intents.all()
bot = commands.Bot(intents=intents, command_prefix=Prefix)
cog_files = ["GunGame"]


@bot.event
async def on_ready():
    # await bingo.setup(bot)
    await gun_game.setup(bot)
    for x in cog_files:
        cog = bot.get_cog(x)
        available_commands = cog.get_commands()
        print([c.name + " - " + c.description for c in available_commands])
        # Iterate through the guilds the bot is in
    for guild in bot.guilds:
        print(f"Guild: {guild.name} (ID: {guild.id})")
        # Iterate through the channels in each guild
    # for channel in guild.text_channels:
    #    print(f'Channel: {channel.name} (ID: {channel.id})')
    #   async for message in channel.history(limit=10):
    #      print(f'{message.author}: {message.content}')
    print(f"We have logged in as {bot.user}")
    for guilds in bot.guilds:
        db_file = f"databases/{guilds.id}.db"
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS bingo_players (
                            player_id INTEGER PRIMARY KEY,
                            discord_id INTEGER,
                            rsn TEXT,
                            team TEXT,
                            signup TEXT
                        )"""
        )
        conn.commit()
        conn.close()


async def get_db(ctx):
    return f"databases/{ctx.guild.id}.db"


@bot.hybrid_command(
    name="check_signups", description="List all users who have signed up."
)
# @app_commands.guilds(discord.Object(id=guild))
async def check_signups(ctx):
    db = await get_db(ctx)
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bingo_players")
    players = cursor.fetchall()
    if players:
        response = "Here are the signed up users:\n"
        for player in players:
            response += f"RuneScape Name: {player[2]} \n"
        await ctx.reply(response)
    else:
        await ctx.reply("No users have signed up yet.")
    conn.close()


"""@bot.hybrid_command(name="tilerace_signup", description="Sign up for bingo!")
# @app_commands.guilds(discord.Object(id=guild))
@app_commands.describe(rsn="Your RuneScape name.")
@app_commands.describe(proof="Screenshot of your buy in proof")
async def tilerace_signup(ctx: commands.Context, rsn: str, proof: discord.Attachment):
    # Check if the user already signed up
    db = await get_db(ctx)
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bingo_players WHERE discord_id = ?", (ctx.author.id,))
    existing_player = cursor.fetchone()
    if existing_player:
        await ctx.reply("You have already signed up for bingo.")
        conn.close()
        return

    # Insert the player into the database
    cursor.execute("INSERT INTO bingo_players (discord_id, rsn, team, signup) VALUES (?, ?, '', ?)",
                   (ctx.author.id, rsn, str(proof)))
    conn.commit()

    # Assign the "Tileracer" role to the player
    role = discord.utils.get(ctx.guild.roles, name="Tileracer")
    if role:
        await ctx.author.add_roles(role)

    conn.close()

    await ctx.reply(f"You have successfully signed up for bingo and been assigned the Tileracer role! {proof}")
"""

"""'@bot.hybrid_command(name="tilerace_signup_other", description="Sign up another person for bingo!")
@app_commands.guilds(discord.Object(id=guild))
@app_commands.describe(rsn="Your RuneScape name.")
@app_commands.describe(discord_name="The discord @ of the other person you are signing up.")
@app_commands.describe(proof="Screenshot of your buy in proof")
async def tilerace_signup_other(ctx: commands.Context, discord_name: str, rsn: str, proof: discord.Attachment):
    if mod_role not in [role.name for role in ctx.author.roles]:
        await ctx.reply("You don't have the required role to use this command.")
        return
    try:
        user_id = int(discord_name.replace("<", "").replace(">", "").replace("@", "").replace("!", ""))
    except ValueError:
        await ctx.reply("Error with the username, make sure you have provided the users discord @ name :)")
        return
    print(user_id)
    # Check if the user already signed up
    db = await get_db(ctx)
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bingo_players WHERE discord_id = ?", (user_id,))
    existing_player = cursor.fetchone()
    if existing_player:
        await ctx.reply("You have already signed up for bingo.")
        conn.close()
        return

    # Insert the player into the database
    cursor.execute("INSERT INTO bingo_players (discord_id, rsn, team, signup) VALUES (?, ?, '', ?)",
                   (user_id, rsn, str(proof)))
    conn.commit()

    # Assign the "Tileracer" role to the player
    role = discord.utils.get(ctx.guild.roles, name="Tileracer")
    if role:
        user = ctx.guild.get_member(user_id)
        await user.add_roles(role)
    conn.close()

    await ctx.reply(f"You have successfully signed up {rsn} for tilerace and they have been assigned the Tileracer role! {proof}")
"""


async def fetch_messages(channel, days):
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    messages = []
    async for message in channel.history(limit=None, after=start_date, before=end_date):
        messages.append(message)
    return messages


@bot.command()
async def sync(ctx):
    if ctx.message.author.id == 210193458898403329:
        # await bot.tree.sync(guild=discord.Object(id=guild))
        await bot.tree.sync()
        await ctx.reply("Command sync successful")
        print("yes")
    else:
        await ctx.reply("not allowed to do that ;)")
        print("no")


@bot.command()
async def tree_clear(ctx):
    if ctx.message.author.id == 210193458898403329:
        bot.tree.clear_commands(guild=ctx.guild)
        await bot.tree.sync(guild=ctx.guild)
        await ctx.reply("Command sync successful")
        print("yes")
    else:
        await ctx.reply("not allowed to do that ;)")
        print("no")


@bot.command()
async def syncrng(ctx):
    if ctx.message.author.id == 210193458898403329:
        await bot.tree.sync(guild=discord.Object(id=guild))
        # await bot.tree.sync()
        await ctx.reply("Command sync successful")
        print("yes")
    else:
        await ctx.reply("not allowed to do that ;)")
        print("no")


@bot.command()
async def synctest(ctx):
    if ctx.message.author.id == 210193458898403329:
        await bot.tree.sync()
        # await bot.tree.sync()
        await ctx.reply("Command sync successful")
        print("yes")
    else:
        await ctx.reply("not allowed to do that ;)")
        print("no")


@bot.hybrid_command(name="info", description="Get info on the available commands! :)")
# @app_commands.guilds(discord.Object(id=guild))
async def info(ctx: commands.Context):
    embed = discord.Embed(
        title="Info!", description="List of available commands :).", color=0x3498DB
    )
    embed.timestamp = datetime.now()

    # Available Commands
    """embed.add_field(name="**Task Generator Commands:**",
                    value=f"`/info:` Show this help message.\n"
                          f"`/setup_player:` Setup yourself as a player.\n"
                          f"`/change_rsn:` Change your in-game name.\n"
                          f"`/skip_task:` Skips your current task (Costing 30 points).\n"
                          f"`/block_task:` Blocks your current task (Costing 100 points and max 3).\n"
                          f"`/generate_task:` Gets a new task for you to complete. \n"
                          f"`/task_complete:` Marks your task as complete.\n"
                          f"`/all_tasks:` Shows current available tasks.\n"
                          f"`/profile:` Shows your player profile.\n"
                          f"`/remove_task:` Removes a task from available tasks via ID (mod only).\n"
                          f"`/add_task:` Adds a new task to available tasks (mod only).\n"
                          f"`/upload_task_list:` Accepts a csv file with 3 columns, Task/Difficulty/Points (mod only).\n"
                          f"`/global_leaderboard:` Shows the all time leaderboard.\n"
                          f"`/month_leaderboard:` Shows the current months leaderboard.\n\n",
                    inline=False)"""
    embed.add_field(
        name="**TileRace Commands:**",
        value=f"`/info:` Show this help message.\n"
        f"`/roll:` Rolls your team to a new tile.\n"
        f"`/reroll:` Don't like your roll? Reroll for a new tile! Teams start with 2 of these.\n"
        f"`/complete_tile:` Marks your current tile as completed.\n"
        f"`/complete_chance:` If you have recieved a chance tile, this must be used to mark as complete.\n"
        f"`/tilerace_leaderboard:` Shows the tilerace leaderboard. \n"
        f"`/tilerace_profile:` Shows your teams profile.\n"
        f"`/bonus_tile <Selection>:` Marks a bonus tile as completed.\n"
        f"`/use_golden_ticket:` Knock a team down a tile, cannot be used on the final tile.\n\n",
        inline=False,
    )

    # Send the embedded message
    await ctx.reply(embed=embed)


@bot.hybrid_command(
    name="screenie", description="Which screenshot has the most reacts? :)"
)
# @app_commands.guilds(discord.Object(id=guild))
@app_commands.describe(days="How many days to go back and check?")
async def screenie(ctx: commands.Context, days: int = 0):
    if ctx.message.author.id in [210193458898403329, 641941620627079187]:
        await ctx.defer(ephemeral=False)
        target_channel_ids = [
            532409123367550996,
            1002820962858831922,
            676680654007566356,
            649600054633562112,
        ]
        top_reacted_messages = []

        for channel_id in target_channel_ids:
            channel = bot.get_channel(channel_id)
            messages = await fetch_messages(channel, days)
            for message in messages:
                max_message_reaction_count = 0
                if message.reactions:
                    max_message_reaction_count = max(
                        reaction.count for reaction in message.reactions
                    )
                top_reacted_messages.append((message, max_message_reaction_count))

        # Sort the list of tuples by reaction count in descending order
        top_reacted_messages.sort(key=lambda x: x[1], reverse=True)

        response = "Most reacted messages across all channels:\n"
        for i, (message, reaction_count) in enumerate(top_reacted_messages[:3], 1):
            response += f"{i}. {message.jump_url} - {reaction_count} reactions\n"

        await ctx.reply(response)
    else:
        await ctx.reply("Only for Revs:(")


@bot.hybrid_command()
async def screenie_of_the_week(ctx):
    target_channel_ids = [
        532409123367550996,
        1002820962858831922,
        676680654007566356,
        649600054633562112,
    ]
    top_reacted_messages = []

    for channel_id in target_channel_ids:
        channel = bot.get_channel(channel_id)
        messages = await fetch_messages(channel, 7)
        for message in messages:
            max_message_reaction_count = 0
            if message.reactions:
                max_message_reaction_count = max(
                    reaction.count for reaction in message.reactions
                )
            top_reacted_messages.append((message, max_message_reaction_count))

    # Sort the list of tuples by reaction count in descending order
    top_reacted_messages.sort(key=lambda x: x[1], reverse=True)

    response = "Most reacted messages across all channels:\n"
    for i, (message, reaction_count) in enumerate(top_reacted_messages[:3], 1):
        response += f"{i}. {message.jump_url} - {reaction_count} reactions\n"

    await ctx.send(response)


@bot.hybrid_command()
async def screenie_of_the_month(ctx):
    target_channel_ids = [
        532409123367550996,
        1002820962858831922,
        676680654007566356,
        649600054633562112,
    ]
    top_reacted_messages = []

    for channel_id in target_channel_ids:
        channel = bot.get_channel(channel_id)
        messages = await fetch_messages(channel, 30)
        for message in messages:
            max_message_reaction_count = 0
            if message.reactions:
                max_message_reaction_count = max(
                    reaction.count for reaction in message.reactions
                )
            top_reacted_messages.append((message, max_message_reaction_count))

    # Sort the list of tuples by reaction count in descending order
    top_reacted_messages.sort(key=lambda x: x[1], reverse=True)

    response = "Most reacted messages across all channels:\n"
    for i, (message, reaction_count) in enumerate(top_reacted_messages[:3], 1):
        response += f"{i}. {message.jump_url} - {reaction_count} reactions\n"

    await ctx.send(response)


@bot.hybrid_command()
async def screenie_of_the_year(ctx):
    target_channel_ids = [
        532409123367550996,
        1002820962858831922,
        676680654007566356,
        649600054633562112,
    ]
    top_reacted_messages = []

    for channel_id in target_channel_ids:
        channel = bot.get_channel(channel_id)
        messages = await fetch_messages(channel, 365)
        for message in messages:
            max_message_reaction_count = 0
            if message.reactions:
                max_message_reaction_count = max(
                    reaction.count for reaction in message.reactions
                )
            top_reacted_messages.append((message, max_message_reaction_count))

    # Sort the list of tuples by reaction count in descending order
    top_reacted_messages.sort(key=lambda x: x[1], reverse=True)

    response = "Most reacted messages across all channels:\n"
    for i, (message, reaction_count) in enumerate(top_reacted_messages[:3], 1):
        response += f"{i}. {message.jump_url} - {reaction_count} reactions\n"

    await ctx.send(response)


@bot.event
async def on_member_join(member):
    await asyncio.sleep(5)

    # Ask for the new member's username
    channel = member.guild.system_channel
    if channel is not None:

        await channel.send(
            f"Welcome {member.mention}! Please reply with your rsn to receive your ranked role and gain access to the server!"
        )

        # Wait for the member's response
        def check(message):
            return message.author == member and message.channel == channel

        try:
            message = await bot.wait_for(
                "message", check=check, timeout=120
            )  # Wait for 120 seconds for a response
            new_username = message.content

            # Change the Discord username
            try:
                await member.edit(nick=new_username)
                print(f"Changed username of {member.display_name} to {new_username}")

                # Set their nickname
                await member.edit(nick=new_username)
                print(f"Set nickname of {member.display_name} to {new_username}")

                # Give them a ranked role (you need to replace 'YOUR_ROLE_ID' with the actual role ID)
                role = discord.utils.get(member.guild.roles, id=734013454431813672)
                if role is not None:
                    await member.add_roles(role)
                    print(f"Gave {member.display_name} the role {role.name}")
                else:
                    print("Role not found.")

                await channel.send(
                    f"Wow... Someone who can actually read. You are so good, you managed to type your name.... Want a pat on the back or what? I've changed your username to match your ign ({new_username}). You've been given a role to access some other channels I guess? I dunno I just do what I'm told...!"
                )
            except Exception as e:
                print(f"An error occurred: {e}")
                await channel.send(
                    "Sorry, I couldn't change your username or give you a role. Please contact a moderator for assistance."
                )
        except asyncio.TimeoutError:
            await channel.send(
                "You took too long to get back to me. I literally don't have all day. I gave you two minutes? And what? Nothing??? Fuck me, you need to get a grip and treat me with some respect. I'll be honest you are on thin fucking ice and when Revs hears about this, there is honestly a 50/50 chance you are just straight getting booted. :boot:"
            )
    else:
        print("System channel not found.")


bot.run(Token)
