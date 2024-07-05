import discord
from discord.ext import commands
from discord import app_commands
import random
import sqlite3
import csv
import io
from datetime import datetime

mod_role = "gungamemod"
player_role = "gungamer"


# LOVE YOU BLAKOS <3
# WHAT A POOKIE xxxx
# KISSES TONIGHT? x

async def get_db(ctx):
    return f"databases/{ctx.guild.id}.db"

# Just a lil cheeeky function to check if the game state is 1 or 0 (1 live 0 not live)
async def is_game_live(db):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT is_live FROM game_state WHERE id = 1")
    game_state = cursor.fetchone()
    conn.close()
    return game_state and game_state[0] == 1

async def get_task_name_by_level(db, level):
    # Searches up and pairs the boss name to the users level - tile 0 at the start would be unknown
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM gun_game_bosses WHERE id = ?', (level,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return "Unknown Task"


class GunGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        for guild in self.bot.guilds:
            db_file = f"databases/{guild.id}.db"
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            # Simply makes the tables for the game per guild
            cursor.execute('''CREATE TABLE IF NOT EXISTS gun_game (
                                discord_id INTEGER PRIMARY KEY,
                                rsn TEXT,
                                level INTEGER,
                                bracket TEXT,
                                opponent_id INTEGER                                
                            )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS game_state (
                                id INTEGER PRIMARY KEY,
                                is_live BOOLEAN
                            )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS gun_game_bosses (
                                id INTEGER PRIMARY KEY,
                                name TEXT
                            )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS game_actions (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                discord_id INTEGER,
                                action TEXT,
                                level INTEGER,
                                timestamp DATETIME
                            )''')
            cursor.execute('''INSERT OR IGNORE INTO game_state (id, is_live) VALUES (1, 0)''')
            conn.commit()
            conn.close()

    @commands.hybrid_command(name="start_game", description="Start the game and set it as live.")
    async def start_game(self, ctx: commands.Context, codeword: str):
        # Checks if mod or not
        if mod_role not in [role.name for role in ctx.author.roles]:
            await ctx.reply("You don't have the required role to use this command.")
            return

        db = await get_db(ctx)
        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        # GUNGAME ACTIVE
        cursor.execute("INSERT OR REPLACE INTO game_state (id, is_live) VALUES (1, 1)")

        # Fetch all gunners
        cursor.execute('SELECT discord_id FROM gun_game')
        participants = cursor.fetchall()
        random.shuffle(participants)
        embed = discord.Embed(
            title="Gun Game Match ups",
            description=f"The game is now live! The codeword is **{codeword}**",
            color=discord.Color.green()
        )

        # Pair gunners and update their levels to 1, should've just made this 1 to begin with :) But here we are
        for i in range(0, len(participants), 2):
            if i + 1 < len(participants):
                p1 = participants[i][0]
                p2 = participants[i + 1][0]
                cursor.execute('UPDATE gun_game SET level = 1, opponent_id = ? WHERE discord_id = ?', (p2, p1))
                cursor.execute('UPDATE gun_game SET level = 1, opponent_id = ? WHERE discord_id = ?', (p1, p2))
                embed.add_field(name=f"Match {i // 2 + 1}", value=f"<@{p1}> vs <@{p2}>", inline=False)

        conn.commit()
        conn.close()

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="kill_confirmed", description="Confirm a kill in the gun game.")
    @app_commands.describe(proof="Screenshot of your proof")
    async def kill_confirmed(self, ctx: commands.Context, proof: discord.Attachment):
        db = await get_db(ctx)
        if not await is_game_live(db):
            await ctx.reply("The game is not currently live.")
            return

        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        # Check if the user is playing / signed up
        cursor.execute('SELECT opponent_id, level FROM gun_game WHERE discord_id = ?', (ctx.author.id,))
        result = cursor.fetchone()
        if not result:
            await ctx.reply("You are not a participant in the game.")
            conn.close()
            return

        opponent_id, current_level = result
        # If no opponent, user can't kill_confirm
        if opponent_id is None:
            await ctx.reply("You currently have no opponent.")
            conn.close()
            return

        embed = discord.Embed(
            title="Kill Confirmed",
            description=f"<@{ctx.author.id}> has beaten <@{opponent_id}>.",
            color=discord.Color.red()
        )
        # Mark the user as a winner, their opponent as a LOSER HAHAHA and increase winners level by 1
        cursor.execute(
            'UPDATE gun_game SET bracket = "winner", level = level + 1, opponent_id = NULL WHERE discord_id = ?',
            (ctx.author.id,))
        cursor.execute('UPDATE gun_game SET bracket = "loser", opponent_id = NULL WHERE discord_id = ?', (opponent_id,))
        # Log baby - can't wait for some kewl stats at the end :)
        cursor.execute('INSERT INTO game_actions (discord_id, action, level, timestamp) VALUES (?, ?, ?, ?)',
                       (ctx.author.id, 'win', current_level + 1, datetime.now()))
        cursor.execute('INSERT INTO game_actions (discord_id, action, level, timestamp) VALUES (?, ?, ?, ?)',
                       (opponent_id, 'lose', current_level, datetime.now()))

        new_matchups = []
        # checks if a user is waiting to be paired with a LOSER
        cursor.execute(
            'SELECT discord_id FROM gun_game WHERE bracket = "loser" AND opponent_id IS NULL AND discord_id != ?',
            (opponent_id,))
        waiting_loser = cursor.fetchone()
        if waiting_loser:
            waiting_loser_id = waiting_loser[0]
            cursor.execute('UPDATE gun_game SET opponent_id = ? WHERE discord_id = ?', (waiting_loser_id, opponent_id))
            cursor.execute('UPDATE gun_game SET opponent_id = ? WHERE discord_id = ?', (opponent_id, waiting_loser_id))
            new_matchups.append(f"<@{opponent_id}> vs <@{waiting_loser_id}>")

        # Checks if a user is waiting to be paired with a winnnnna
        cursor.execute(
            'SELECT discord_id FROM gun_game WHERE bracket = "winner" AND opponent_id IS NULL AND discord_id != ?',
            (ctx.author.id,))
        new_opponent = cursor.fetchone()
        if new_opponent:
            new_opponent_id = new_opponent[0]
            cursor.execute('UPDATE gun_game SET opponent_id = ? WHERE discord_id = ?', (new_opponent_id, ctx.author.id))
            cursor.execute('UPDATE gun_game SET opponent_id = ? WHERE discord_id = ?', (ctx.author.id, new_opponent_id))
            new_matchups.append(f"<@{ctx.author.id}> vs <@{new_opponent_id}>")

        if new_matchups:
            embed.add_field(name="New Matchups", value="\n".join(new_matchups), inline=False)
        else:
            embed.add_field(name="No New Opponents", value="No new opponents at this time.", inline=False)

        embed.set_image(url=proof.url)

        conn.commit()
        conn.close()

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="gun_game_signup_other", description="Sign up another user for the gun game!")
    @app_commands.describe(user="The user you want to sign up.")
    @app_commands.describe(rsn="Their RuneScape name.")
    @app_commands.describe(proof="Screenshot of their participation proof")
    async def gun_game_signup_other(self, ctx: commands.Context, user: discord.User, rsn: str,
                                    proof: discord.Attachment):
        # Check if the user already signed up and don't let them sign up twice :)
        db = await get_db(ctx)
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM gun_game WHERE discord_id = ?", (user.id,))
        existing_player = cursor.fetchone()
        if existing_player:
            await ctx.reply(f"{user.mention} has already signed up for the gun game.")
            conn.close()
            return

        # Determine the initial level based on whether the game is live or not
        initial_level = 0
        if await is_game_live(db):
            initial_level = 1

        # Insert the player into the players db, new players start as LOSERS
        cursor.execute(
            "INSERT INTO gun_game (discord_id, rsn, level, bracket, opponent_id) VALUES (?, ?, ?, 'loser', NULL)",
            (user.id, rsn, initial_level))

        # Assign the gungamer role to the player
        role = discord.utils.get(ctx.guild.roles, name=player_role)
        if role:
            await user.add_roles(role)

        # Check if game is live and try to pair the new joining player if someone is waiting to pair up
        if await is_game_live(db):
            cursor.execute(
                'SELECT discord_id FROM gun_game WHERE bracket = "loser" AND opponent_id IS NULL AND discord_id != ?',
                (user.id,))
            available_player = cursor.fetchone()
            if available_player:
                available_player_id = available_player[0]
                cursor.execute('UPDATE gun_game SET opponent_id = ? WHERE discord_id = ?',
                               (available_player_id, user.id))
                cursor.execute('UPDATE gun_game SET opponent_id = ? WHERE discord_id = ?',
                               (user.id, available_player_id))
                await ctx.send(f"{user.mention} has been paired with <@{available_player_id}>. Good luck!")
            else:
                await ctx.send(f"{user.mention}, you have no new opponent at this time.")

        conn.commit()
        conn.close()

        await ctx.reply(
            f"{user.mention} has successfully signed up for the gun game and been assigned the {player_role} role! {proof}")


    @commands.hybrid_command(name="gun_game_signup", description="Sign up for the gun game!")
    @app_commands.describe(rsn="Your RuneScape name.")
    @app_commands.describe(proof="Screenshot of your participation proof")
    async def gun_game_signup(self, ctx: commands.Context, rsn: str, proof: discord.Attachment):
        # Check if the user already signed up and don't let them sign up twice :)
        db = await get_db(ctx)
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM gun_game WHERE discord_id = ?", (ctx.author.id,))
        existing_player = cursor.fetchone()
        if existing_player:
            await ctx.reply("You have already signed up for the gun game.")
            conn.close()
            return

        # Determine the initial level based on whether the game is live or not
        initial_level = 0
        if await is_game_live(db):
            initial_level = 1

        # Insert the player into the players db, new players start as LOSERS
        cursor.execute(
            "INSERT INTO gun_game (discord_id, rsn, level, bracket, opponent_id) VALUES (?, ?, ?, 'loser', NULL)",
            (ctx.author.id, rsn, initial_level))

        # Assign the gungamer role to the player
        role = discord.utils.get(ctx.guild.roles, name=player_role)
        if role:
            await ctx.author.add_roles(role)

        # Check if game is live and try to pair the new joining player if someone is waiting to pair up
        if await is_game_live(db):
            cursor.execute(
                'SELECT discord_id FROM gun_game WHERE bracket = "loser" AND opponent_id IS NULL AND discord_id != ?',
                (ctx.author.id,))
            available_player = cursor.fetchone()
            if available_player:
                available_player_id = available_player[0]
                cursor.execute('UPDATE gun_game SET opponent_id = ? WHERE discord_id = ?',
                               (available_player_id, ctx.author.id))
                cursor.execute('UPDATE gun_game SET opponent_id = ? WHERE discord_id = ?',
                               (ctx.author.id, available_player_id))
                await ctx.send(f"<@{ctx.author.id}> has been paired with <@{available_player_id}>. Good luck!")
            else:
                await ctx.send(f"<@{ctx.author.id}>, you have no new opponent at this time.")

        conn.commit()
        conn.close()

        await ctx.reply(
            f"You have successfully signed up for the gun game and been assigned the {player_role} role! {proof}")

    @commands.hybrid_command(name="upload_bosses", description="Upload a CSV file with boss information.")
    async def upload_bosses(self, ctx: commands.Context, csv_file: discord.Attachment):
        db = await get_db(ctx)
        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        # Read the csv boss list
        csv_data = await csv_file.read()
        csv_reader = csv.reader(io.StringIO(csv_data.decode('utf-8')))

        # Store the bosses
        for row in csv_reader:
            name = str(row[0])
            cursor.execute('INSERT OR REPLACE INTO gun_game_bosses (name) VALUES (?)',
                           (name,))

        conn.commit()
        conn.close()

        await ctx.reply("Bosses have been successfully uploaded and stored.")

    @commands.hybrid_command(name="get_current_task", description="Get your current task based on your level.")
    async def get_current_task(self, ctx: commands.Context):
        # See above - oh I moved, way above :) comments are yawn
        db = await get_db(ctx)
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute('SELECT level FROM gun_game WHERE discord_id = ?', (ctx.author.id,))
        result = cursor.fetchone()
        conn.close()
        if not result:
            await ctx.reply("You are not a participant in the game.")
            return

        level = result[0]
        task_name = await get_task_name_by_level(db, level)
        await ctx.reply(f"Your current task is: {task_name}")

    @commands.hybrid_command(name="knife", description="Knife a user, moving them back one level.")
    @app_commands.describe(discord_name="The Discord name of the user you want to knife.")
    @app_commands.describe(proof="Screenshot of your proof")
    async def knife(self, ctx: commands.Context, discord_name: str, proof: discord.Attachment):
        db = await get_db(ctx)
        if not await is_game_live(db):
            await ctx.reply("The game is not currently live.")
            return
        # Gets rid of all the @ < > around the ID that gets sent to the bot - surely there is a better way to do this but nothing ever works :)
        # apparantly can do with discord.util.find but couldn't work it out - this'll work for now xx (It's how I did the other game)
        try:
            user_id = int(discord_name.replace("<", "").replace(">", "").replace("@", "").replace("!", ""))
        except ValueError:
            await ctx.reply("The specified user was not found.")
            return

        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        cursor.execute("SELECT level FROM gun_game WHERE discord_id = ?", (user_id,))
        result = cursor.fetchone()

        if not result:
            # Make sure the user is signed up x
            await ctx.reply("The specified user is not a participant in the game.")
            conn.close()
            return

        target_level = result[0]

        # Check if the user has been knifed from their current level before - ONLY ONCE!
        cursor.execute("SELECT * FROM game_actions WHERE action = 'knife' AND discord_id = ? AND level = ?",
                       (user_id, target_level))
        knifed_before = cursor.fetchone()

        if knifed_before:
            await ctx.reply(
                f"This user has already been knifed from level {target_level} and cannot be knifed again from this level.")
            conn.close()
            return

        # Decrease the users level by 1 (AHAHAHA LOSER)
        if target_level > 0:
            new_level = target_level - 1
            cursor.execute("UPDATE gun_game SET level = ? WHERE discord_id = ?", (new_level, user_id))
            cursor.execute(
                "INSERT INTO game_actions (discord_id, action, level, timestamp) VALUES (?, ?, ?, ?)",
                (user_id, 'knife', new_level, datetime.now().isoformat()))

            conn.commit()
            await ctx.send(f"<@{ctx.author.id}> has knifed <@{user_id}>, moving them back to level {new_level}.")
        else:
            await ctx.reply("The target user is already at the lowest level and cannot be knifed further.")

        conn.close()


async def setup(bot):
    await bot.add_cog(GunGame(bot))
