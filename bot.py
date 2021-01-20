import discord
from discord.ext import commands
import random
import time
import bottoken

#client = discord.Client()

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='caco', intents=intents)
bot.remove_command('help') #removing the default help command

@bot.event
async def on_ready():
    print('HEALTHbot is online')

@bot.command()
async def ping(ctx):
    await ctx.send("<@" + str(ctx.author.id) + ">, pong!")

#HELP COMMAND
@bot.command()
async def help(ctx, *arg):
    arg = ' '.join(arg)
    if arg == "help" or arg == "":
        embed=discord.Embed(title="Help",description="Use ``cacohelp [command]`` for more info on a command.\n\n**__List of commands:__\ncacohelp** shows the list of commands and info about them.",color=0xff0000)
    else:
        await ctx.author.send(arg + " is not a valid command.")
        return
    await ctx.author.send(embed=embed)
    if ctx.author.dm_channel != ctx.channel:
        await ctx.channel.send(ctx.author.mention + ", I've sent you a DM with the help menu.")

'''
MOD COMMANDS
'''
def getvars(ctx,arg,healthguild):
    userID = ""

    for x in range(len(arg)):
        if arg[x].isnumeric():
            userID += arg[x]
        if arg[x] == ">":
            break

    reason = arg[x+2:]
    userID = int(userID)
    user = bot.get_user(userID)
    member = healthguild.get_member(userID)
    
    return user,reason,member

def modactions(ctx,user,reason,member,healthguild,mod,action):
    if mod in ctx.author.roles:
        if ctx.author.top_role > member.top_role:
            if user.avatar:
                avatarurl = "https://cdn.discordapp.com/avatars/" + str(user.id) + "/" + user.avatar + ".webp"
            else:
                avatarurl = "https://cdn.discordapp.com/avatars/774402228084670515/5ef539d5f3e8d576c4854768727bc75a.png"
            userstr = user.name + "#" + user.discriminator
            embed = False
            message = False
            if reason == "":
                embed=discord.Embed(title=" ", color=0xff0000)
                embed.set_author(name=userstr+" has been "+action+".", icon_url=avatarurl)
                message = "**You have been "+action+" by a moderator in HEALTHcord.**"
            else:
                embed=discord.Embed(title=" ", description="**Reason:** "+reason, color=0xff0000)
                embed.set_author(name=userstr+" has been "+action+".", icon_url=avatarurl)
                message = "**You have been "+action+" by a moderator in HEALTHcord.\nReason:** " + reason
            return embed,message
        return False, False
    else:
        return "notmod",False

@bot.command()
async def warn(ctx, *, arg):
    healthguild = bot.get_guild(688206199992483851)
    mod = healthguild.get_role(689280713153183795)
    user,reason,member = getvars(ctx,arg,healthguild)
    embed,message = modactions(ctx,user,reason,member,healthguild,mod,"warned")
    if embed == "notmod":
        return
    elif embed:
        await ctx.channel.send(embed=embed)
        await user.send(message)
    else:
        await ctx.channel.send("You cannot warn this user.")

@bot.command()
async def ban(ctx, *, arg):
    healthguild = bot.get_guild(688206199992483851)
    mod = healthguild.get_role(689280713153183795)
    user,reason,member = getvars(ctx,arg,healthguild)
    embed,message = modactions(ctx,user,reason,member,healthguild,mod,"banned")
    if embed == "notmod":
        return
    elif embed:
        if reason =="":
            await healthguild.ban(user,reason=None, delete_message_days=0)
        else:
            await healthguild.ban(user,reason=reason, delete_message_days=0)
        await ctx.channel.send(embed=embed)
        await user.send(message)
    else:
        await ctx.channel.send("You cannot ban this user.")

@bot.command()
async def kick(ctx, *, arg):
    healthguild = bot.get_guild(688206199992483851)
    mod = healthguild.get_role(689280713153183795)
    user,reason,member = getvars(ctx,arg,healthguild)
    embed,message = modactions(ctx,user,reason,member,healthguild,mod,"kicked")
    if embed == "notmod":
        return
    elif embed:
        await member.kick()
        await ctx.channel.send(embed=embed)
        await user.send(message)
    else:
        await ctx.channel.send("You cannot kick this user.")

@bot.command()
async def mute(ctx, *, arg):
    healthguild = bot.get_guild(688206199992483851)
    mod = healthguild.get_role(689280713153183795)
    user,reason,member = getvars(ctx,arg,healthguild)

    '''seconds = ""
    for x in range(len(reason)):
        seconds += reason[x]
        if not(reason[x].isnumeric()):
            break
    reason = reason[x+2:]

    if seconds[-1] == "s":
        seconds = int(seconds[:-1])
    elif seconds[-1] == "m":
        seconds = int(seconds[:-1]) * 60
    elif seconds[-1] == "h":
        seconds = int(seconds[:-1]) * 60 * 60
    elif seconds[-1] == "d":
        seconds = int(seconds[:-1]) * 60 * 60 * 24
    elif seconds[-1] == "y":
        seconds = int(seconds[:-1]) * 60 * 60 * 24 * 365'''

    embed,message = modactions(ctx,user,reason,member,healthguild,mod,"muted indefinitely")
    muted = healthguild.get_role(716467961631866922)
    if embed == "notmod":
        return
    elif embed:
        await member.add_roles(muted,reason="Muted", atomic=True)
        await ctx.channel.send(embed=embed)
        await user.send(message)
        #time.sleep(seconds)
        #await member.remove_roles(muted, reason="Unmuted", atomic=True)
    else:
        await ctx.channel.send("You cannot mute this user.")

@bot.command()
async def unmute(ctx, *, arg):
    healthguild = bot.get_guild(688206199992483851)
    mod = healthguild.get_role(689280713153183795)
    user,reason,member = getvars(ctx,arg,healthguild)
    embed,message = modactions(ctx,user,reason,member,healthguild,mod,"unmuted")
    muted = healthguild.get_role(716467961631866922)
    if embed == "notmod":
        return
    elif embed:
        await member.remove_roles(muted, reason="Unmuted", atomic=True)
        await ctx.channel.send(embed=embed)
        await user.send(message)
    else:
        await ctx.channel.send("You cannot unmute this user.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith("!"): #recognising a Ryan command
        message.content = "caco" + message.content[1:]
    
    if message.content.startswith("caco"): #recognising a command
        await bot.process_commands(message)
        return

    if message.content.lower() in ["musik make love to <@774402228084670515>","musik make love to health bot","musik make love to health :: bot"]:
        time.sleep(1)
        o = ["Oh no... not me.","Why would anyone want this","What is wrong with you?","No no no no no no"]
        await message.channel.send(random.choice(o))
    



bot.run(bottoken.token)