import discord
from discord import app_commands
from discord.ext import commands
import json
import re
import kklubdatabase
import pindatabase

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

config_file = open("config.json")
config = json.load(config_file)

bot.remove_command("help")

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





@bot.tree.command(name="add_kklub",
                  description="It's in the name")
@app_commands.describe(username="Who to add kklub")
async def add_kklub(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    username_id = username[2:]
    username_id = username_id[:-1]
    username_id = username_id.replace("!", "")

    if (username_id.isdigit()):
        kklubdatabase.add_points(username_id, 1)
    else:
        from_server = interaction.guild
        user = from_server.get_member_named(username)
        if (user == None):
            await interaction.followup.send("Invalid User")
            return
        else:
            kklubdatabase.add_points(user.id, 1)
    await interaction.followup.send(username + " has received a kklub")
@bot.tree.command(name="add_pin_report",
                  description="It's in the name")
@app_commands.describe(username="Who to pin Report")
async def add_pin_report(interaction: discord.Interaction, username: str):
    await interaction.response.defer()

    from_server = interaction.guild
    username_id = username[2:]
    username_id = username_id[:-1]
    username_id = username_id.replace("!", "")

    if (username_id.isdigit()):
        user = from_server.get_member(int(username_id))
        for role in user.roles:
            if (role.name == "Pledges"):
                pindatabase.add_points(username_id, 1)
                await interaction.followup.send(username + " has received a Pin Violation")
                return
        await interaction.followup.send("That's not A pledge NERD")
        return

    else:
        user = from_server.get_member_named(username)
        if (user == None):
            await interaction.followup.send("Invalid User")
            return
        else:
            for role in user.roles:
                if (role.name == "Pledges"):
                    pindatabase.add_points(user.id, 1)
                    await interaction.followup.send(username + " has received a Pin Violation")
                    break
            await interaction.followup.send("That's not A pledge NERD")
            return



@bot.tree.command(name='remove_kklub', description= config["remove_kklub"])
@app_commands.describe(username="Who to remove kklub")
async def remove_kklub(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    roles = interaction.user.roles
    permission = False
    for role in roles:
        if(role.permissions.administrator):
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
        kklubdatabase.remove_points(username_id, point)
    else:
        from_server = interaction.guild
        user = from_server.get_member_named(username)
        if (user == None):
            await interaction.followup.send("Invalid user")
            return
        else:
            kklubdatabase.remove_points(user.id, point)
    await interaction.followup.send("KKClub removed from " + str(username) + "!")

@bot.tree.command(name='remove_pin_report', description= config["remove_pin_report"])
@app_commands.describe(username="Who to remove kklub")
async def remove_pin_report(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    roles = interaction.user.roles
    permission = False
    for role in roles:
        if(role.permissions.administrator):
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
        pindatabase.remove_points(username_id, point)
    else:
        from_server = interaction.guild
        user = from_server.get_member_named(username)
        if (user == None):
            await interaction.followup.send("Invalid user")
            return
        else:
            pindatabase.remove_points(user.id, point)
    await interaction.followup.send("pin report removed from " + str(username) + "!")



@bot.tree.command(name="check_kklubs",
                  description=config["check_kklubs"])
async def check_kklub(interaction: discord.Interaction):
    await interaction.response.defer()
    points = kklubdatabase.get_user_point(interaction.user.id)
    await interaction.followup.send("You have " + str(points) + " KKclub(s)")
    return
@bot.tree.command(name="check_pin_report",
                  description=config["check_pin_report"])
async def check_pin_report(interaction: discord.Interaction):
    await interaction.response.defer()
    user = interaction.user
    for role in user.roles:
        if(role == "pledges"):
            points = pindatabase.get_user_point(interaction.user.id)
            await interaction.followup.send("You have " + str(points) + " KKclub(s)")
            return
    await interaction.followup.send("Ur not a pledge Nerd")



@bot.tree.command(name="check_kklub_leaderboard", description=config["check_kklub_leaderboard"])
async def check_kklub_leaderboard(interaction: discord.Interaction):
    await interaction.response.defer()
    rows = kklubdatabase.get_users(1)

    embed = discord.Embed(title="KKlub Leaderboard", color=0x8150bc)
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
    kklubdatabase.add_leaderboard(interaction.user.id, msg_sent.id, count)
    if (count == 11):
        await msg_sent.add_reaction(u"\u25B6")
@bot.tree.command(name="check_pin_report_leaderboard", description=config["check_pin_report_leaderboard"])
async def check_pin_report_leaderboard(interaction: discord.Interaction):
    await interaction.response.defer()
    rows = pindatabase.get_users(1)

    embed = discord.Embed(title="Pin Report Leaderboard", color=0x8150bc)
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
    pindatabase.add_leaderboard(interaction.user.id, msg_sent.id, count)
    if (count == 11):
        await msg_sent.add_reaction(u"\u25B6")



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

    embed.add_field(name="General Commands", value="", inline=False)
    embed.add_field(name="/help", value=config["help"], inline=False)
    await interaction.followup.send(embed=embed)


@bot.tree.command(name="reset_kklubs",
                  description=config["reset_kklubs"])
async def reset_kklubs(interaction: discord.Interaction):
    await interaction.response.defer()
    permission = False
    roles = interaction.user.roles
    for role in roles:
        if (role.permissions.administrator):
            permission = True

    if (permission):
        await kklubdatabase.reset_database()
        await interaction.followup.send("Database was rest!")
    else:
        await interaction.followup.send("No permision!")

@bot.tree.command(name="reset_pin_reports",
                  description=config["reset_pin_reports"])
async def reset_pin_reports(interaction: discord.Interaction):
    await interaction.response.defer()
    permission = False
    roles = interaction.user.roles
    for role in roles:
        if (role.permissions.administrator):
            permission = True

    if (permission):
        await pindatabase.reset_database()
        await interaction.followup.send("Database was reset!")
    else:
        await interaction.followup.send("No permision!")


@bot.event
async def on_reaction_add(reaction, user):
    if (kklubdatabase.check_leaderboard(reaction.message.id, user.id)):
        if (reaction.emoji == u"\u25B6"):
            page, last_user_count = kklubdatabase.get_leaderboard_page(reaction.message.id, user.id)
            if (last_user_count < page * 10):
                return
            rows = kklubdatabase.get_users(page + 1)
            embed = discord.Embed(title="Leaderboard", color=0x8150bc)
            for row in rows:

                if(row[1] != None and row[2] != None):
                    user_name = user.guild.get_member(int(row[1])).display_name
                    user_name = "#" + str(last_user_count) + " | " + str(user_name)
                    embed.add_field(name=user_name, value='{:,}'.format(row[2]), inline=False)
                    last_user_count += 1

            kklubdatabase.update_leaderboard(page + 1, last_user_count, reaction.message.id)
            await reaction.message.edit(embed=embed)
            await reaction.message.clear_reactions()
            await reaction.message.add_reaction(u"\u25C0")
            if (last_user_count > (page + 1) * 10):
                await reaction.message.add_reaction(u"\u25B6")

        if (reaction.emoji == u"\u25C0"):
            page, last_user_count = kklubdatabase.get_leaderboard_page(reaction.message.id, user.id)
            if (page == 1):
                return
            rows = kklubdatabase.get_users(page - 1)
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

            kklubdatabase.update_leaderboard(page - 1, last_user_count, reaction.message.id)
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

        if (permission and kklubdatabase.check_requests(reaction.message.id) and not user.bot):
            users, points = kklubdatabase.get_users_requests(reaction.message.id)
            split_users = users.split()
            for user_id in split_users:
                kklubdatabase.add_points(user_id, points)

            kklubdatabase.update_requests(reaction.message.id, 1)
            await reaction.message.add_reaction('\U00002705')


@bot.event
async def on_message_edit(before, after):
    if (kklubdatabase.check_requests(after.id)):
        kklubdatabase.update_requests(after.id, -1)


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

        kklubdatabase.insert_points_requests(interaction.message.id, saved_users, split_message[len(split_message) - 1], 0,
                               interaction.message.author.id)

        users_req = saved_users.split()
        for user in users_req:
            kklubdatabase.add_points(user, 1)

        await interaction.followup.send("KKClub added")



bot.run(config["bot_token"])


# @bot.command(pass_context = True)
# async def kklub(ctx, command = None, username = None, point = 1):
#     #print(username)
#
#
#     if(command == None or username == None):
#         if(command == None and username == None):
#             points = get_user_point(ctx.message.author.id)
#             await ctx.send("You have " + str(points) + " KKclub(s)")
#             return
#         else:
#             await ctx.send("Invalid command, please check the documentation: \n!kkclub [add/remove] <username> <points>")
#             return
#
#     roles = ctx.message.author.roles
#     permission = True
#
#     for role in roles:
#         if(role.name == "Manager" or role.permissions.administrator):
#             permission = True
#
#     if(not permission):
#         await request_points(ctx)
#         #await ctx.send("No permission")
#         return
#
#     if(command.lower() == "add"):
#
#             username_id = username[2:]
#             username_id = username_id[:-1]
#             username_id = username_id.replace("!","")
#
#
#             if(username_id.isdigit()):
#                 kklubdatabase.add_points(username_id, 1)
#             else:
#                 from_server = ctx.guild
#                 user = from_server.get_member_named(username)
#                 if(user == None):
#                     await ctx.send("Invalid user")
#                     return
#                 else:
#                     kklubdatabase.add_points(user.id, 1)
#             await ctx.send("KKlub added!")
#
#     else:
#         if(command.lower() == "remove"):
#
#                 username_id = username[2:]
#                 username_id = username_id[:-1]
#                 username_id = username_id.replace("!","")
#                 if(username_id.isdigit()):
#                     remove_points(username_id, point)
#                 else:
#                     from_server = ctx.guild
#                     user = from_server.get_member_named(username)
#                     if(user == None):
#                         await ctx.send("Invalid user")
#                         return
#                     else:
#                         remove_points(user.id,point)
#                 await ctx.send("KKClub removed!")
#
#         else:
#             await ctx.send("Invalid command, please check the documentation: \n!points [add/remove] <username> <points>")
#
# @bot.command(pass_context = True)
# async def help(ctx):
#     embed = discord.Embed(title = "Help command list", color=0x8150bc)
#     embed.add_field(name = "!leaderboard", value = config["leaderboard_help"], inline = False)
#     embed.add_field(name = "!kkclubs", value = config["points_help"], inline = False)
#     embed.add_field(name = "!help", value = config["help_help"], inline = False)
#     await ctx.send(embed = embed)
# @bot.command(pass_context = True)
# async def leaderboard(ctx):
#     rows = kklubdatabase.get_users(1)
#     embed = discord.Embed(title = "Kklub Leaderboard", color=0x8150bc)
#     count = 1
#     for row in rows:
#         if(row[1] != None and row[2] != None):
#             user = bot.get_user(int(row[1]))
#             user = "#" + str(count) + " | " + str(user)
#             embed.add_field(name = user, value = '{:,}'.format(row[2]), inline=False)
#             count += 1
#
#     msg_sent = await ctx.send(embed=embed)
#     add_leaderboard(ctx.message.author.id, msg_sent.id, count)
#     if(count == 11):
#         await msg_sent.add_reaction(u"\u25B6")
# @bot.command(pass_context = True)
# async def reset(ctx):
#     permission = False
#     roles = ctx.user.roles
#     for role in roles:
#         if role.permissions.administrator:
#             permission = True
#
#     if (permission):
#         await reset_database()
#         await ctx.send("Database was rest!")
#     else:
#          await ctx.send("No permision!")
# @bot.command(pass_context = True)
# async def pinReport(ctx, command = None, username =None, point = 1):
#     is_pledge = False
#     roles = ctx.message.author.roles
#     permission = True
#
#     for role in roles:
#         if (role.name == "Manager" or role.permissions.administrator):
#             permission = True
#     for role in roles:
#         if role.name == "Pledges":
#             is_pledge = True
#
#     if (command == None or username == None):
#         if (command == None and username == None):
#             if (is_pledge):
#                 points = pindatabase.get_user_point(ctx.message.author.id)
#                 await ctx.send("You have " + str(points) + " PinReport(s)")
#                 return
#             else:
#                 await ctx.send("Ur not a Pledge Nerd")
#                 return
#
#     if command.lower() == "add":
#
#         username_id = username[2:]
#         username_id = username_id[:-1]
#         username_id = username_id.replace("!", "")
#
#         if username_id.isdigit():
#             from_server = ctx.guild
#             user = bot.get_user(int(username_id))
#             user = user.name
#             user = from_server.get_member_named(user)
#             for role in user.roles:
#                 if role.name == "Pledges":
#                     pindatabase.add_points(username_id, 1)
#                     await ctx.send("Pin Violation Reported")
#                     return
#
#         else:
#             from_server = ctx.guild
#             user = from_server.get_member_named(username)
#             if (user == None):
#                 await ctx.send("Invalid user")
#                 return
#             else:
#                 for role in user.roles:
#                     if role.name == "Pledges":
#                         pindatabase.add_points(user.id, 1)
#                         await ctx.send("Pin Violation Reported")
#                         return
#         await ctx.send("Not a Pledge Nerd")
#
#
#
#
#
#
#
#
# @bot.tree.command()
# async def pinleaderboard(interactions: discord.Interaction):
#     rows = pindatabase.get_users(1)
#     embed = discord.Embed(title = "Pin Report Leaderboard", color=0x8150bc)
#     count = 1
#     for row in rows:
#         if(row[1] != None and row[2] != None):
#             user = bot.get_user(int(row[1]))
#             user = "#" + str(count) + " | " + str(user)
#             embed.add_field(name = user, value = '{:,}'.format(row[2]), inline=False)
#             count += 1
#
#     msg_sent = await interactions.send(embed=embed)
#     pindatabase.add_leaderboard(interactions.message.author.id, msg_sent.id, count)
#     if(count == 11):
#         await msg_sent.add_reaction(u"\u25B6")


