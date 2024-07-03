import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
import csv
import sqlite3
import os
from datetime import datetime

#guild = 1196425312708345896


# Will add this later, currently every db is defined with each function itself yawn
async def get_db(ctx):
    return f"{ctx.guild.id}.db"


async def player_exists(player_id, db_file):
    # Connect to the database
    conn = sqlite3.connect(f'databases/{db_file}')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS players
                                  (player_id INTEGER, rsn TEXT, points INTEGER, completed BOOLEAN, task_id INTEGER, total_completed INTEGER  )''')
    # Execute a SELECT query to check if the player exists
    cursor.execute("SELECT * FROM players WHERE player_id = ?", (player_id,))
    # Fetch the first row
    row = cursor.fetchone()
    # Close the connection
    conn.close()
    # Check if a row was fetched
    if row is None:
        return False
    else:
        return True


async def check_status(player_id, db_file):
    conn = sqlite3.connect(f'databases/{db_file}')
    cursor = conn.cursor()
    cursor.execute("SELECT completed FROM players WHERE player_id = ?", (player_id,))
    result = cursor.fetchone()
    completed_status = bool(result[0])
    conn.close()
    return completed_status


async def get_task_name(task_id, db_file):
    conn = sqlite3.connect(f'databases/{db_file}')
    cursor = conn.cursor()
    cursor.execute("SELECT task FROM tasks WHERE task_id = ?", (task_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "No Task"


async def refund_points(task, refund, db_file):
    conn = sqlite3.connect(f'databases/{db_file}')
    cursor = conn.cursor()

    # Find players who have the given task in the blocks table
    cursor.execute("SELECT player_id FROM blocks WHERE task_id = ?", (task,))
    players_with_task = cursor.fetchall()

    for player_id in players_with_task:
        player_id = player_id[0]  # Extract player_id from the tuple
        # Check if the player exists in the players table
        cursor.execute("SELECT * FROM players WHERE player_id = ?", (player_id,))
        player_data = cursor.fetchone()
        if player_data:
            # Refund 30 points to the player
            new_points = player_data[2] + int(refund)
            cursor.execute("UPDATE players SET points = ? WHERE player_id = ?", (new_points, player_id))

    conn.commit()
    conn.close()


class TaskGenCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        for guilds in self.bot.guilds:
            db_file = f"{guilds.id}.db"
            conn = sqlite3.connect(f'databases/{db_file}')
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS tasks
                                          (task_id INTEGER PRIMARY KEY, task TEXT, difficulty TEXT, points INTEGER)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS players (
                                player_id INTEGER,
                                rsn TEXT,
                                points INTEGER,
                                completed BOOLEAN,
                                task_id INTEGER,
                                total_completed INTEGER
                            )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS blocks (
                                block_id INTEGER PRIMARY KEY,
                                player_id INTEGER,
                                task_id INTEGER,
                                FOREIGN KEY (player_id) REFERENCES players(player_id),
                                FOREIGN KEY (task_id) REFERENCES tasks(task_id)
                            )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS tasks_complete (
                                complete_id INTEGER PRIMARY KEY,
                                task_id INTEGER,
                                month TEXT,
                                player_id INTEGER,
                                points INTEGER
                            )''')

    @commands.hybrid_command(name="setup_player", description="Setup your profile")
    # @app_commands.guilds(discord.Object(id=guild))
    @app_commands.describe(rsn="Your in game OldSchool Runescape name")
    async def setup_player(self, ctx: commands.Context, rsn: str):
        db_file = f"{ctx.guild.id}.db"
        if await player_exists(ctx.author.id, db_file):
            await ctx.reply(f"{ctx.author.mention}, You already have been setup, you cannot create another profile :)")
            return
        conn = sqlite3.connect(f'databases/{db_file}')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO players (player_id, rsn, points, completed, task_id, total_completed) VALUES (?, ?, 0, 1, 0, 0)",
            (ctx.author.id, rsn))
        conn.commit()
        conn.close()
        await ctx.reply("Profile successfully created.")

    @commands.hybrid_command(name="skip_task", description="Skips your current task.")
    # @app_commands.guilds(discord.Object(id=guild))
    async def skip_task(self, ctx: commands.Context):
        db_file = f"{ctx.guild.id}.db"
        player_id = ctx.author.id
        if not await player_exists(ctx.author.id, db_file):
            await ctx.reply(
                f"{ctx.author.mention}, You must be new here :) Type '/setup_player' to create your profile :)")
            return
        if await check_status(ctx.author.id, db_file):
            await ctx.reply(
                f"You have already marked your task as complete. Please '/generate_task' to get a new task.")
            return
        try:
            conn = sqlite3.connect(f'databases/{db_file}')
            cursor = conn.cursor()
            # Check if the player has enough points to skip the task
            cursor.execute("SELECT points FROM players WHERE player_id = ?", (player_id,))
            player_points = cursor.fetchone()[0]
            if player_points < 30:
                print("Insufficient points to skip the task.")
                await ctx.reply("Insufficient points to skip the task.")
                return False
            cursor.execute("UPDATE players SET points = points - 30 WHERE player_id = ?", (player_id,))
            cursor.execute(
                "UPDATE players SET completed = ?, task_id = 0  WHERE player_id = ?",
                (1, player_id))

            conn.commit()
            await ctx.reply("Task successfully skipped.")
        except sqlite3.Error as e:
            print("Error skiping task:", e)
            await ctx.reply("Error attempting to skip task.")
            conn.rollback()
            return False
        finally:
            conn.close()

    @commands.hybrid_command(name="block_task", description="Blocks your current task.")
    # @app_commands.guilds(discord.Object(id=guild))
    async def block_task(self, ctx: commands.Context):
        # Extract player_id from ctx, I should do this for more functions tbh :) cbf atm :)
        player_id = ctx.author.id
        db_file = f"{ctx.guild.id}.db"
        # Make sure the player exists
        if not await player_exists(ctx.author.id, db_file):
            await ctx.reply(
                f"{ctx.author.mention}, You must be new here :) Type '/setup_player' to create your profile :)")
            return
        # Make sure the player has a task
        if await check_status(ctx.author.id, db_file):
            await ctx.reply("You need a task to block! Use /generate_task to get yourself a new task.")
            return
        try:
            conn = sqlite3.connect(f'databases/{db_file}')
            cursor = conn.cursor()
            cursor.execute("SELECT points FROM players WHERE player_id = ?", (player_id,))
            player_points = cursor.fetchone()[0]
            if player_points < 100:
                print("Insufficient points to block the task.")
                await ctx.reply("Insufficient points to block the task.")
                return False

            # Check if the player has already blocked 3 tasks
            cursor.execute("SELECT COUNT(*) FROM blocks WHERE player_id = ?", (player_id,))
            num_blocks = cursor.fetchone()[0]
            if num_blocks >= 3:
                print("You have already blocked the maximum number of tasks.")
                await ctx.reply("Player has already blocked the maximum number of tasks.")
                return False

            # Retrieve task_id from the players table
            cursor.execute("SELECT task_id FROM players WHERE player_id = ?", (player_id,))
            task_id = cursor.fetchone()[0]

            # Insert into the blocks table
            cursor.execute("INSERT INTO blocks (player_id, task_id) VALUES (?, ?)", (player_id, task_id))

            # Deduct points from the player
            cursor.execute("UPDATE players SET points = points - 100 WHERE player_id = ?", (player_id,))
            # Remove current task and update completed to True
            cursor.execute("UPDATE players SET task_id = 0, completed = 1, task_id = 0  WHERE player_id = ?",
                           (player_id,))
            print("Task successfully blocked.")
            await ctx.reply("Task blocked successfully.")
            conn.commit()
            return True
        except sqlite3.Error as e:
            print("Error blocking task:", e)
            await ctx.reply("Error attempting to block task.")
            conn.rollback()
            return False
        finally:
            # Close the connection
            conn.close()

    @commands.hybrid_command(name="change_rsn", description="Change your saved data for your OldSchool Runescape name")
    # @app_commands.guilds(discord.Object(id=guild))
    @app_commands.describe(rsn="Your new in game OldSchool Runescape Name")
    async def change_rsn(self, ctx: commands.Context, rsn: str):
        db_file = f"{ctx.guild.id}.db"
        if not await player_exists(ctx.author.id, db_file):
            await ctx.reply(
                f"{ctx.author.mention}, You must be new here :) Type '/setup_player' to create your profile :)")
            return
        conn = sqlite3.connect(f'databases/{db_file}')
        cursor = conn.cursor()
        cursor.execute("UPDATE players SET rsn = ? WHERE player_id = ?", (rsn, ctx.author.id))
        conn.commit()
        conn.close()
        await ctx.reply(f"Your RuneScape name has been updated to {rsn}.")

    @commands.hybrid_command(name="generate_task", description="Generate a task for you to complete.")
    # @app_commands.guilds(discord.Object(id=guild))
    @app_commands.describe(difficulty="Select difficulty")
    @app_commands.choices(difficulty=[
        discord.app_commands.Choice(name='All', value='all'),
        discord.app_commands.Choice(name='Easy', value='Easy'),
        discord.app_commands.Choice(name='Medium', value='Medium'),
        discord.app_commands.Choice(name='Hard', value='Hard'),
        discord.app_commands.Choice(name='Elite', value='Elite'),
        discord.app_commands.Choice(name='Master', value='Master'),
        discord.app_commands.Choice(name='Grandmaster', value='Grandmaster'),
        discord.app_commands.Choice(name='Crazy', value='Crazy')

    ])
    async def generate_task(self, ctx: commands.Context, difficulty: str):
        db_file = f"{ctx.guild.id}.db"

        # Check if the player exists in the database
        if not await player_exists(ctx.author.id, db_file):
            await ctx.reply(
                f"{ctx.author.mention}, You must be new here :) Type '/setup_player' to create your profile :)")
            return

        try:
            if await check_status(ctx.author.id, db_file):
                selected_difficulty = random.choice(difficulty.split()).title()

                conn = sqlite3.connect(f'databases/{db_file}')
                cursor = conn.cursor()

                if selected_difficulty == "All":
                    cursor.execute("""
                           SELECT t.task_id, t.task, t.points 
                           FROM tasks t
                           LEFT JOIN blocks b ON t.task_id = b.task_id AND b.player_id = ?
                           WHERE b.block_id IS NULL
                           ORDER BY RANDOM() 
                           LIMIT 1
                       """, (ctx.author.id,))
                else:
                    cursor.execute("""
                           SELECT t.task_id, t.task, t.points 
                           FROM tasks t
                           LEFT JOIN blocks b ON t.task_id = b.task_id AND b.player_id = ?
                           WHERE t.difficulty = ? AND b.block_id IS NULL
                           ORDER BY RANDOM() 
                           LIMIT 1
                       """, (ctx.author.id, selected_difficulty))

                task = cursor.fetchone()
                if task:
                    task_id, name, points = task

                    # Retrieve the task_id for the player from the players table
                    cursor.execute("SELECT task_id FROM players WHERE player_id = ?", (ctx.author.id,))
                    player_task_id = cursor.fetchone()[0]

                    if player_task_id == task_id:
                        await ctx.reply("You already have this task.")
                    else:
                        cursor.execute("UPDATE players SET completed = ?, task_id = ? WHERE player_id = ?",
                                       (0, task_id, ctx.author.id))
                        conn.commit()
                        await ctx.reply(
                            f"Random task selected. Difficulty: **{selected_difficulty}**. Task: **{name}**. Offering **{points}** points.")

                else:
                    await ctx.reply("No available tasks.")
                conn.close()
            else:
                await ctx.reply(
                    f"You still haven't completed your last task, type '/task_complete' (or 'skip/block') along with your image?"
                    f" Is an image going to be required? For now I'll let it just type '/task_complete' to complete your task.")
        except sqlite3.Error as e:
            await ctx.reply(f"An error occurred: {e}")

    @commands.hybrid_command(name="task_complete", description="Mark your current task as completed.")
    # @app_commands.guilds(discord.Object(id=guild))
    async def task_complete(self, ctx: commands.Context, completed_image: discord.Attachment):
        db_file = f"{ctx.guild.id}.db"
        print(completed_image)
        current_month = datetime.now().strftime("%Y-%m")
        if not await player_exists(ctx.author.id, db_file):
            await ctx.reply(
                f"{ctx.author.mention}, You must be new here :) Type '/setup_player' to create your profile :)")
            return
        if await check_status(ctx.author.id, db_file):
            await ctx.reply(
                f"You have already marked your task as complete. Please '/generate_task' to get a new task.")
            return
        conn = sqlite3.connect(f'databases/{db_file}')
        cursor = conn.cursor()
        cursor.execute("SELECT task_id, points, total_completed FROM players WHERE player_id = ?", (ctx.author.id,))
        task_id, current_points, total_completed = cursor.fetchone()
        cursor.execute("SELECT points FROM tasks where task_id = ?", (task_id,))
        task_points = cursor.fetchone()[0]
        new_points = task_points + current_points
        total_completed += 1
        cursor.execute(
            "UPDATE players SET completed = ?, points = ?, total_completed = ?, task_id = 0  WHERE player_id = ?",
            (1, new_points, total_completed, ctx.author.id))
        cursor.execute(
            "INSERT INTO tasks_complete (task_id, month, player_id, points) VALUES (?, ?, ?, ?)",
            (task_id, current_month, ctx.author.id, task_points))

        conn.commit()
        # Close the database connection
        conn.close()
        await ctx.reply(
            f"Task complete! You have earned {task_points} points and now have {new_points}.\n{completed_image}")

    @commands.hybrid_command(name="global_leaderboard", description="View the all time leaderboard.")
    # @app_commands.guilds(discord.Object(id=guild))
    async def global_leaderboard(self, ctx: commands.Context):
        db_file = await get_db(ctx)
        conn = sqlite3.connect(f'databases/{db_file}')
        cursor = conn.cursor()
        cursor.execute("SELECT rsn, points FROM players ORDER BY points DESC LIMIT 5")
        results = cursor.fetchall()
        conn.close()
        if results:
            embed = discord.Embed(title="Global Leaderboard", color=0x00ff00)
            for index, (rsn, points) in enumerate(results, start=1):
                embed.add_field(name=f"#{index}: {rsn}", value=f"Points: {points}", inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("No players found.")

    @commands.hybrid_command(name="all_tasks", description="View all available tasks.")
    # @app_commands.guilds(discord.Object(id=guild))
    async def all_tasks(self, ctx: commands.Context):
        db_file = await get_db(ctx)
        conn = sqlite3.connect(f'databases/{db_file}')
        cursor = conn.cursor()
        # Execute a SELECT query to fetch all tasks
        cursor.execute("SELECT task_id, task, difficulty, points FROM tasks")
        tasks = cursor.fetchall()

        # Close the database connection
        conn.close()
        file_name = f"{ctx.guild.id}_task_list.txt"
        with open(file_name, "w") as file:
            # Iterate over tasks and write them to the text file
            for task in tasks:
                task_id, task_name, difficulty, points = task
                file.write(f"Task ID: {task_id} Task: {task_name} Difficulty: {difficulty} Points: {points}\n")

        # Send the text file
        with open(file_name, "rb") as file:
            await ctx.send(file=discord.File(file, filename=file_name))

    @commands.hybrid_command(name="month_leaderboard", description="View the monthly leaderboard.")
    # @app_commands.guilds(discord.Object(id=guild))
    @app_commands.describe(month="Add a month to see the leaderboard for that month, in the format 'YYYY-MM'")
    async def monthly_leaderboard(self, ctx: commands.Context, month: str = None):
        db_file = await get_db(ctx)
        conn = sqlite3.connect(f'databases/{db_file}')
        cursor = conn.cursor()

        # If no month provided, then just save the current month I guess?
        if month:
            current_month = month
        else:
            current_month = datetime.now().strftime("%Y-%m")
        try:
            cursor.execute(
                "SELECT player_id, SUM(points) as total_points FROM tasks_complete WHERE month = ? GROUP BY player_id ORDER BY total_points DESC LIMIT 5",
                (current_month,))
            results = cursor.fetchall()

            if results:
                embed = discord.Embed(title="Monthly Leaderboard", description=f"For {current_month}", color=0x00ff00)
                for index, (player_id, total_points) in enumerate(results, start=1):
                    # Assuming you have a way to get the player's display name based on their ID
                    cursor.execute("SELECT rsn FROM players WHERE player_id = ?", (player_id,))
                    display_name = cursor.fetchone()[0]  # Implement this function
                    embed.add_field(name=f"#{index}: {display_name}", value=f"Points: {total_points}", inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"No players found for the month: {month}.")
            conn.close()
        except:
            await ctx.reply("Error, Month should be in format YYYY-MM")
            conn.close()

    @commands.hybrid_command(name="profile", description="View your Task profile")
    # @app_commands.guilds(discord.Object(id=guild))
    @app_commands.describe(rsn="Username of the user you would like to view the profile of.")
    async def profile(self, ctx: commands.Context, rsn: str = None):
        db_file = await get_db(ctx)
        if rsn:
            print("player lookup :)")
            print(rsn)
        elif not await player_exists(ctx.author.id, db_file):
            await ctx.reply(
                f"{ctx.author.mention}, You must be new here :) Type '/setup_player' to create your profile :)")
            return
        conn = sqlite3.connect(f'databases/{db_file}')
        cursor = conn.cursor()
        if rsn:
            cursor.execute(
                "SELECT player_id, points, completed, task_id, total_completed FROM players WHERE rsn = ? COLLATE NOCASE",
                (rsn,))
            result = cursor.fetchone()
            if result is None:
                # Player doesn't exist, handle it here (e.g., return an error, raise an exception, etc.)
                await ctx.reply("Player not found.")
                conn.close()
                return
            player_id, points, completed, task_id, total_completed = result
            print(task_id)

            # Get the task name for the current task
            current_task_name = await get_task_name(task_id, db_file)
            # Get the blocked tasks for the player
            cursor.execute("SELECT task_id FROM blocks WHERE player_id = ?", (player_id,))
            blocked_tasks = cursor.fetchall()
            blocked_task_names = []
            for blocked_task_id in blocked_tasks:
                task_name = await get_task_name(blocked_task_id[0], db_file)
                blocked_task_names.append(task_name)

            conn.close()
        else:
            cursor.execute("SELECT rsn, points, completed, task_id, total_completed FROM players WHERE player_id = ?",
                           (ctx.author.id,))
            result = cursor.fetchone()
            rsn, points, completed, task_id, total_completed = result
            print(task_id)

            # Get the task name for the current task
            current_task_name = await get_task_name(task_id, db_file)
            # Get the blocked tasks for the player
            cursor.execute("SELECT task_id FROM blocks WHERE player_id = ?", (ctx.author.id,))
            blocked_tasks = cursor.fetchall()
            blocked_task_names = []
            for blocked_task_id in blocked_tasks:
                task_name = await get_task_name(blocked_task_id[0], db_file)
                blocked_task_names.append(task_name)

            conn.close()

        embed = discord.Embed(title="Player Profile", color=0x00ff00)
        embed.add_field(name="RSN", value=rsn, inline=True)
        embed.add_field(name="Points", value=points, inline=True)
        embed.add_field(name="Current task", value=current_task_name, inline=True)
        embed.add_field(name="Total Completed", value=total_completed, inline=False)

        if blocked_task_names:
            embed.add_field(name="Blocked Tasks", value="\n".join(blocked_task_names), inline=False)
        else:
            embed.add_field(name="Blocked Tasks", value="No tasks blocked", inline=False)

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="remove_task",
                             description="Removes a task from the task list.")
    async def remove_task(self, ctx: commands.Context, task_id: int):
        db_file = f"{ctx.guild.id}.db"
        if ctx.message.author.id == 210193458898403329:
            # Connect to the database
            conn = sqlite3.connect(f'databases/{db_file}')
            cursor = conn.cursor()
            await refund_points(task_id, 100, db_file)
            # Check if the task exists
            cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
            result = cursor.fetchone()
            if not result:
                await ctx.send("Task not found.")
                conn.close()
                return

            # Remove the task from the database
            cursor.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))

            # Commit changes and close connection
            conn.commit()
            conn.close()

            await ctx.send("Task removed successfully.")
        else:
            await ctx.reply("You can't do that :(")

    @commands.hybrid_command(name="add_task",
                             description="Add's a new task to the tast list.")
    async def add_task(self, ctx: commands.Context, task_name: str, points: int, difficulty: str):
        db_file = f"{ctx.guild.id}.db"
        if ctx.message.author.id == 210193458898403329:

            # Connect to the database
            conn = sqlite3.connect(f'databases/{db_file}')
            cursor = conn.cursor()

            # Check if the task already exists
            cursor.execute("SELECT * FROM tasks WHERE task = ?", (task_name.title(),))
            result = cursor.fetchone()
            if result:
                await ctx.send("Task already exists.")
                conn.close()
                return

            # Find an available task_id or reuse an empty one
            cursor.execute("SELECT task_id FROM tasks")
            existing_task_ids = {row[0] for row in cursor.fetchall()}
            task_id = 1
            while task_id in existing_task_ids:
                task_id += 1

            # Insert the new task into the database
            cursor.execute("INSERT INTO tasks (task_id, task, difficulty, points) VALUES (?, ?, ?, ?)",
                           (task_id, task_name, difficulty, points))

            # Commit changes and close connection
            conn.commit()
            conn.close()

            await ctx.send("Task added successfully.")
        else:
            ctx.reply("You can't do that :(")

    @commands.hybrid_command(name="upload_task_list",
                             description="Upload a task list in csv format please with rows Name/points/difficulty")
    async def upload_task_list(self, ctx: commands.Context, uploaded_tasks: discord.Attachment):
        if ctx.message.author.id == 210193458898403329:
            db_file = f"{ctx.guild.id}.db"
            print("File received")
            await ctx.defer(ephemeral=False)
            if os.path.exists(f'databases/{db_file}'):
                # If it exists, connect to the database
                conn = sqlite3.connect(f'databases/{db_file}')
                cursor = conn.cursor()
            else:
                # If it doesn't exist, create a new database
                conn = sqlite3.connect(f'databases/{db_file}')
                cursor = conn.cursor()
                cursor.execute('''CREATE TABLE tasks
                                  (task_id INTEGER PRIMARY KEY, task TEXT, difficulty TEXT, points INTEGER)''')

            await uploaded_tasks.save("task_list.csv")
            with open('task_list.csv', 'r') as file:
                csv_reader = csv.reader(file)
                existing_tasks = set()  # To keep track of tasks in the new CSV
                updated_tasks_info = []  # To store changed points/difficulty info
                for row in csv_reader:
                    task, difficulty, points = row
                    existing_tasks.add(task)
                    # Check if the task already exists in the database
                    cursor.execute("SELECT * FROM tasks WHERE task = ?", (task,))
                    result = cursor.fetchone()
                    if result:
                        # If the task exists, update difficulty and points if necessary
                        if result[2] != difficulty or result[3] != int(points):
                            cursor.execute("UPDATE tasks SET difficulty = ?, points = ? WHERE task = ?",
                                           (difficulty, int(points), task))
                            updated_tasks_info.append((task, difficulty, int(points)))  # Track changes
                    else:
                        # If the task doesn't exist, insert it into the database
                        # Find an available task_id or reuse an empty one
                        cursor.execute("SELECT task_id FROM tasks")
                        existing_task_ids = {row[0] for row in cursor.fetchall()}  # Collect all existing task IDs

                        # Find the lowest unused task ID
                        task_id = 1
                        while task_id in existing_task_ids:
                            task_id += 1

                        cursor.execute("INSERT INTO tasks (task_id, task, difficulty, points) VALUES (?, ?, ?, ?)",
                                       (task_id, task, difficulty, int(points)))

            # Remove tasks not present in the new CSV
            cursor.execute("SELECT task_id, task FROM tasks")
            tasks_in_db = {row[1]: row[0] for row in cursor.fetchall()}  # Dictionary of task: task_id
            tasks_to_remove = [task for task in tasks_in_db.keys() if task not in existing_tasks]
            for task in tasks_to_remove:
                task_id = tasks_in_db[task]
                # Call refund_points function for tasks to be removed
                await refund_points(task_id, 100, db_file)
                # Remove task from database
                cursor.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
            conn.commit()
            conn.close()
            # Construct reply message
            reply_msg = "File processed successfully."
            if tasks_to_remove:
                removed_tasks_info = "\n".join([f"Task: {task}, ID: {tasks_in_db[task]}" for task in tasks_to_remove])
                reply_msg += f"\nRemoved tasks:\n{removed_tasks_info}"
            if updated_tasks_info:
                updated_tasks_info_str = "\n".join(
                    [f"Task: {task}, Difficulty: {difficulty}, Points: {points}" for task, difficulty, points in
                     updated_tasks_info])
                reply_msg += f"\nUpdated tasks:\n{updated_tasks_info_str}"
            await ctx.reply(reply_msg)
        else:
            await ctx.reply("You can't do that :(")

async def setup(bot):
    await bot.add_cog(TaskGenCommands(bot))
