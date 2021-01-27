import discord
from discord.ext import commands
import random
import time
import bottoken
import mysql.connector
import dbconnect

healthbot = mysql.connector.connect(
  host=dbconnect.h,
  user=dbconnect.u,
  password=dbconnect.p,
  database="healthbot"
)

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='!', intents=intents)
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
        embed=discord.Embed(title="Help",description="Use ``cacohelp [command]`` for more info on a command.\n\n**__List of commands:__\ncacohelp** shows the list of commands and info about them.\n**cacoping** not sure what this does even.\n\n__Mod commands:__\n**cacokick** [mention user] [optional reason]\n**cacoban** [mention user] [optional reason]\n**cacowarn** [mention user] [optional reason]\n**cacomute** [mention user] [optional reason]\n**cacounmute** [mention user] [optional reason]\n",color=0xff0000)
    else:
        await ctx.author.send(arg + " is not a valid command.")
        return
    await ctx.author.send(embed=embed)
    if ctx.author.dm_channel != ctx.channel:
        await ctx.channel.send(ctx.author.mention + ", I've sent you a DM with the help menu.")


def checkdb(t):
    mycursor = healthbot.cursor()
    mycursor.execute("SELECT name,content,embed FROM `Trigger`")
    myresult = mycursor.fetchall()
    possible = []
    trigger = False
    flag = False
    for x,y,z in myresult:
        print(x + " " + t)
        if x == t:
            if z == 0:
                possible.append(y)
            else:
                possible.append(y)
                flag = True
    if possible:
        trigger = random.choice(possible)
    return trigger,flag

def convertembed(t):
    return

'''
MOD COMMANDS
'''

def checkmod(ctx):
    healthguild = bot.get_guild(688206199992483851)
    mod = healthguild.get_role(689280713153183795)
    return mod in ctx.author.roles

def getvars(ctx,arg,healthguild): # gets the user,reason and member for the mod functions
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
    
    return user,reason,member,userID

def modactions(ctx,user,reason,member,healthguild,mod,action): # writes the embed and dm for the mod functions
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
    user,reason,member,memberID = getvars(ctx,arg,healthguild)
    if not(member):
        await ctx.channel.send("<@!" + str(memberID) + "> is not a member of HEALTHcord.")
        return
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
    user,reason,member,memberID = getvars(ctx,arg,healthguild)
    if not(member):
        await ctx.channel.send("<@!" + str(memberID) + "> is not a member of HEALTHcord.")
        return
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
    user,reason,member,memberID = getvars(ctx,arg,healthguild)
    if not(member):
        await ctx.channel.send("<@!" + str(memberID) + "> is not a member of HEALTHcord.")
        return
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
    user,reason,member,memberID = getvars(ctx,arg,healthguild)
    if not(member):
        await ctx.channel.send("<@!" + str(memberID) + "> is not a member of HEALTHcord.")
        return

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
    user,reason,member,memberID = getvars(ctx,arg,healthguild)
    if not(member):
        await ctx.channel.send("<@!" + str(memberID) + "> is not a member of HEALTHcord.")
        return
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

@bot.command()
async def createtrigger(ctx, arg1, arg2):
    if checkmod(ctx):
        sql = "INSERT INTO `Trigger` (name, content,embed) VALUES (%s, %s, 0)"
        val = (arg1, arg2)
        mycursor = healthbot.cursor()
        mycursor.execute(sql, val)
        healthbot.commit()
        await ctx.channel.send("Trigger created successfully.")

@bot.command()
async def deletetrigger(ctx, arg):
    if checkmod(ctx):
        mycursor = healthbot.cursor()
        sql = "DELETE FROM `Trigger` WHERE name = '" + arg + "'"
        mycursor.execute(sql)
        healthbot.commit()
        await ctx.channel.send("Trigger deleted successfully.")


'''
temporary commands (prob)
'''
@bot.command()
async def riff(ctx):
    embed=discord.Embed(title=" ", description="https://open.spotify.com/playlist/4rjHTKoc6UW6vZ3OtsRskC?si=OusEsIvdQPaHLnY2ae1bjw \n\nhttps://music.apple.com/us/playlist/tricils-riff-of-the-week/pl.u-GgAxqabhZxeVBG", color=0xff0000)
    embed.set_author(name="TRICIL'S RIFF OF THE WEEK PLAYLISTS! UPDATED EVERY WEDNESDAY!")
    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/732593127352696942.png")
    await ctx.channel.send(embed=embed)



def album(m):
    albuml = []
    m = "".join(m.lower().split()) #remove spaces, all lowercase, makes it easier for search

    health = ["girlattorney", "triceratops", "crimewave", "courtship", "zoothorns", "tabloidsores", "glitterpills", "perfectskin", "losttime"]
    getcolor = ["getcolor", "inheat","dieslow","nicegirls","death+","beforetigers","severin","eatflesh","wearewater","inviolet"]
    deathmagic = ["deathmagic","victim","stonefist","mentoday","fleshworld","courtshipii","darkenough","salvia","newcoke","lalooks","l.a.looks","hurtyourself","drugsexist"]
    vol4 = ["vol4","psychonaut","feelnothing","godbotherer","blackstatic","lossdeluxe","nc-17","nc17","the message","ratwars","strangedays","wrongbag","slavesoffear","decimation"]
    disco4 = ["disco4","cyberpunk2020","cyberpunk2.0.0.0","cyberpunk2.0.0.0.","body/prison","bodyprison","powerfantasy","judgmentnight","innocence","fullofhealth","colors","hateyou","dflooks","d.f.looks","massgrave","deliciousape","hardtobeagod"]

    for x in health:
        if x in m:
            albuml.append(755047461734580306)
            break
    for x in getcolor:
        if x in m:
            albuml.append(755047462640681030)
            break
    for x in deathmagic:
        if x in m:
            albuml.append(755047460019372062)
            break
    for x in vol4:
        if x in m:
            albuml.append(755047461944557618)
            break
    for x in disco4:
        if x in m:
            albuml.append(755050227215630426)

    return albuml    



@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
  
    if message.content.startswith("!"): #recognising a command
        #trigger,e = checkdb(message.content[1:])
        #if trigger:
        #    if e:
        #        embed = convertembed(trigger)
        #        await message.channel.send(embed=embed)
        #    else:
        #        await message.channel.send(trigger)
        #    return
        await bot.process_commands(message)
        return

    if message.author.id == 225522547154747392: #replacing the stock bot messages with HEALTH BOT messages
        embedc=discord.Embed(title= "STOCKS", description= message.embeds[0].description, color=0xff0000)
        embedc.set_footer(text= message.embeds[0].footer.text)
        await message.channel.send(embed= embedc)
        await message.delete()

    if message.content.lower() in ["musik make love to <@774402228084670515>","musik make love to health bot","musik make love to health :: bot"]:
        time.sleep(1)
        o = ["Oh no... not me.","Why would anyone want this","What is wrong with you?","No no no no no no"]
        await message.channel.send(random.choice(o))
    
    if message.channel.id != 707011962898481254: #we dont want this on #on-the-real certainly
        emojialbum = album(message.content) #finding if there is a mention to a HEALTH album in a message and reacting with the album cover
        if emojialbum:
            for x in emojialbum:
                emoji = bot.get_emoji(x)
                await message.add_reaction(emoji)

    
    



bot.run(bottoken.token)