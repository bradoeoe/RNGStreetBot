import discord
from discord.ext import commands
from discord import app_commands
import random
import sqlite3

mod_role = "Tileracemod"
player_role = "Tileracer"

async def get_db(ctx):
    return f"databases/{ctx.guild.id}.db"

async def is_game_live(db):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT is_live FROM game_state WHERE id = 1")
    game_state = cursor.fetchone()
    conn.close()
    return game_state and game_state[0] == 1

class GunGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        for guild in self.bot.guilds:
            db_file = f"databases/{guild.id}.db"
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
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
            cursor.execute('''INSERT OR IGNORE INTO game_state (id, is_live) VALUES (1, 0)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS waiting_list (
                                discord_id INTEGER PRIMARY KEY,
                                rsn TEXT
                            )''')
            conn.commit()
            conn.close()

    @commands.hybrid_command(name="start_game", description="Start the game and set it as live.")
    async def start_game(self, ctx: commands.Context, codeword: str):
        if mod_role not in [role.name for role in ctx.author.roles]:
            await ctx.reply("You don't have the required role to use this command.")
            return

        db = await get_db(ctx)
        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        # Set game state to live
        cursor.execute("INSERT OR REPLACE INTO game_state (id, is_live) VALUES (1, 1)")

        # Fetch all participants
        cursor.execute('SELECT discord_id FROM gun_game')
        participants = cursor.fetchall()
        random.shuffle(participants)

        # Pair participants and update their levels and the database
        for i in range(0, len(participants), 2):
            if i + 1 < len(participants):
                p1 = participants[i][0]
                p2 = participants[i + 1][0]
                cursor.execute('UPDATE gun_game SET level = 1, opponent_id = ? WHERE discord_id = ?', (p2, p1))
                cursor.execute('UPDATE gun_game SET level = 1, opponent_id = ? WHERE discord_id = ?', (p1, p2))
                user1 = await self.bot.fetch_user(p1)
                user2 = await self.bot.fetch_user(p2)
                await ctx.send(f"{user1.display_name} has been paired with {user2.display_name}. Good luck!")

        conn.commit()
        conn.close()

        await ctx.send(f"The game is live! The codeword is {codeword}")

    @commands.hybrid_command(name="kill_confirmed", description="Confirm a kill in the gun game.")
    async def kill_confirmed(self, ctx: commands.Context):
        db = await get_db(ctx)
        if not await is_game_live(db):
            await ctx.reply("The game is not currently live.")
            return

        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        # Check if the user is in the game
        cursor.execute('SELECT opponent_id, level FROM gun_game WHERE discord_id = ?', (ctx.author.id,))
        result = cursor.fetchone()
        if not result:
            await ctx.reply("You are not a participant in the game.")
            conn.close()
            return

        opponent_id, current_level = result
        if opponent_id is None:
            await ctx.reply("You currently have no opponent.")
            conn.close()
            return

        # Mark the user as a winner, increment their level, and mark their opponent as a loser
        cursor.execute('UPDATE gun_game SET bracket = "winner", level = level + 1, opponent_id = NULL WHERE discord_id = ?', (ctx.author.id,))
        cursor.execute('UPDATE gun_game SET bracket = "loser", opponent_id = NULL WHERE discord_id = ?', (opponent_id,))

        # Check if there's a waiting player to pair with the opponent (loser)
        cursor.execute('SELECT discord_id FROM waiting_list LIMIT 1')
        waiting_player = cursor.fetchone()
        if waiting_player:
            waiting_player_id = waiting_player[0]
            cursor.execute('UPDATE gun_game SET opponent_id = ? WHERE discord_id = ?', (waiting_player_id, opponent_id))
            cursor.execute('UPDATE gun_game SET opponent_id = ? WHERE discord_id = ?', (opponent_id, waiting_player_id))
            cursor.execute('DELETE FROM waiting_list WHERE discord_id = ?', (waiting_player_id,))
            user1 = await self.bot.fetch_user(waiting_player_id)
            await ctx.send(f"{ctx.author.display_name} has been paired with {user1.display_name}. Good luck!")
        else:
            await ctx.send(f"{ctx.author.display_name}, you have no new opponent at this time.")

        # Try to pair the user (winner) with another winner or loser
        cursor.execute('SELECT discord_id FROM gun_game WHERE bracket = "winner" AND opponent_id IS NULL AND discord_id != ?', (ctx.author.id,))
        new_opponent = cursor.fetchone()
        if new_opponent:
            new_opponent_id = new_opponent[0]
            cursor.execute('UPDATE gun_game SET opponent_id = ? WHERE discord_id = ?', (new_opponent_id, ctx.author.id))
            cursor.execute('UPDATE gun_game SET opponent_id = ? WHERE discord_id = ?', (ctx.author.id, new_opponent_id))
            user1 = await self.bot.fetch_user(new_opponent_id)
            await ctx.send(f"{ctx.author.display_name} has been paired with {user1.display_name}. Good luck!")
        else:
            await ctx.send(f"{ctx.author.display_name}, you have no new opponent at this time.")

        conn.commit()
        conn.close()

    @commands.hybrid_command(name="gun_game_signup", description="Sign up for the gun game!")
    @app_commands.describe(rsn="Your RuneScape name.")
    @app_commands.describe(proof="Screenshot of your participation proof")
    async def gun_game_signup(self, ctx: commands.Context, rsn: str, proof: discord.Attachment):
        # Check if the user already signed up
        db = await get_db(ctx)
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM gun_game WHERE discord_id = ?", (ctx.author.id,))
        existing_player = cursor.fetchone()
        if existing_player:
            await ctx.reply("You have already signed up for the gun game.")
            conn.close()
            return

        # Insert the player into the database
        cursor.execute("INSERT INTO gun_game (discord_id, rsn, level, bracket, opponent_id) VALUES (?, ?, 0, '', NULL)",
                       (ctx.author.id, rsn))
        conn.commit()

        # Assign the "Tileracer" role to the player
        role = discord.utils.get(ctx.guild.roles, name=player_role)
        if role:
            await ctx.author.add_roles(role)

        # Check if game is live and try to pair the new player if possible
        if await is_game_live(db):
            cursor.execute('SELECT discord_id FROM gun_game WHERE opponent_id IS NULL AND discord_id != ?', (ctx.author.id,))
            available_player = cursor.fetchone()
            if available_player:
                available_player_id = available_player[0]
                cursor.execute('UPDATE gun_game SET opponent_id = ? WHERE discord_id = ?', (available_player_id, ctx.author.id))
                cursor.execute('UPDATE gun_game SET opponent_id = ? WHERE discord_id = ?', (ctx.author.id, available_player_id))
                user1 = await self.bot.fetch_user(available_player_id)
                await ctx.send(f"{ctx.author.display_name} has been paired with {user1.display_name}. Good luck!")
            else:
                # Add the new player to the waiting list if no available player
                cursor.execute("INSERT INTO waiting_list (discord_id, rsn) VALUES (?, ?)", (ctx.author.id, rsn))
                await ctx.send(f"{ctx.author.display_name}, you have been added to the waiting list.")

        conn.commit()
        conn.close()

        await ctx.reply(f"You have successfully signed up for the gun game and been assigned the {player_role} role! {proof}")

async def setup(bot):
    await bot.add_cog(GunGame(bot))
