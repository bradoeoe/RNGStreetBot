import discord
import random
import asyncio
import json
import datetime

# RNGStreetToken
TOKEN = 'TOKEN'

ardy_pigs_roll = 0

# Prefix to use with Discord
PREFIX = '$'

allowed_channels = [1207630751407935509, 1206154823888801792]

game_state = True

# File of Teams Data to be saved to (This must exist because cbf making it if it doesn't) :)
json_file_path = "data.json"
with open(json_file_path, 'r') as json_file:
    teams = json.load(json_file)

intents = discord.Intents.all()
client = discord.Client(intents=intents)

# Set roles in discord for permissions in commands
# team_captain_role = "Bingo Captain"
bingo_mod_role = "Bingo Mod"
bingo_player_role = "Bingo"

tile_messages = {
    1: "(Tile 1) 3 x Ahrim's Pieces",
    2: "(Tile 2) 3 x Guthan's Pieces",
    3: "(Tile 3) 3 x Dharok's Pieces",
    4: "(Tile 4) 3 x Karil's Pieces",
    5: "(Tile 5) 3 x Torag's Pieces",
    6: "(Tile 6) 3 x Verac's Pieces",
    7: "(Tile 7) Warped Sceptre",
    8: "(Tile 8) Dragon Pickaxe",
    9: "(Tile 9) Chompy Chick",
    10: "(Tile 10) Dragon Warnhammer",
    11: "(Tile 11) Dragon Chainbody",
    12: "(Tile 12) Sarachnis Cudgel",
    13: "(Tile 13) Vorkath's Head",
    14: "(Tile 14) Bandos Armour Piece",
    15: "(Tile 15) Elder Chaos Robe Piece",
    16: "(Tile 16) Spirit Shield",
    17: "(Tile 17) Champion Scroll",
    18: "(Tile 18) Venator Shard",
    19: "(Tile 19) COX Purple",
    20: "(Tile 20) TOA Purple",
    21: "(Tile 21) Tanzanite Fang",
    22: "(Tile 22) Abyssal Dye",
    23: "(Tile 23) Corrupted Gauntlet Unique",
    24: "(Tile 24) Blood Shard",
    25: "(Tile 25) 3 Awakened Orbs",
    26: "(Tile 26) 1M+ Revenant Statue",
    27: "(Tile 27) Dragon Pickaxe",
    28: "(Tile 28) 3 Clue Pieces from the same God",
    29: "(Tile 29) Voidwaker Piece",
    30: "(Tile 30) TOA Purple",
    31: "(Tile 31) Any Godsword Shard",
    32: "(Tile 32) Staff of the Dead",
    33: "(Tile 33) Full Pyromancer",
    34: "(Tile 34) Amulet of the Damned",
    35: "(Tile 35) Basilisk Jaw",
    36: "(Tile 36) Lord of the Rings",
    37: "(Tile 37) Full Odium or Malediction Ward",
    38: "(Tile 38) Armadyl Armour Piece",
    39: "(Tile 39) Armadyl Crossbow or Saradomin Hilt",
    40: "(Tile 40) Medium Clue Boots",
    41: "(Tile 41) Chromium Ingot",
    42: "(Tile 42) Serpentine Visage",
    43: "(Tile 43) Pharoah's sceptre",
    44: "(Tile 44) 5 Fire Capes",
    45: "(Tile 45) Nex Unique",
    46: "(Tile 46) Nightmare Unique",
    47: "(Tile 47) COX Purple",
    48: "(Tile 48) TOB Purple",
    49: "(Tile 49) Holy Elixir",
    50: "(Tile 50) TOB Purple",
    51: "(Tile 51) Zenyte Shard and Uncut Onyx",
    52: "(Tile 52) Black Mask",
    53: "(Tile 53) Virtus Piece",
    54: "(Tile 54) Magic Fang",
    55: "(Tile 55) Dex and Arcane Scroll",
    56: "(Tile 56) Justicar Piece",
    57: "(Tile 57) 3 x Fang/Lighbearer",
    58: "(Tile 58) COX Purple",
    59: "(Tile 59) TOB Purple",
    60: "(Tile 60) Masori Piece",
    61: "(THE FINAL TILE) Any Raids Purple",

}
tiles_max = len(tile_messages)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith(PREFIX):
        command, *args = message.content[len(PREFIX):].split(' ')

        if command == 'create_team':
            await handle_create_team_command(message)
        elif command == 'set_tile':
            await handle_set_tile_command(message, args)
        elif command == 'team':
            await handle_team_tile_command(message)
        elif command == 'team_old':
            await handle_team_tile_old_command(message)
        elif command == 'all_tiles':
            await handle_all_tiles_command(message)
        elif command == 'roll':
            await handle_roll_command(message)
        # elif command == 'join':
        #    await handle_join_command(message, args)
        elif command == 'set_team':
            await set_team_command(message, args)
        elif command == 'remove_user':
            await handle_remove_user_command(message, args)
        # elif command == 'team_players':
        #    await handle_team_players_command(message)
        # elif command == 'leave_team':
        #    await handle_leave_team_command(message)
        # elif command == 'current_tile':
        #     await handle_current_tile_command(message)
        # elif command == 'skip_tile':
        # await handle_skip_tile_command(message)
        elif command == 'reroll':
            await handle_reroll_command(message)
        elif command == 'info':
            await handle_info_command(message)
        elif command == 'all_teams':
            await handle_all_teams_command(message)
        elif command == 'leaderboard':
            await handle_leaderboard_command(message)
        elif command == 'give_reroll':
            await handle_give_reroll(message, args)
        elif command == 'tiles_completed':
            await handle_tiles_completed_command(message, args)
        elif command == 'give_skip_tile':
            await handle_give_skip_tile(message, args)
        elif command == 'completed':
            await handle_completed_command(message)
        elif command == 'reset':
            await handle_reset_command(message)
        elif command == 'start_game':
            await handle_start_game_command(message)
        elif command == 'stop_game':
            await handle_stop_game_command(message)
        elif command == 'team_logo':
            await handle_team_logo_command(message, args)
        elif command == 'team_name':
            await handle_team_name_command(message, args)
        else:
            await message.channel.send(f"Unknown command: {command}. Use {PREFIX}info to see available commands.")


async def save_to_json(json_file_path, data):
    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file)

async def handle_tiles_completed_command(message, args):
    if any(role.name == bingo_mod_role for role in message.author.roles):

        try:
            # Extract the team name or user ID and new tile from the arguments
            team_name = ' '.join(args[:-1]).lower()
            print(args)
            tiles_done = int(args[-1])

            # Check if the team exists
            team = get_team_by_name_or_id(team_name)
            if not team:
                await message.channel.send(f"{message.author.mention}, team '{team_name}' not found.")
                return

            # Update the team's tile
            team['tiles_done'] = tiles_done
            await save_to_json(json_file_path, teams)
            # Notify about the tile update
            await message.channel.send(
                f"{message.author.mention}, updated tiles done for: {team_name}.")
        except():
            await message.channel.send(
                f"{message.author.mention}, invalid command format... uh oh")
    else:
        await message.channel.send(f"{message.author.mention}, you don't have the required role to update tiles done.")


async def handle_team_logo_command(message, args):
    if any(role.name == bingo_mod_role for role in message.author.roles):

        try:
            # Extract the team name or user ID and new tile from the arguments
            team_name = ' '.join(args[:-1]).lower()
            print(args)
            logo_link = args[-1]

            # Check if the team exists
            team = get_team_by_name_or_id(team_name)
            if not team:
                await message.channel.send(f"{message.author.mention}, team '{team_name}' not found.")
                return

            # Update the team's tile
            team['team_logo'] = logo_link
            await save_to_json(json_file_path, teams)
            # Notify about the tile update
            await message.channel.send(
                f"{message.author.mention}, updated the logo for team {team_name}.")
        except():
            await message.channel.send(
                f"{message.author.mention}, invalid command format... uh oh")
    else:
        await message.channel.send(f"{message.author.mention}, you don't have the required role to update the logo.")
async def handle_start_game_command(message):
    global game_state
    if any(role.name == bingo_mod_role for role in message.author.roles):
        game_state = True
        await message.channel.send("The bingo game is officially live!!!")


async def handle_team_name_command(message, args):
    if bingo_mod_role not in [role.name for role in message.author.roles]:
        await message.channel.send(
            f"{message.author.mention}, you don't have the required role to create a team.")
        return
    team_name = ' '.join(args).lower()
    team_name_old = get_team_by_name_or_id(team_name)

    if team_name_old:
        await message.channel.send(f"{message.author.mention}, What should the new team name be?")

        def check(msg):
            return msg.author == message.author and msg.channel == msg.channel

        try:
            old_name = team_name_old['name']
            team_name_new = await client.wait_for('message', check=check, timeout=30)
            team_name_new = team_name_new.content.lower()
            team_name_old['name'] = team_name_new
            await save_to_json(json_file_path, teams)
            await message.channel.send(
                f"{message.author.mention}, you have changed the name of '{old_name}' to '{team_name_new}'!")
        except asyncio.TimeoutError:
            await message.channel.send(f"{message.author.mention}, team creation timed out. Try again.")
    else:
        await message.channel.send(f"{message.author.mention}, please provide a valid team to edit.")


async def handle_stop_game_command(message):
    global game_state
    if any(role.name == bingo_mod_role for role in message.author.roles):
        game_state = False
        await message.channel.send("Game paused :)")


async def handle_all_tiles_command(message):
    if any(role.name == bingo_mod_role for role in message.author.roles):
        embed = discord.Embed(title="All Tiles",
                              description="List of all tiles", color=0x3498db)
        embed.timestamp = datetime.datetime.now()
        all_tiles = '\n'.join(map(str, tile_messages.values()))
        tile_len = len(all_tiles) // 2
        first_half = all_tiles[:tile_len]
        second_half = all_tiles[tile_len:]
        embed.add_field(name=f"**First half!**", value=first_half)
        embed.add_field(name=f"**Second half!**", value=second_half)
        print(all_tiles)
        print(len(all_tiles))
        await message.channel.send(embed=embed, allowed_mentions=discord.AllowedMentions(users=False))


# 1-6 give rerolls to barrows up to a max of 2 and then the other tiles give rerolls regardless"
async def check_tile_for_movement(check_tile, team, message):
    if not team['has_completed']:
        if check_tile in [1, 2, 3, 4, 5, 6]:
            if team['rerolls_earned'] < 2:
                team['rerolls'] += 1
                team['rerolls_earned'] += 1
                await message.channel.send(
                    f"You just earned a reroll! Your team now has {team['rerolls']} rerolls remaining!")
            return check_tile
        if check_tile in [10, 22, 33, 40, 46]:
            team['rerolls'] += 1
            team['rerolls_earned'] += 1
            await message.channel.send(
                f"You just earned a reroll! Your team now has {team['rerolls']} rerolls remaining!")
            return check_tile
    else:
        print("yeet")
        return check_tile
    return check_tile
    # no movement required so checking tile when rolling and when completing also.

async def handle_reset_command(message):
    # Check if the user has the required role
    if any(role.name == bingo_mod_role for role in message.author.roles):
        await message.channel.send(f"{message.author.mention}, You sure you wanna do that? (type yes to confirm)")

        def check(msg):
            return msg.author == message.author and msg.channel == msg.channel

        try:
            team_name_message = await client.wait_for('message', check=check, timeout=30)
            answer = team_name_message.content.lower()  # Convert the team name to lowercase

            if answer == "yes":
                # Empty the Teams database
                teams.clear()
                # Save a blank teams file
                with open(json_file_path, 'w') as json_file:
                    json.dump({}, json_file)
                await message.channel.send(f"Successfully reset the game.")
            else:
                await message.channel.send("Reset Cancelled")

            # Create the team and add the user as the creator

            await save_to_json(json_file_path, teams)
        except asyncio.TimeoutError:
            await message.channel.send(f"{message.author.mention}, reset timed out.")

    else:
        await message.channel.send(f"{message.author.mention}, you don't have the required role to reset")


async def handle_give_reroll(message, args):
    # Check if the user has the required role
    if any(role.name == bingo_mod_role for role in message.author.roles):
        # Check if enough arguments are provided
        '''if len(args) == 2:
            target_team_name = args[0].lower()
            amount = int(args[1])'''
        try:
            target_team_name = ' '.join(args[:-1])
            amount = int(args[-1])

            # Check if the target team exists
            target_team = get_team_by_name_or_id(target_team_name)

            if target_team:
                # Give rerolls to the target team
                target_team['rerolls'] += amount
                await save_to_json(json_file_path, teams)

                await message.channel.send(f"Successfully gave {amount} reroll(s) to team '{target_team['name']}'!")

            else:
                await message.channel.send(f"Team '{target_team_name}' not found.")
        except():
            await message.channel.send("Invalid command format. Use $give_reroll <team_name_or_id> <amount>.")
    else:
        await message.channel.send(f"{message.author.mention}, you don't have the required role to give rerolls.")


async def handle_give_skip_tile(message, args):
    # Check if the user has the required role
    if any(role.name == bingo_mod_role for role in message.author.roles):
        # fixed - join the arguments from the discord message.
        try:
            target_team_name = ' '.join(args[:-1])
            amount = int(args[-1])

            # Check if the target team exists
            target_team = get_team_by_name_or_id(target_team_name)

            if target_team:
                # Give skip tiles to the target team
                target_team['skips'] += amount
                await save_to_json(json_file_path, teams)
                await message.channel.send(f"Successfully gave {amount} skip tile(s) to team '{target_team['name']}'!")

            else:
                await message.channel.send(f"Team '{target_team_name}' not found.")
        except():
            await message.channel.send("Invalid command format. Use $give_skip_tile <team_name_or_id> <amount>.")
    else:
        await message.channel.send(f"{message.author.mention}, you don't have the required role to give skip tiles.")


async def handle_set_tile_command(message, args):
    # Check if the user has the required role
    if any(role.name == bingo_mod_role for role in message.author.roles):

        try:
            # Extract the team name or user ID and new tile from the arguments
            team_name = ' '.join(args[:-1]).lower()
            new_tile = int(args[-1])

            # Check if the team exists
            team = get_team_by_name_or_id(team_name)
            if not team:
                await message.channel.send(f"{message.author.mention}, team '{team_name}' not found.")
                return

            # Update the team's tile
            team['tile'] = int(new_tile)
            await save_to_json(json_file_path, teams)
            # Notify about the tile update
            await message.channel.send(
                f"{message.author.mention}, updated the tile for team '{team['name']}' to {new_tile}.")
        except():
            await message.channel.send(
                f"{message.author.mention}, invalid command format. Use {PREFIX}set_tile <team_name> <new_tile>")
    else:
        await message.channel.send(f"{message.author.mention}, you don't have the required role to set tile.")


def get_team_by_name_or_id(name_or_id):
    team = teams.get(str(name_or_id))

    if name_or_id in teams:
        return teams[name_or_id]

        # Check if the input is a team name
    for t in teams.values():
        if t['name'] == name_or_id:
            return t

    for t in teams.values():
        if name_or_id in t['members']:
            return t

    return None


async def handle_leaderboard_command(message):
    async def handle_leaderboard_command(message):
    '''if teams:
        # Sort teams based on their tile number in descending order
        sorted_teams = sorted(teams.values(), key=lambda x: x['tile'], reverse=True)
        leaderboard_info = "\n".join(
            [f"**{i + 1}. Team '{team['name']}'** - Tile: {team['tile']} - Tiles done: {team['tiles_done']} \n Completed tiles: {team['completed_tiles']}" for i, team in enumerate(sorted_teams)])
        await message.channel.send(f"**Leaderboard:**\n{leaderboard_info}")
    else:
        await message.channel.send("There are no teams yet!")

    team = get_team_by_name_or_id(message.author.id)

    for t in teams.values():
        if message.author.id in t['members']:
            team = t
            break'''
    if teams:

        sorted_teams = sorted(teams.values(), key=lambda x: x['tile'], reverse=True)

        embed = discord.Embed(title="Leaderboard!", description="Oooooh, I wonder who is winning?!?! Find out below:",
                              color=0x3498db)  # You can customize the color
        embed.timestamp = datetime.datetime.now()

        for i, team in enumerate(sorted_teams):
            print(i)
            print(team)
            completed_tiles_name = []
            for tile in team['completed_tiles']:
                completed = await handle_tile_result(message, tile, team)
                completed_tiles_name.append(completed)
            if i == 0:
                embed.set_thumbnail(url=team['team_logo'])
            sorted_completed_tiles = '\n'.join(completed_tiles_name)

            embed.add_field(name=f"**{i + 1} - {team['name'].title()}**",
                            value=f"Current tile:{await handle_tile_result(message, team['tile'], team)}\n"
                                  f"Tiles completed:{team['tiles_done']}",
                                  #f"Finished tiles: \n{sorted_completed_tiles}\n",
                            inline=True)
        await message.channel.send(embed=embed)


async def handle_team_players_command(message):
    author_id = str(message.author.id)

    if author_id in teams:
        team_id = teams[author_id]

        # Print the team_id for debugging
        print(f"Author ID: {author_id}, Team ID: {team_id}")

        # Check if the team_id exists in the dictionary
        if team_id in teams:
            team_players = [member for member in teams if teams[member] == team_id]

            # Print the team_players for debugging
            print(f"Team Players: {team_players}")

            if team_players:
                player_mentions = [f"<@{player}>" for player in team_players]
                player_list = ", ".join(player_mentions)
                await message.channel.send(f"Players in your team ({team_id}): {player_list}")
            else:
                await message.channel.send("Your team has no players.")
        else:
            await message.channel.send("Error: Team ID not found in teams dictionary.")
    else:
        await message.channel.send("You are not part of any team. Create a team using $create_team.")


async def handle_all_teams_command(message):
    embed = discord.Embed(title="All teams", description="List of all teams and their users!")
    embed.timestamp = datetime.datetime.now()
    embed.set_image(
        url="https://cdn.discordapp.com/banners/532377514975428628/76d2322eefb0c6794274302fa4a8512f.webp?size=240")
    if teams:
        teams_info = []
        for team in teams.values():
            member_mentions = [f"<@{member}>" for member in team['members']]
            team_info = f"**Team '{team['name']}'** - Members: {', '.join(member_mentions)}"
            teams_info.append(team_info)
            embed.add_field(name=f"**{team['name']}**",
                            value='\n'.join(member_mentions))

        teams_info_str = "\n".join(teams_info)
        # await message.channel.send(content=f"**All Teams:**\n{teams_info_str}", allowed_mentions=discord.AllowedMentions(users=False))
        await message.channel.send(embed=embed)

    else:
        await message.channel.send("There are no teams yet!")


async def handle_info_command(message):
    embed = discord.Embed(title="Command Help", description="Use these commands to interact with the game.",
                          color=0x3498db)  # You can customize the color
    embed.set_image(
        url="https://static.wikia.nocookie.net/logopedia/images/c/cc/Runescape_Logo.png/revision/latest?cb=20100701012035")
    embed.set_author(name="The Almighty RNG Street Discord")
    embed.set_thumbnail(
        url="https://cdn.discordapp.com/banners/532377514975428628/76d2322eefb0c6794274302fa4a8512f.webp?size=240")
    embed.timestamp = datetime.datetime.now()

    # Available Commands
    embed.add_field(name="**Available Commands:**",
                    value=f"`{PREFIX}info:` Show this help message.\n"
                          f"`{PREFIX}roll:` Roll the dice and move to a new tile.\n"
                          f"`{PREFIX}completed:` Mark your tile as completed.\n"
                    # f"`{PREFIX}current_tile`: Get your team's current tile.\n"
                          f"`{PREFIX}reroll:` Use a reroll to redo the previous roll.\n"
                    # f"`{PREFIX}skip:`: Skip the current tile and move to the next one.\n"
                          f"`{PREFIX}team:` Shows your current team details.\n"
                          f"`{PREFIX}all_teams:` Shows all teams and their members.\n"
                          f"`{PREFIX}leaderboard:` Shows the current standings.\n\n",
                    inline=False)
    if message.channel.id == 1206154823888801792:
        embed.add_field(name="**Mod Commands**",
                        value=f"`{PREFIX}create_team:` Create a new team.\n"
                              f"`{PREFIX}set_tile <team name><tile number>:` Moves a team to a specific tile.\n"
                              f"`{PREFIX}set_team @user <team name>:` Assign a user to a specific team.\n"
                              f"`{PREFIX}remove_user @user:` Removes a user from a specific team.\n"
                              f"`{PREFIX}start_game:` Starts the bingo game.\n"
                              f"`{PREFIX}stop_game:` Stops the bingo game.\n"
                              f"`{PREFIX}team_name:` Allows you to edit the name of the team\n"
                              f"`{PREFIX}reset:` Resets the game.\n\n",
                        inline=False)

    # Team Creation Commands
    '''embed.add_field(name="**Team Creation Commands:**",
                    value=f"`{PREFIX}create_team`: Create a new team.\n"
                          f"`{PREFIX}join <team name>`: Join an existing team.\n"
                    # f"`{PREFIX}set_team <@user> <team name>`: Sets a user to an existing team.\n"
                          f"`{PREFIX}all_teams`: List all existing teams and their members.\n",
                    # f"`{PREFIX}leave_team`: Leave your current team.\n\n",
                    inline=False)'''

    # Moderator Commands
    '''embed.add_field(name="**Moderator Commands**",
                    value=f"`{PREFIX}set_tile <tile_number>`: Set the current tile for your team.\n"
                          f"`{PREFIX}give_reroll <team name>`: Give a reroll to another team member.\n"
                          f"`{PREFIX}give_skip <team name>`: Give a skip tile to another team member.\n"
                          f"'{PREFIX}set_team @username <teamname>: Assign a user to a team.\n"
                          f"`{PREFIX}reset`: Reset the game.",
                    inline=False)'''

    # Send the embedded message
    await message.channel.send(embed=embed)

    '''await message.channel.send(
        f"**Available Commands:**\n"
        f"`{PREFIX}info`: Show this help message.\n"
        f"`{PREFIX}roll`: Roll the dice and move to a new tile.\n"
        f"`{PREFIX}completed`: Mark your tile as completed.\n"
        f"`{PREFIX}current_tile`: Get your team's current tile.\n"
        f"`{PREFIX}reroll`: Use a reroll to redo the previous roll.\n"
        f"`{PREFIX}skip_tile:`: Skip the current tile and move to the next one.\n"
        f"`{PREFIX}team_tile:`: Shows your current team and tile.\n"
        f"`{PREFIX}leaderboard`: Shows the current standings.\n\n"

        f"**Team Creation Commands:**\n"
        f"`{PREFIX}create_team`: Create a new team. (Team leaders only)\n"
        f"`{PREFIX}join <team name>`: Join an existing team\n"
        f"`{PREFIX}all_teams`: List all existing teams and their members.\n"
        f"`{PREFIX}leave_team`: Leave your current team.\n\n"

        f"**Moderator Commands**\n"
        f"`{PREFIX}set_tile <team name> <tile number>`: Set the current tile for your team.\n"
        f"`{PREFIX}give_reroll <team name> <amount>`: Give a reroll to another team member.\n"
        f"`{PREFIX}give_skip_tile <team name> <amount>`: Give a skip tile to another team member.\n"
        f"`{PREFIX}reset`: Reset the game."
    )'''


async def handle_skip_tile_command(message):
    # See if the user exists in a team
    team = get_team_by_name_or_id(message.author.id)

    if team:
        # Check if the user is a member of the team
        if message.author.id not in team['members']:
            await message.channel.send(f"{message.author.mention}, you are not a member of team '{team['name']}'!")
            return

        # Check if the team has completed the turn
        if team['has_completed']:
            await message.channel.send(
                f"{message.author.mention}, your team '{team['name']}' has completed its turn. Use `{PREFIX}roll` to start a new turn.")
            return

        # Check if the team has skips remaining
        if team['skips'] > 0:
            # Consume one skip
            team['skips'] -= 1

            # Update the team's current tile based on the dice roll
            new_tile = team['tile'] + 1  # Limit tiles to 0-50

            # check if tile is on a movement tile
            check_tile = check_tile_for_movement(new_tile, team, message)
            if new_tile != check_tile:
                await message.channel.send(
                    f"{message.author.mention}, You used a skip! Which means you moved forward to:")
                result_message = await handle_tile_result(message, new_tile, team)
                if result_message:
                    await message.channel.send(f"**{result_message}**")
                await message.channel.send(f"{message.author.mention}, that means you are moving to {check_tile}:")
                new_tile = check_tile
            else:
                # send the skip usage and the dice roll result with an update on the team's current tile
                await message.channel.send(
                    f"{message.author.mention}, you used a skip for team '{team['name']}'. You have now been moved forward 1 tile.")
                await asyncio.sleep(1)  # Introduce a delay to ensure correct order of messages
                await message.channel.send(
                    f"{message.author.mention}, your previous tile was {team['tile']}. Your new tile is now {new_tile}")

            # Provide the remaining skips information
            await message.channel.send(f"{message.author.mention}, you have {team['skips']} skip(s) remaining.")

            # Handle the result based on the tile
            result_message = handle_tile_result(message, new_tile, team)
            if result_message:
                await message.channel.send(f"**{result_message}**")

            # team['previous_tile'] = new_tile
            team['tile'] = new_tile
            await save_to_json(json_file_path, teams)


        else:
            await message.channel.send(
                f"{message.author.mention}, you don't have any skips remaining for team '{team['name']}'.")
    else:
        await message.channel.send(
            f"{message.author.mention}, you are not part of any team! Create a team using `{PREFIX}create_team`")


async def handle_remove_user_command(message, args):
    if any(role.name == bingo_mod_role for role in message.author.roles):
        if len(args) != 1:
            await message.channel.send(f"{message.author.mention}, please provide only a user to remove.")
            return

        # Extract mentioned user and team name from args
        user_mention = args[0]

        # Check if the mentioned user is valid
        try:
            user_id = int(user_mention.replace("<", "").replace(">", "").replace("@", "").replace("!", ""))
            mentioned_user = message.guild.get_member(user_id)
            team = (get_team_by_name_or_id(user_id))
            team_name = team['name']
        except ValueError:
            await message.channel.send(f"{message.author.mention}, please mention a valid user.")
            return
        except TypeError:
            await message.channel.send(f"{message.author.mention}, Provided user doesn't appear to be in any teams.")
            return

        if not mentioned_user:
            await message.channel.send(f"{message.author.mention}, please mention a valid user.")
            return

        # Check if the team name exists in the list of team names
        if any(t.lower() == team_name for t in teams):
            # Check if the user is already part of a team
            if any(mentioned_user.id in t['members'] for t in teams.values()):
                # Remove the mentioned user to the existing team
                team = teams[team_name]
                team['members'].remove(mentioned_user.id)
                await save_to_json(json_file_path, teams)
                await message.channel.send(
                    f"{message.author.mention}, {mentioned_user.mention} has been removed from: '{team_name}'!")
            else:
                await message.channel.send(
                    f"{message.author.mention}, {mentioned_user.mention} is not in a team!")
        else:
            await message.channel.send(f"{message.author.mention}, the team '{team_name}' does not exist!")
    else:
        await message.channel.send(
            f"{message.author.mention}, you don't have the required role to use this command.")


async def handle_tile_result(message, tile, team):
    if tile in tile_messages:
        result_message = tile_messages[tile]
        result_message = result_message.replace("SKIP", f"SKIP TO {team['tile'] + 2}")
        return result_message
        # await message.channel.send(f"**{result_message}**")
    else:
        return False


async def set_team_command(message, args):
    # Check if the user has the required role
    if any(role.name == bingo_mod_role for role in message.author.roles):
        if len(args) < 2:
            await message.channel.send(f"{message.author.mention}, please provide both a user and a team to join.")
            return

        # Extract mentioned user and team name from args
        user_mention = args[0]
        team_name = ' '.join(args[1:]).lower()

        # Check if the mentioned user is valid
        try:
            user_id = int(user_mention.replace("<", "").replace(">", "").replace("@", "").replace("!", ""))
            mentioned_user = message.guild.get_member(user_id)
        except ValueError:
            await message.channel.send(f"{message.author.mention}, please mention a valid user.")
            return

        if not mentioned_user:
            await message.channel.send(f"{message.author.mention}, please mention a valid user.")
            return

        # Check if the team name exists in the list of team names
        if any(t.lower() == team_name for t in teams):
            # Check if the user is already part of a team
            if any(mentioned_user.id in t['members'] for t in teams.values()):
                await message.channel.send(
                    f"{message.author.mention}, {mentioned_user.mention} is already part of a team!")
            else:
                # Add the mentioned user to the existing team
                team = teams[team_name]
                team['members'].append(mentioned_user.id)
                await save_to_json(json_file_path, teams)
                await message.channel.send(
                    f"{message.author.mention}, {mentioned_user.mention} has joined team '{team_name}'!")
        else:
            await message.channel.send(f"{message.author.mention}, the team '{team_name}' does not exist!")
    else:
        await message.channel.send(
            f"{message.author.mention}, you don't have the required role to use this command.")


async def handle_join_command(message, args):
    # Check if the user has the required role
    if any(role.name == bingo_player_role for role in message.author.roles):
        if not args or not args[0]:
            await message.channel.send(f"{message.author.mention}, please provide a team name to join.")
            return

        # If args is a list, take the first element as the team name
        team_name = ' '.join(args) if isinstance(args, list) else args.lower()

        team_id = str(message.author.id)

        # Check if the team name exists in the list of team names
        if any(t.lower() == team_name for t in teams):
            # Check if the user is already part of a team
            if any(message.author.id in t['members'] for t in teams.values()):
                await message.channel.send(f"{message.author.mention}, you are already part of a team!")
            else:
                # Add the user to the existing team
                team = teams[team_name]
                team['members'].append(message.author.id)
                await save_to_json(json_file_path, teams)
                await message.channel.send(f"{message.author.mention}, you have joined team '{team_name}'!")
        else:
            await message.channel.send(f"{message.author.mention}, the team '{team_name}' does not exist!")
    else:
        await message.channel.send(f"{message.author.mention}, You don't have the required roll to use this command.")


async def handle_roll_command(message, skip=False):
    team = get_team_by_name_or_id(message.author.id)

    if game_state:
        if team:
            if team['tile'] == tiles_max:
                await message.channel.send(
                    f"what are you doing trying to roll again? You have already finished... Congrats!")
                return
            else:
                # while True:
                # Check if the team has rolled for the current turn
                if team['has_rolled'] and not skip:
                    await message.channel.send(
                        f"{message.author.mention}, your team 'Team {team['name']}' has already rolled for this turn. Use `{PREFIX}reroll` if you want to reroll.")
                    return

                while True:
                    # Generate a random number between 1 and 6
                    dice_roll = generate_random_number()
                    testing_tile = team['tile'] + dice_roll
                    if testing_tile in team['has_landed']:
                        continue
                    else:
                        break
                if testing_tile >= tiles_max:
                    testing_tile = tiles_max


                    # Check if it's the first roll or a reroll
                if not team['has_rolled'] and not skip:
                    # Store the initial tile for the first roll or reroll
                    team['previous_tile'] = team['tile']

                # Update the team's current tile based on the dice roll
                new_tile = testing_tile
                check_tile = await check_tile_for_movement(new_tile, team, message)

                # check if tile is on a movement tile
                if new_tile != check_tile:
                    await message.channel.send(
                        f"{message.author.mention}, You rolled a #{dice_roll}! Which means you landed on:")
                    result_message = await handle_tile_result(message, new_tile, team)
                    if result_message:
                        await message.channel.send(f"**{result_message}**")

                    await message.channel.send(f"{message.author.mention}, that means you are moving to {check_tile}:")
                    new_tile = check_tile
                else:
                    await message.channel.send(
                        f"{message.author.mention}, you rolled a #{dice_roll}! Team {team['name']} is now on tile {new_tile}.")

                # Update the team's current tile if not skipping
                team['tile'] = new_tile

                # Set the 'has_rolled' flag to True
                team['has_rolled'] = True

                # Update 'previous_tile' for the next roll or reroll
                # team['previous_tile'] = new_tile

                # Update 'previous_roll' for the next roll or reroll
                team['previous_roll'] = dice_roll

                team['has_completed'] = False
                await save_to_json(json_file_path, teams)

                # Handle the result based on the tile
                result_message = await handle_tile_result(message, new_tile, team)
                if result_message:
                    await message.channel.send(f"**{result_message}**")
        else:
            await message.channel.send(
                f"{message.author.mention}, you are not part of any team! Create a team using `{PREFIX}create_team`")
    else:
        await message.channel.send(f"{message.author.mention}, the game hasn't started yet!")


async def handle_reroll_command(message):
    team = get_team_by_name_or_id(message.author.id)


    if team:
        # Check if the user is a member of the team
        if message.author.id not in team['members']:
            await message.channel.send(f"{message.author.mention}, you are not a member of team '{team['name']}'!")
            return

        # Check if the team has completed the turn
        if team['has_completed']:
            await message.channel.send(
                f"{message.author.mention}, your team '{team['name']}' has completed its turn. Use `{PREFIX}roll` to start a new turn.")
            return
        if team['previous_roll'] == 0:
            await message.channel.send(
                f"{message.author.mention}, your team '{team['name']}' needs to roll still! `{PREFIX}roll` to start a new turn.")
            return
        team['has_completed'] = True

        # Check if the team has rerolls remaining
        if team['rerolls'] > 0:
            while True:
                # Generate a random number between 1 and 6
                dice_roll = generate_random_number()
                testing_tile = team['previous_tile'] + dice_roll
                if dice_roll == team['previous_roll']
                    continue
                elif testing_tile in team['has_landed']:
                    continue
                else:
                    break
            if testing_tile >= tiles_max:
                testing_tile = tiles_max

            # Update the team's current tile based on the new dice roll
            new_tile = testing_tile  # Limit tiles to 0-50

            # Decrement the remaining rerolls
            team['rerolls'] -= 1

            # check if tile is on a movement tile
            check_tile = await check_tile_for_movement(new_tile, team, message)
            if new_tile != check_tile:
                await message.channel.send(
                    f"{message.author.mention}, You rerolled a #{dice_roll}! Which means you landed on:")
                result_message = await handle_tile_result(message, new_tile, team)
                if result_message:
                    await message.channel.send(f"**{result_message}**")
                await message.channel.send(f"{message.author.mention}, that means you are moving to {check_tile}:")
                new_tile = check_tile
            else:
                # Send the reroll result with an update on the team's current tile and remaining rerolls
                await message.channel.send(
                    f"{message.author.mention}, your teams previous roll was {team['previous_roll']}. \n"
                    f"{message.author.mention}, your previous tile was {team['previous_tile']}, you rerolled a {dice_roll}! Your team is now on tile {new_tile}.\n"
                    f"{message.author.mention}, your team has {team['rerolls']} reroll(s) remaining."
                )

            # Update 'previous_tile' for the next reroll
            # team['previous_tile'] = new_tile
            team['tile'] = new_tile

            # Update 'previous_roll' for the next reroll
            team['previous_roll'] = dice_roll
            print(teams)
            team['has_completed'] = False
            await save_to_json(json_file_path, teams)
            print("fucker")
            print(new_tile)


            # Handle the result based on the tile
            result_message = await handle_tile_result(message, new_tile, team)
            if result_message:
                print(result_message)
                await message.channel.send(f"**{result_message}**")
        else:
            await message.channel.send(
                f"{message.author.mention}, your team '{team['name']}' has no rerolls remaining.")
    else:
        await message.channel.send(
            f"{message.author.mention}, you are not part of any team! Create a team using `{PREFIX}create_team`")


def generate_random_number():
    return random.randint(1, 6)



async def handle_completed_command(message):
    team = get_team_by_name_or_id(message.author.id)

    if team:
        if team['tile'] == tiles_max:
            await message.channel.send(f"{message.author.mention}, nice. Now go have a shower you sweaty team.")
        else:
            # Check if the user is a member of the team
            if message.author.id not in team['members']:
                await message.channel.send(f"{message.author.mention}, you are not a member of team '{team['name']}'!")
                return

            # Check if the team has already completed
            if team['has_completed']:
                await message.channel.send(
                    f"{message.author.mention}, your team '{team['name']}' has already completed its turn.")
                return

            await check_tile_for_movement(team['tile'], team, message)
            # Set the 'has_completed' flag to True
            team['has_completed'] = True
            team['has_rolled'] = False
            team['tiles_done'] += 1
            team['completed_tiles'].append(team['tile'])
            await save_to_json(json_file_path, teams)
            await message.channel.send(
                f"{message.author.mention}, you have marked your turn as completed for team '{team['name']}'. Use `$roll` to start a new turn.")
    else:
        await message.channel.send(
            f"{message.author.mention}, you are not part of any team! Create a team using `$create_team`")


async def handle_create_team_command(message):
    if bingo_mod_role not in [role.name for role in message.author.roles]:
        await message.channel.send(
            f"{message.author.mention}, you don't have the required role to create a team.")
        return

    team = get_team_by_name_or_id(message.author.id)

    # if not team:
    # Prompt the user to specify a team name
    await message.channel.send(f"{message.author.mention}, enter a team name for your new team:")

    def check(msg):
        return msg.author == message.author and msg.channel == msg.channel

    try:
        team_name_message = await client.wait_for('message', check=check, timeout=30)
        try:
            '''await message.channel.send(f"{message.author.mention}, and a link to the team picture please :)")

            def check(msg):
                return msg.author == message.author and msg.channel == msg.channel

            team_picture_message = await client.wait_for('message', check=check, timeout=30)
            print(team_picture_message)
            team_picture = team_picture_message.content
            print(team_picture)'''
            team_name = team_name_message.content.lower()  # Convert the team name to lowercase

            # Create the team and add the user as the creator
            teams[team_name] = {'name': team_name, 'creator': message.author.id, 'members': [],
                                'tile': 0, 'rerolls': 0, 'skips': 0, 'previous_tile': 0, 'previous_roll': 0,
                                'has_rolled': False,
                                'has_completed': True,
                                'completed_tiles': [],
                                'team_logo': False,
                                'tiles_done': 0,
                                'has_landed': []}
            await save_to_json(json_file_path, teams)
            await message.channel.send(f"{message.author.mention}, you have created team '{team_name}'!")
        except asyncio.TimeoutError:
            await message.channel.send(f"{message.author.mention}, team creation timed out. Try again.")
    except asyncio.TimeoutError:
        await message.channel.send(f"{message.author.mention}, team creation timed out. Try again.")
    # else:
    # await message.channel.send(f"{message.author.mention}, you are already part of a team!")


async def handle_team_tile_command(message):
    team = (get_team_by_name_or_id(message.author.id))

    if team:
        '''await message.channel.send(
            f"{message.author.mention}, your team '{team['name']}' is on tile {team['tile']} and has {team['rerolls']} rerolls remaining.")'''
        embed = discord.Embed(title="Team info!", description=f"This is the info for the team: {team['name']}!!",
                              color=0x3498db)  # You can customize the color
        embed.timestamp = datetime.datetime.now()
        if team['team_logo']:
            embed.set_thumbnail(url=team['team_logo'])

        # Available Commands
        embed.add_field(name="**Team tile:**",
                        value=f"Your team is currently on:\n"
                              f"**{await handle_tile_result(message, team['tile'], team)}**\n\n",
                        inline=True)
        embed.add_field(name="**Team Rerolls Remaining:**",
                        value=f"Your team currently has **{team['rerolls']}** rerolls Remaining\n\n",
                        inline=True)
        await message.channel.send(embed=embed)

    else:
        await message.channel.send(
            f"{message.author.mention}, you are not part of any team! Create a team using {PREFIX}create_team")


async def handle_team_tile_old_command(message):
    team = (get_team_by_name_or_id(message.author.id))

    if team:
        await message.channel.send(
            f"{message.author.mention}, your team '{team['name']}' is on tile {team['tile']} and has {team['rerolls']} rerolls remaining.")

    else:
        await message.channel.send(
            f"{message.author.mention}, you are not part of any team! Create a team using {PREFIX}create_team")


async def handle_leave_team_command(message):
    author_id = str(message.author.id)
    team = get_team_by_name_or_id(message.author.id)

    if teams:
        author_id.isdigit()
        team['members'].remove(message.author.id)
        await save_to_json(json_file_path, teams)
        await message.channel.send(f"{message.author.mention} has left the team.")
    else:
        await message.channel.send("You are not part of any team.")


'''async def handle_current_tile_command(message):
    team = get_team_by_name_or_id(message.author.id)

    if team:
        current_tile = team['tile']
        await message.channel.send(f"{message.author.mention}, your team '{team['name']}' is on tile {current_tile}.")
    else:
        await message.channel.send(
            f"{message.author.mention}, you are not part of any team! Create a team using `{PREFIX}create_team`")'''

client.run(TOKEN)
