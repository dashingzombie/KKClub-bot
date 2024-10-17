import discord
from discord import app_commands
from discord.ext import commands
import json
import re
import database as db

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

config_file = open("config.json")
config = json.load(config_file)

bot.remove_command("help")
# Set up databases
pin_database = db.Database('pindiscodatabase.db')
kklub_database = db.Database('kklubdiscodatabase.db')
blacklist_database = db.Database('blacklist_database.db')

##create hooks so bot doesn't forget itself when it idles
@bot.event
async def setup_hook():
    try:
        synced = await bot.tree.sync()
        print("Synced Commands: " + str(synced))
    except Exception as e:
        print("Booooof Something went wrong")

@bot.event
async def on_ready():
    print("KKlub Bot is running")


##DATABASE CODE - Stuff that gets reused a fuck ton
async def remove_row(interaction: discord.Interaction, username: str, database: db.Database, title: str):
    await interaction.response.defer()
    roles = interaction.user.roles
    permission = False
    for role in roles:
        if (role.permissions.administrator):
            permission = True
            break

    if (not permission):
        await interaction.followup.send('No permission')
        # await ctx.send("No permission")
        return
    point = 1
    username_id = username[2:]
    username_id = username_id[:-1]
    username_id = username_id.replace("!", "")
    if (username_id.isdigit()):
        database.remove_points(username_id, point)
    else:
        from_server = interaction.guild
        user = from_server.get_member_named(username)
        if (user == None):
            await interaction.followup.send("Invalid User. Use the format @(Name of Person)")
            return
        else:
            database.remove_points(user.id, point)
    await interaction.followup.send(title + " removed from " + str(username) + "!")

async def add_row(interaction: discord.Interaction, username: str, database: db.Database, title: str):
    username = str(username)
    username_id = username[2:]
    username_id = username_id[:-1]
    username_id = username_id.replace("!", "")

    if (username_id.isdigit()):
        database.add_points(username_id, 1)
    else:
        from_server = interaction.guild
        user = from_server.get_member_named(username)
        if (user == None):
            await interaction.followup.send("Invalid User. Use the format @(Name of Person)")
            return
        else:
            database.add_points(str(user.id), 1)
    await interaction.followup.send(username + " has " + title + ".")

async def leaderboard(interaction: discord.Interaction, database: db.Database, title: str):
    await interaction.response.defer()
    rows = database.get_users(1)

    embed = discord.Embed(title=title, color=0x8150bc)
    count = 1

    for row in rows:
        if (row[1] != None and row[2] != None):
            user = bot.get_user(int(row[1]))
            if user == None:
                continue
            user = interaction.guild.get_member(user.id).display_name
            user = "#" + str(count) + " | " + str(user)
            embed.add_field(name=user, value='{:,}'.format(row[2]), inline=False)
            count += 1

    await interaction.followup.send(embed=embed)
    msg_sent = interaction
    database.add_leaderboard(interaction.user.id, msg_sent.id, count)
    if (count == 11):
        await msg_sent.add_reaction(u"\u25B6")

async def reset_database(interaction: discord.Interaction, database: db.Database):
    await interaction.response.defer()
    permission = False
    roles = interaction.user.roles
    for role in roles:
        if (role.permissions.administrator):
            permission = True

    if (permission):
        await database.reset_database()
        await interaction.followup.send("Database was reset!")
    else:
        await interaction.followup.send("No permission!")

async def get_user(interaction: discord.Interaction, username: str) -> discord.Member:
    username = str(username)
    username_id = username[2:]
    username_id = username_id[:-1]
    username_id = username_id.replace("!", "")

    from_server = interaction.guild
    if not username_id.isdigit():
        return None
    user = from_server.get_member(int(username_id))

    return user



# KKLUB CODE - kklub commands
@bot.tree.command(name="add_kklub",
                  description="It's in the name")
@app_commands.describe(username="Who to add kklub")
async def add_kklub(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    points = blacklist_database.get_user_point(interaction.user.id)
    if points > 0:
        await interaction.followup.send("You are not allowed to kklub someone")
        return
    await add_row(interaction, username, kklub_database, "been KKlubed")

@bot.tree.command(name='remove_kklub', description= config["remove_kklub"])
@app_commands.describe(username="Who to remove kklub")
async def remove_kklub(interaction: discord.Interaction, username: str):
    await remove_row(interaction, username, kklub_database, title = "Kklub")
    return

@bot.tree.command(name="check_kklubs",
                  description=config["check_kklubs"])
async def check_kklub(interaction: discord.Interaction):
    await interaction.response.defer()
    points = kklub_database.get_user_point(interaction.user.id)
    await interaction.followup.send("You have " + str(points) + " KKclub(s)")
    return

@bot.tree.command(name="check_kklub_leaderboard", description=config["check_kklub_leaderboard"])
async def check_kklub_leaderboard(interaction: discord.Interaction):
    await leaderboard(interaction, database = kklub_database, title = "KKlub Leaderboard" )

@bot.tree.command(name="reset_kklubs",
                  description=config["reset_kklubs"])
async def reset_kklubs(interaction: discord.Interaction):
    await reset_database(interaction, kklub_database)

# PIN REPORT CODE


@bot.tree.command(name="add_pin_report",
                  description="It's in the name")
@app_commands.describe(username="Who to pin Report")
async def add_pin_report(interaction: discord.Interaction, username: str):
    await interaction.response.defer()

    user = await get_user(interaction, username)
    if user is None:
        await interaction.followup.send("Invalid User. Use the format @(Name of Person)")
        return
    roles = [role.name for role in user.roles]

    if not roles.__contains__("Pledges"):
        await interaction.followup.send("Not a Pledge Nerd")
        return

    await add_row(interaction, username, pin_database, "received a PIN VIOLATION")



@bot.tree.command(name='remove_pin_report', description= config["remove_pin_report"])
@app_commands.describe(username="Who to remove kklub")
async def remove_pin_report(interaction: discord.Interaction, username: str):
    await remove_row(interaction, username, pin_database, title = "Pin Violation")
    return


@bot.tree.command(name="check_pin_report",
                  description=config["check_pin_report"])
async def check_pin_report(interaction: discord.Interaction):
    await interaction.response.defer()
    user = interaction.user
    roles = [role.name for role in user.roles]
    if roles.__contains__("Pledges"):
        points = pin_database.get_user_point(interaction.user.id)
        await interaction.followup.send("You have " + str(points) + " Pin Report(s)")
        return
    await interaction.followup.send("Ur not a pledge Nerd")



@bot.tree.command(name="check_pin_report_leaderboard", description=config["check_pin_report_leaderboard"])
async def check_pin_report_leaderboard(interaction: discord.Interaction):
    await leaderboard(interaction, database=pin_database, title="Pin Report Leaderboard")

@bot.tree.command(name="reset_pin_reports",
                  description=config["reset_pin_reports"])
async def reset_pin_reports(interaction: discord.Interaction):
    await reset_database(interaction, pin_database)

#BLACKLIST CODE - for people abusing kklub bot

@bot.tree.command(name="add_shame",
                  description= config["add_blacklist"])
@app_commands.describe(username="Who to add shame")
async def add_shame(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    roles = interaction.user.roles
    permission = False
    for role in roles:
        if role.permissions.administrator:
            permission = True
            break

    if not permission:
        await interaction.followup.send('MUST HAVE ADMINISTRATIVE PERMISSION')
        return
    user = await get_user(interaction, username)
    points = blacklist_database.get_user_point(user.id)
    if points > 0:
        await interaction.followup.send(username + " is already shammed")
        return

    await add_row(interaction, username, blacklist_database, " HAS BEEN SHAMMED")

@bot.tree.command(name='remove_shame', description= config["remove_blacklist"])
@app_commands.describe(username="Who to remove shame")
async def remove_shame(interaction: discord.Interaction, username: str):
    await remove_row(interaction, username, blacklist_database, title = "Blacklist")
    return

@bot.tree.command(name="check_shame",
                  description=config["check_blacklist"])
async def check_shame(interaction: discord.Interaction):
    await interaction.response.defer()
    points = blacklist_database.get_user_point(interaction.user.id)
    if(points == 0):
        await interaction.followup.send("You are not on the blacklist")
        return
    await interaction.followup.send("You are on the blacklist for abusing the bot")

@bot.tree.command(name="wall_of_shame", description=config["wall_of_shame"])
async def wall_of_shame(interaction: discord.Interaction):
    await leaderboard(interaction, database = blacklist_database, title = "WALL OF SHAME" )

@bot.tree.command(name="reset_shame_database",
                  description=config["reset_blacklist"])
async def reset_shame_database(interaction: discord.Interaction):
    await reset_database(interaction, blacklist_database)


#GENERAL CODE
@bot.tree.command(name="help",
                  description=config["help"])
async def help(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(title="Help command list", color=0x8150bc)
    embed.add_field(name="KKlub Commands", value="", inline=False)
    embed.add_field(name="/check_kklub_leaderboard", value=config["check_kklub_leaderboard"], inline=False)
    embed.add_field(name="/add_kklubs <username>", value=config["add_kklub"], inline=False)
    embed.add_field(name="/check_kklubs", value=config["check_kklubs"], inline=False)
    embed.add_field(name="/remove_kklubs <username>", value=config["remove_kklub"], inline=False)
    embed.add_field(name="/reset_kklubs", value=config["reset_kklubs"], inline=False)
    embed.add_field(name="", value="", inline=False)

    embed.add_field(name="Pin Report Commands", value="", inline=False)
    embed.add_field(name="/check_pin_report_leaderboard", value=config["check_pin_report_leaderboard"], inline=False)
    embed.add_field(name="/add_pin_report <username>", value=config["add_pin_report"], inline=False)
    embed.add_field(name="/check_pin_report", value=config["check_pin_report"], inline=False)
    embed.add_field(name="/remove_pin_report <username>", value=config["remove_pin_report"], inline=False)
    embed.add_field(name="/reset_pin_reports", value=config["reset_pin_reports"], inline=False)
    embed.add_field(name="", value="", inline=False)

    embed.add_field(name="Shame", value="", inline=False)
    embed.add_field(name="/add_shame <username>", value=config["add_blacklist"], inline=False)
    embed.add_field(name="/remove_shame <username>", value=config["remove_blacklist"], inline=False)
    embed.add_field(name="/check_shame", value=config["check_blacklist"], inline=False)
    embed.add_field(name="/wall_of_shame ", value=config["wall_of_shame"], inline=False)
    embed.add_field(name="/reset_shame_database", value=config["reset_blacklist"], inline=False)
    embed.add_field(name="", value="", inline=False)


    embed.add_field(name="General Commands", value="", inline=False)
    embed.add_field(name="/help", value=config["help"], inline=False)
    await interaction.followup.send(embed=embed)





@bot.event
async def on_reaction_add(reaction, user):
    if (kklub_database.check_leaderboard(reaction.message.id, user.id)):
        if (reaction.emoji == u"\u25B6"):
            page, last_user_count = kklub_database.get_leaderboard_page(reaction.message.id, user.id)
            if (last_user_count < page * 10):
                return
            rows = kklub_database.get_users(page + 1)
            embed = discord.Embed(title="Leaderboard", color=0x8150bc)
            for row in rows:

                if(row[1] != None and row[2] != None):
                    user_name = user.guild.get_member(int(row[1])).display_name
                    user_name = "#" + str(last_user_count) + " | " + str(user_name)
                    embed.add_field(name=user_name, value='{:,}'.format(row[2]), inline=False)
                    last_user_count += 1

            kklub_database.update_leaderboard(page + 1, last_user_count, reaction.message.id)
            await reaction.message.edit(embed=embed)
            await reaction.message.clear_reactions()
            await reaction.message.add_reaction(u"\u25C0")
            if (last_user_count > (page + 1) * 10):
                await reaction.message.add_reaction(u"\u25B6")

        if (reaction.emoji == u"\u25C0"):
            page, last_user_count = kklub_database.get_leaderboard_page(reaction.message.id, user.id)
            if (page == 1):
                return
            rows = kklub_database.get_users(page - 1)
            embed = discord.Embed(title="Leaderboard", color=0x8150bc)
            if (last_user_count <= page * 10):
                last_user_count -= 10 + (last_user_count - 1) % 10
            else:
                last_user_count -= 20

            for row in rows:

                if(row[1] != None and row[2] != None):
                    user_name = user.guild.get_member(int(row[1])).display_name
                    user_name = "#" + str(last_user_count) + " | " + str(user_name)
                    embed.add_field(name=user_name, value='{:,}'.format(row[2]), inline=False)
                    last_user_count += 1

            kklub_database.update_leaderboard(page - 1, last_user_count, reaction.message.id)
            await reaction.message.edit(embed=embed)
            await reaction.message.clear_reactions()
            if (page - 1 > 1):
                await reaction.message.add_reaction(u"\u25C0")
            await reaction.message.add_reaction(u"\u25B6")

    if (reaction.emoji == u"\U0001F44D"):
        roles = user.roles

        permission = False

        for role in roles:
            if (role.name == "Manager" or role.permissions.administrator or role.name == "Exec Board Members"):
                permission = True

        if (permission and kklub_database.check_requests(reaction.message.id) and not user.bot):
            users, points = kklub_database.get_users_requests(reaction.message.id)
            split_users = users.split()
            for user_id in split_users:
                kklub_database.add_points(user_id, points)

            kklub_database.update_requests(reaction.message.id, 1)
            await reaction.message.add_reaction('\U00002705')


@bot.event
async def on_message_edit(before, after):
    if (kklub_database.check_requests(after.id)):
        kklub_database.update_requests(after.id, -1)


@bot.event
async def on_command_error(ctx, error):
    try:
        await request_points(ctx)
    except Exception as e:
        print("Some shit happened: " + str(error))
        print("Error from try catch : " + str(e))


async def format_user(user_name):
    for i in range(len(user_name)):
        if (user_name[i] != ' '):
            break
        else:
            user_name = user_name[1:]

    for i in user_name[::-1]:
        if (i != " "):
            break
        else:
            user_name = user_name[:-1]
    return user_name


async def request_points(interaction: discord.Interaction):
    # print("here it go")
    message_sent = interaction.message.content
    if (message_sent[:12] == "!points add "):
        message_sent = message_sent[12:]
        split_message = re.split('\s+', message_sent)
        users = ''
        # print(split_message)
        for i in range(0, len(split_message) - 1):
            users += split_message[i]
            users += ' '

        users = users[:-1]
        # print(users)
        split_users = users.split(',')
        saved_users = ''
        # print(split_users)
        for user in split_users:
            user = await format_user(user)
            # print(user)
            if (user[:1] == '"' and user[-1:] == '"'):
                user = user[1:]
                user = user[:-1]
                # print(user)
                user_id = interaction.guild.get_member_named(user)
                if (user_id == None):
                    await interaction.followup.send("The following user does not exist: " + str(
                        user) + "\nPlease do not use white spaces between users and commas")
                    return

                saved_users += str(user_id.id)
                saved_users += ' '
            elif (user[:1] == "<"):
                user = user.strip()
                user = user[2:]
                user = user[:-1]
                user = user.replace("!", "")
                if (user.isdigit()):
                    found = bot.get_user(int(user))
                else:
                    await interaction.followup.send(
                        "The following user does not exist : " + str(user) + "\nPlease use comma between users!")
                    return

                if (found == None):
                    await interaction.followup.send(
                        "The following user does not exist : " + str(user) + "\nPlease use comma between users!")
                    return

                saved_users += str(user)
                saved_users += ' '
            elif (user[-1:] == ">"):
                user = user.strip()
                user = user[2:]
                user = user[:-1]
                user = user.replace("!", "")
                if (user.isdigit()):
                    found = bot.get_user(int(user))
                else:
                    await interaction.followup.send(
                        "The following user does not exist : " + str(user) + "\nPlease use comma between users!")
                    return

                found = bot.get_user(user)
                if (found == None):
                    await interaction.followup.send(
                        "The following user does not exist : " + str(user) + "\nPlease use comma between users!")
                    return
                saved_users += str(user)
                saved_users += ' '
            else:
                # print("Ja")
                user_id = interaction.guild.get_member_named(user)
                if (user_id == None):
                    await interaction.followup.send("The following user does not exist : " + str(user))
                    return
                saved_users += str(user_id.id)
                saved_users += ' '

        kklub_database.insert_points_requests(interaction.message.id, saved_users, split_message[len(split_message) - 1], 0,
                               interaction.message.author.id)

        users_req = saved_users.split()
        for user in users_req:
            kklub_database.add_points(user, 1)

        await interaction.followup.send("KKClub added")



bot.run(config["bot_token"])


