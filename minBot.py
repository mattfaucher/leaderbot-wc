import discord
import json
import random
from discord.ext import commands, tasks
from operator import itemgetter

from discord.ext.commands import has_permissions

TOKEN = 'Njk0MjQ4NjE3NzI4Mjc4NTM4.XoI4dQ.I_JZvxoSnLnQ_E_TXd0_3X9uClw'
client = commands.Bot(command_prefix = '!')


@client.event
async def on_ready():
    await client.change_presence(status = discord.Status.online, activity = discord.Game('Keeping Score'))
    print('Bot online')


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Use !help <command> to see proper command usage.')


# displays current ping
@client.command()
async def ping(ctx):
    await ctx.send(f'{ctx.author.mention} -> Ping: {round(client.latency * 1000)}ms')


# Adds a duo to the data file
@client.command()
async def add_duo(ctx, person1, person2):
    with open('leaderboard.json', 'r') as f:
        leaderboard_data = json.load(fp=f)

    updated_leaderboard = await update_duos(leaderboard_data, person1, person2)

    with open('leaderboard.json', 'w') as f:
        json.dump(updated_leaderboard, fp = f, indent= 4)

    length = len(leaderboard_data) - 1
    await ctx.send(f'{ctx.author.mention}\nDuo: {person1} & {person2}\n'
                   f'ID: {leaderboard_data[length]["id"]}\n'
                   f'Points: {leaderboard_data[length]["points"]}')

    await check_duplicates(leaderboard_data)
    print(check_duplicates(leaderboard_data))


# Displays the points system for the games + tags whoever called the command
@client.command()
async def points(ctx):
    await ctx.send(f'{ctx.author.mention} -> Point rules: 7pts for win, 3pts for top 3, 1pt for top 5')


# deletes previous 5 messages, only people with manage message permissions can use
@client.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount)


# outputs link to rules channel
@client.command()
async def rules(ctx):
    await ctx.send(f'{ctx.author.mention} -> Check out the {"<#694925915515256872>"} channel')


# outputs link to new channel
@client.command()
async def games(ctx):
    await ctx.send(f'{ctx.author.mention} -> Check out the {"<#693665620407091251>"} channel to see when'
                   f' the next games are starting. Also check out https://twitch.tv/wc_lavish/')


@client.command()
async def twitch(ctx):
    await ctx.send(f'{ctx.author.mention} -> Check out https://twitch.tv/wc_lavish/')


# display current stats for the duo
@client.command()
async def stats(ctx, id):
    with open('leaderboard.json', 'r') as f:
        leaderboard_data = json.load(fp = f)

        for i in range(0, len(leaderboard_data)):
            count = -1
            if (leaderboard_data[i]["id"] == id):
                await ctx.send(f'{ctx.author.mention}\nDuo: {leaderboard_data[i]["duo"]}\n'
                               f'Points: {leaderboard_data[i]["points"]}')
                break
            else:
                count = count + 1
        if (count > 0):
            await ctx.send(f'ID not found. Try again or contact <@{491600210816925706}>')


# find your duo id number
@client.command()
async def duo_id(ctx, yourDuosName):
    with open('leaderboard.json', 'r') as f:
        leaderboard_data = json.load(fp = f)
        for i in range(0, len(leaderboard_data)):
            count = -1
            str = leaderboard_data[i]["duo"]
            if (str.find(yourDuosName and ctx.author.mention)):
                await ctx.send(f'{ctx.author.mention}\nDuo: {leaderboard_data[i]["duo"]}\nID: {leaderboard_data[i]["id"]}')
                break;
            else:
                count = count + 1
            if (count > 0):
                await ctx.send(f'id not found. Try again or contact <@{491600210816925706}>')


# add points for a win
@client.command()
@has_permissions(manage_messages=True)
async def win(ctx, id):
    try:
        with open('leaderboard.json', 'r') as f:
            leaderboard_data = json.load(fp = f)

        await change_score(leaderboard_data, id, 7)

        with open('leaderboard.json', 'w') as f:
            json.dump(leaderboard_data, fp = f, indent= 4)
        await ctx.send(f'{ctx.author.mention} -> Nice win! +7 Points')
    except PermissionError():
        await ctx.send(f"You don't have permission to use that command\n"
                       f"contact <@{433423373201178646}>, <@{491600210816925706}>,"
                       f" or <@{603799184138567681}> to update your score")


# add points for a top three finish
@client.command()
@has_permissions(manage_messages=True)
async def top3(ctx, id):
    try:
        with open('leaderboard.json', 'r') as f:
            leaderboard_data = json.load(fp = f)

        await change_score(leaderboard_data, id, 3)

        with open('leaderboard.json', 'w') as f:
            json.dump(leaderboard_data, fp = f, indent= 4)
            await ctx.send(f'{ctx.author.mention} -> Top Three! +3 points')
    except PermissionError():
        await ctx.send(f"You don't have permission to use that command\n"
                       f"contact <@{433423373201178646}>, <@{491600210816925706}>,"
                       f" or <@{603799184138567681}> to update your score")
        

# add points for a top 5 finish
@client.command()
@has_permissions(manage_messages=True)
async def top5(ctx, id):
    try:
        with open('leaderboard.json', 'r') as f:
            leaderboard_data = json.load(fp = f)

        await change_score(leaderboard_data, id, 1)

        with open('leaderboard.json', 'w') as f:
            json.dump(leaderboard_data, fp = f, indent= 4)
        await ctx.send(f'{ctx.author.mention} -> Top Five! +1 point')
    except PermissionError():
        await ctx.send(f"You don't have permission to use that command\n"
                           f"contact <@{433423373201178646}>, <@{491600210816925706}>,"
                           f" or <@{603799184138567681}> to update your score")


# output the top 10 scores from the group
@client.command()
async def leaderboard(ctx):
    try:
        with open('leaderboard.json', 'r') as f:
            leaderboard_data = json.load(f)

            n = len(leaderboard_data)
            for i in range(n):
                for j in range(n-i-1):
                    if leaderboard_data[j]["points"] < leaderboard_data[j + 1]["points"]:
                        # swap the places of the duo name and points values
                        leaderboard_data[j]["points"] = leaderboard_data[j + 1]["points"]
                        leaderboard_data[j]["duo"] = leaderboard_data[j+1]["duo"]
                        # swap the places of the duo name and points values
                        leaderboard_data[j + 1]["points"] = leaderboard_data[j]["points"]
                        leaderboard_data[j+1]["duo"] = leaderboard_data[j]["duo"]
            for i in range(10):
                await ctx.send(f'{i+1}. {leaderboard_data[i]["duo"]}: {leaderboard_data[i]["points"]}')
    except LookupError():
        await ctx.send("could not retrieve leaderboard")


# Inner method handling
async def update_duos(leaderboard_data, person1, person2):
    leaderboard_data.append({
        "id": f"{random.randint(999, 9999)}",
        "duo": f"{person1} & {person2}",
        "points": 0
    })

    return leaderboard_data


# method to change the score
async def change_score(data, id, points):
    for i in range(0, len(data)):
        str = data[i]["id"]
        if str == id:
            data[i]["points"] += points
            break
        else:
            continue

    return data


async def check_duplicates(data):
    set(data)
    return data


def __hash__(self):
    return hash(('id', self.id, 'duo', self.duo))


def __eq__(self, other):
    return self.id == other.id and self.duo == other.duo


# Run the client
client.run(TOKEN)