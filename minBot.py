import discord
import json
import random
from discord.ext import commands, tasks
from operator import itemgetter

from discord.ext.commands import has_permissions

TOKEN = # Your Token
client = commands.Bot(command_prefix = '!')


@client.event
async def on_ready():
    await client.change_presence(status = discord.Status.online, activity = discord.Game('Keeping Score'))
    print('Bot online')


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Use !help <command> to see proper command usage.')
        
        
# command for commands
@client.command()
async def bot_commands(ctx):
    embed = discord.Embed(
        title='LeaderBot Commands',
        description='All the commands that the LeaderBot has to offer!',
        color=discord.Color.blue()
    )

    embed.set_footer(text='LeaderBot Commands')
    embed.set_image(url='https://st2.depositphotos.com/2964705/9030/i/950/depositphotos_90300058-stock-photo-young-little-boy-isolated-thumbs.jpg')

    embed.add_field(name="***!ping***", value="displays your ping", inline=False)
    embed.add_field(name="***!add_duo***", value="creates your duo for the leaderboard\nusage *!add_duo @name @name*", inline=False)
    embed.add_field(name="***!points***", value="displays point rules for scrims", inline=False)
    embed.add_field(name="***!rules***", value="links to scrims-rules channel", inline=False)
    embed.add_field(name="***!games***", value="links to channel with info about games and twitch stream", inline=False)
    embed.add_field(name="***!twitch***", value="links to twitch", inline=False)
    embed.add_field(name="***!stats***", value="displays current stats\nusage *!stats 9999*", inline=False)
    embed.add_field(name="***!duo_id***", value="retrieves duo ID number\nusage *!duo_id @partnerName*", inline=False)
    await ctx.channel.send(content=None, embed=embed)


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
    await ctx.send(f'{ctx.author.mention} -> Check out the {"CHANNEL NAME HERE"} channel')


# outputs link to new channel
@client.command()
async def games(ctx):
    await ctx.send(f'{ctx.author.mention} -> Check out the {"<CHANNEL NAME HERE"} channel to see when'
                   f' the next games are starting. Also check out TWITCH LINK')


@client.command()
async def twitch(ctx):
    await ctx.send(f'{ctx.author.mention} -> Check out TWITCH LINK')


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
            await ctx.send(f'ID not found. Try again or contact YOUR DISCORD ID #')


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
                await ctx.send(f'id not found. Try again or contact YOUR DISCORD ID #')


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
                       f"contact DISCORD ID, DISCORD ID,"
                       f" or DISCORD ID to update your score")


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
                       f"contact DISCORD ID, DISCORD ID,"
                       f" or DISCORD ID to update your score")
        

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
                           f"contact DISCORD ID, DISCORD ID,"
                           f" or DISCORD ID to update your score")


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
                        leaderboard_data[j]["points"], leaderboard_data[j + 1]["points"] = \
                            leaderboard_data[j + 1]["points"], leaderboard_data[j]["points"]
                        leaderboard_data[j]["duo"], leaderboard_data[j + 1]["duo"] = \
                            leaderboard_data[j + 1]["duo"], leaderboard_data[j]["duo"]
            for i in range(5):
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
