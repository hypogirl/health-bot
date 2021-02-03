import discord
from discord.ext import commands
import random
import time
import math
import asyncio
from datetime import datetime
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
        embed=discord.Embed(title="Help",description="Use ``!help [command]`` for more info on a command.\n\n**__List of commands:__\n!help** shows the list of commands and info about them.\n**!ping** not sure what this does even.\n\n__Mod commands:__\n**!kick** [mention user] [optional reason]\n**!ban** [mention user] [optional reason]\n**!warn** [mention user] [optional reason]\n**!mute** [mention user] [optional reason]\n**!unmute** [mention user] [optional reason]\n**!unban (not recommended)** [mention user] [optional reason]\n**!purge** [no. of messages]\n**!purgeuser (unstable for now)** [mention user] [no. of messages]\n**!spam** [no. of messages]",color=0xff0000)
    elif arg == "kick":
        embed=discord.Embed(title="!kick",description= "kicks member from HEALTHcord and stores information - including the reason for the kick - in the <#733746271684263936>. They might rejoin the server whenever they want.")
    elif arg == "ban":
        embed=discord.Embed(title="!ban",description= "bans member from HEALTHcord and stores information - including the reason for the ban - in the <#733746271684263936>.")
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
    if mod in ctx.author.roles and member.id != 774402228084670515:
        if ctx.author.top_role > member.top_role or ctx.author.id == 233290361877823498:
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

def modlogembed(action, reason, message, colour, user): # building the embed for the mod log channel
    modlog = bot.get_channel(733746271684263936)
    serverid = str(message.guild.id)
    channelid = str(message.channel.id)
    messageid = str(message.message.id)
    messageurl = "https://discord.com/channels/" + serverid + "/" + channelid + "/" + messageid
    if not(reason):
        reason = "No reason given by the moderator."
    embed=discord.Embed(title= action + " | #" + message.channel.name, description= "**Offender:** " + user.mention + "\n**Reason:** " + reason + "\n**Responsible moderator: **" + message.author.mention,color=colour)
    embed.add_field(name="-----", value="[Jump to incident](" + messageurl + ")", inline=False)
    return embed, modlog

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
        embed2,modlog = modlogembed("warn", reason, ctx, 0xfffcbb, user)
        await modlog.send(embed= embed2)
        try:
            await user.send(message)
        except:
            print(user.mention + " doesn't allow DMs. It's likely a bot.")
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
            await healthguild.ban(user,reason="​​​", delete_message_days=0)
        else:
            await healthguild.ban(user,reason=reason + "​​​", delete_message_days=0)
        await ctx.channel.send(embed=embed)
        embed2,modlog = modlogembed("ban", reason, ctx, 0xff0000, user)
        await modlog.send(embed = embed2)
        try:
            await user.send(message)
        except:
            print(user.mention + " doesn't allow DMs. It's likely a bot.")
    else:
        await ctx.channel.send("You cannot ban this user.")

@bot.command()
async def unban(ctx, *, arg):
    healthguild = bot.get_guild(688206199992483851)
    mod = healthguild.get_role(689280713153183795)
    user,reason,member,memberID = getvars(ctx,arg,healthguild)
    if not(member):
        await ctx.channel.send("I cannot find this user. Please unban <@!" + str(memberID) + "> manually.")
        return
    embed,message = modactions(ctx,user,reason,member,healthguild,mod,"unbanned")
    if embed == "notmod":
        return
    elif embed:
        if reason == "":
            await healthguild.unban(user,reason="​​​")
        else:
            await healthguild.unban(user,reason=reason + "​​​")
        await ctx.channel.send(embed=embed)
        embed2,modlog = modlogembed("unban", reason, ctx, 0x149414, user)
        await modlog.send(embed = embed2)
        try:
            await user.send(message)
        except:
            print(user.mention + " doesn't allow DMs. It's likely a bot.")
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
        embed2,modlog = modlogembed("kick", reason, ctx, 0xffa500, user)
        await modlog.send(embed = embed2)
        try:
            await user.send(message)
        except:
            print(user.mention + " doesn't allow DMs. It's likely a bot.")
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

    seconds = ""
    for x in range(len(reason)):
        seconds += reason[x]
        if not(reason[x].isnumeric()):
            break

    reason = reason[x+2:]
    muteaction = seconds[:-1]
    secondsint = int(seconds[:-1])

    if seconds[-1] == "s":
        if secondsint == 1:
            muteaction += " second"
        else:
            muteaction += " seconds"
    elif seconds[-1] == "m":
        if secondsint == 1:
            muteaction += " minute"
        else:
            muteaction += " minutes"
        secondsint *= 60
    elif seconds[-1] == "h":
        if secondsint == 1:
            muteaction += " hour"
        else:
            muteaction += " hours"
        secondsint *= 60 * 60
    elif seconds[-1] == "d":
        if secondsint == 1:
            muteaction += " day"
        else:
            muteaction += " days"
        secondsint *= 60 * 60 * 24
    elif seconds[-1] == "y":
        if secondsint == 1:
            muteaction += " year"
        else:
            muteaction += " years"
        secondsint *= 60 * 60 * 24 * 365

    embed,message = modactions(ctx,user,reason,member,healthguild,mod,"muted for " + muteaction)
    muted = healthguild.get_role(716467961631866922)
    if embed == "notmod":
        return
    elif embed:
        await member.add_roles(muted,reason="Muted", atomic=True)
        await ctx.channel.send(embed=embed)
        embed2,modlog = modlogembed("mute", reason, ctx, 0xfffcbb, user)
        await modlog.send(embed = embed2)
        try:
            await user.send(message)
        except:
            print(user.mention + " doesn't allow DMs. It's likely a bot.")
        await asyncio.sleep(secondsint)
        await member.remove_roles(muted, reason="Unmuted", atomic=True)
        embed2,modlog = modlogembed("unmute", "Timed unmute", ctx, 0x149414, user)
        await modlog.send(embed = embed2)
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
        embed2,modlog = modlogembed("unmute", reason, ctx, 0x149414, user)
        await modlog.send(embed = embed2)
        try:
            await user.send(message)
        except:
            print(user.mention + " doesn't allow DMs. It's likely a bot.")
    else:
        await ctx.channel.send("You cannot unmute this user.")

@bot.command()
async def spam(ctx, *, arg):
    if not(checkmod(ctx)):
        return
    for x in range(int(arg)):
        await ctx.channel.send("spam")

@bot.command()
async def purge(ctx, *, arg):
    if not(checkmod(ctx)):
        return
    deleted = await ctx.channel.purge(limit= int(arg))
    await ctx.channel.purge(limit= 1)
    deletedstr = ""
    users = []
    visited = []
    for message in deleted:
        if message.author not in visited:
            users.append((message.author,1))
            visited.append(message.author)
        else:
            i = visited.index(message.author)
            users[i] = (message.author,users[i][1] + 1)

    users.sort(reverse=True, key=lambda x:x[1])

    for x in users:
        deletedstr += "**" + x[0].name + "#" + x[0].discriminator + ":** " + str(x[1]) + "\n"

    modlog = bot.get_channel(733746271684263936)
    embed = discord.Embed(title=" ", description="Messages deleted:\n\n" + deletedstr, color=0xff0000)
    embed.set_author(name= str(len(deleted)) + " messages purged | #" + ctx.channel.name)
    await modlog.send(embed= embed)


userID = False
def checkid(m):
    global userID
    return m.author.id == userID

@bot.command()
async def purgeuser(ctx, *, arg):
    global userID
    if not(checkmod(ctx)):
        return

    userID = ""
    for x in range(len(arg)):
        if arg[x].isnumeric():
            userID += arg[x]
        if arg[x] == ">" or arg[x] == " ":
            break

    userID = int(userID)
    limit = int(arg[x+1:])
    initlimit = limit
    i = 0
    while limit:   
        deleted = await ctx.channel.purge(limit= limit, check= checkid)
        await ctx.channel.send(i)
        i+=1
        limit = limit - len(deleted)

    await ctx.channel.purge(limit= 1)
    
    userstr = "**" + bot.get_user(userID).name + "#" + bot.get_user(userID).discriminator + ":** " + str(initlimit)
    modlog = bot.get_channel(733746271684263936)
    embed = discord.Embed(title=" ", description="User" + userstr + "/" + bot.get_user(userID).mention, color=0xff0000)
    embed.set_author(name= str(initlimit) + " specific user's messages deleted | #" + ctx.channel.name)
    await modlog.send(embed= embed)



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



## temporary commands (prob) ##
@bot.command()
async def riff(ctx):
    embed=discord.Embed(title=" ", description="https://open.spotify.com/playlist/4rjHTKoc6UW6vZ3OtsRskC?si=OusEsIvdQPaHLnY2ae1bjw \n\nhttps://music.apple.com/us/playlist/tricils-riff-of-the-week/pl.u-GgAxqabhZxeVBG", color=0xff0000)
    embed.set_author(name="TRICIL'S RIFF OF THE WEEK PLAYLISTS! UPDATED EVERY WEDNESDAY!")
    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/732593127352696942.png")
    await ctx.channel.send(embed=embed)



def album(m):
    albuml = []
    m = "".join(m.lower().split()) #remove spaces, all lowercase, makes it easier for search

    health = (["heaven", "girlattorney", "triceratops", "crimewave", "courtship", "zoothorns", "tabloidsores", "glitterpills", "perfectskin", "losttime","//m\\\\"],755047461734580306)
    getcolor = (["getcolor", "inheat","dieslow","nicegirls","death+","beforetigers","severin","eatflesh","wearewater","inviolet"],755047462640681030)
    deathmagic = (["deathmagic","victim","stonefist","mentoday","fleshworld","courtshipii","darkenough","salvia","newcoke","lalooks","l.a.looks","hurtyourself","drugsexist"],755047460019372062)
    vol4 = (["vol4","vol.4","psychonaut","feelnothing","godbotherer","blackstatic","lossdeluxe","nc-17","nc17","themessage","ratwars","strangedays","wrongbag","slavesoffear","decimation"],755047461944557618)
    disco4 = (["disco4","cyberpunk2020","cyberpunk2.0.0.0","cyberpunk2.0.0.0.","body/prison","bodyprison","powerfantasy","judgmentnight","innocence","fullofhealth","colors","hateyou","dflooks","d.f.looks","massgrave","deliciousape","hardtobeagod"],755050227215630426)
    disco3 = (["disco3","euphoria","slumlord","crusher"],755050414008696852)
    disco2 = (["disco2","usaboys","u.s.a.boys"],755050225751556117)
    mp3 = (["tears"],755047462896533605)
    
    albums = [health,getcolor,deathmagic,vol4,disco2,disco3,disco4,mp3]

    for x in albums:
        for y in x[0]:
            if y in m:
                albuml.append(x[1])
                break

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
        try:
            await bot.process_commands(message)
        except:
            print(message.content + " is an invalid command.")
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

        if "pain" in "".join(message.content.lower().split()):
            max = bot.get_emoji(697638034937479239)
            await message.add_reaction(max)

    if message.content == "health joao qwerty":
        logs = await bot.get_guild(688206199992483851).audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten()
        logs = logs[0]
        await message.channel.send(logs)
    

## MISC EVENTS ##

@bot.event
async def on_message_edit(before,after):
    if before.channel.id == 733412404351991846: # curated channel, it prevents the channel to be spammed with cacostar counter updates
        return
    if before.content != after.content:
        userstr = before.author.name + "#" + before.author.discriminator
        avatarurl = "https://cdn.discordapp.com/avatars/" + str(before.author.id) + "/" + before.author.avatar + ".webp"
        embed=discord.Embed(title="Message edited in #" + before.channel.name, description= "**Before:** " + before.content + "\n**After:** " + after.content,color=0x45b6fe)
        embed.set_author(name=userstr, icon_url=avatarurl)
        await bot.get_channel(735169441729478717).send(embed= embed)

@bot.event
async def on_message_delete(message):
    if message.author.id == 372175794895585280: #its the haikubot ID, its kinda useless showing when these are deleted
        return
    userstr = message.author.name + "#" + message.author.discriminator
    avatarurl = "https://cdn.discordapp.com/avatars/" + str(message.author.id) + "/" + message.author.avatar + ".webp"
    if message.content:
        description = message.content
    else:
        description = "*[This message only contained attachements.]*"
    embed=discord.Embed(title="Message deleted in #" + message.channel.name, description= description,color=0xff0000)
    embed.set_author(name=userstr, icon_url=avatarurl)
    await bot.get_channel(735169441729478717).send(embed= embed)

@bot.event
async def on_member_ban(healthcord,user):
    logs = await healthcord.audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten()
    logs = logs[0]
    if "​​​" in logs.reason:
        return
    modlog = bot.get_channel(733746271684263936)
    embed=discord.Embed(title= "manual ban", description= "**Offender:** " + user.mention + " / " + user.mention + "\n**Reason:** " + logs.reason + "\n**Responsible moderator: **" + logs.user.mention,color= 0xff0000)
    await modlog.send(embed= embed)

@bot.event
async def on_member_unban(healthcord,user):
    logs = await healthcord.audit_logs(limit=1, action=discord.AuditLogAction.unban).flatten()
    logs = logs[0]
    if "​​​" in logs.reason:
        return
    modlog = bot.get_channel(733746271684263936)
    embed = discord.Embed(title= "manual unban", description= "**Offender:** " + user.mention + "\n**Responsible moderator: **" + logs.user.mention,color= 0xff0000)
    await modlog.send(embed= embed)

@bot.event
async def on_member_remove(member):
    modlog = bot.get_channel(733746271684263936)
    memberstr = member.name + "#" + member.discriminator
    timeonserver = datetime.now() - member.joined_at
    timestr = " joined "
    if timeonserver.days:
        if timeonserver.days >= 365:
            if timeonserver.days / 365 < 2:
                timestrAux = "1 year, " + str(timeonserver.days % 365) + " days, "
                timestr += timestrAux
            else:
                timestrAux = str(math.floor(timeonserver.days/365)) + " years, " + str(timeonserver.days % 365) + " days, "
                timestr += timestrAux
        else:
            if timeonserver.days == 1:
                timestr += "1 day, "
            else:
                timestrAux = str(timeonserver.days) + " days, "
                timestr += timestrAux
    if timeonserver.seconds:
        if timeonserver.seconds / 60 >= 60:
            if timeonserver.seconds / 3600 < 2:
                rest = timeonserver.seconds % 3600
                minutes = math.floor(rest / 60)
                seconds = rest % 60
                timestrAux = "1 hour, "
                if minutes:
                    if minutes == 1:
                        timestrAux += "1 minute, "
                    else:
                        timestrAuxAux = str(minutes) + " minutes, "
                        timestrAux += timestrAuxAux
                if seconds:
                    if seconds == 1:
                        timestrAux += "1 second, "
                    else:
                        timestrAuxAux = str(seconds) + " seconds"
                        timestrAux += timestrAuxAux
                timestr += timestrAux
            else:
                rest = timeonserver.seconds % 3600
                minutes = math.floor(rest / 60)
                seconds = rest % 60
                timestrAux = str(math.floor(timeonserver.seconds / 3600)) + " hours, "
                if minutes:
                    if minutes == 1:
                        timestrAux += "1 minute, "
                    else:
                        timestrAuxAux = str(minutes) + " minutes, "
                        timestrAux += timestrAuxAux
                if seconds:
                    if seconds == 1:
                        timestrAux += "1 second, "
                    else:
                        timestrAuxAux = str(seconds) + " seconds"
                        timestrAux += timestrAuxAux
                timestr += timestrAux
        else:
            minutes = math.floor(timeonserver.seconds / 60)
            seconds = timeonserver.seconds % 60
            timestrAux = ""
            if minutes:
                if minutes == 1:
                    timestrAux += "1 minute, "
                else:
                    timestrAuxAux = str(minutes) + " minutes, "
                    timestrAux += timestrAuxAux
            if seconds:
                if seconds == 1:
                    timestrAux += "1 second, "
                else:
                    timestrAuxAux = str(seconds) + " seconds"
                    timestrAux += timestrAuxAux
            timestr += timestrAux

    if timestr[-2:] == ", ":
        timestr = timestr[:-2] + " ago."
    else:
        timestr += " ago."
                
    rolestr = ""
    for role in member.roles[1:]:
        rolestr += role.mention + ", "

    if rolestr[-2:] == ", ":
        rolestr = rolestr[:-2]

    if member.avatar:
        avatarurl = "https://cdn.discordapp.com/avatars/" + str(member.id) + "/" + member.avatar + ".webp"
    else:
        avatarurl = "https://cdn.discordapp.com/avatars/774402228084670515/5ef539d5f3e8d576c4854768727bc75a.png"
    
    embed = discord.Embed(title = "Member left", description = member.mention + timestr + "\n**Roles:** " + rolestr, color=0xff0000)
    embed.set_author(name=memberstr, icon_url=avatarurl)
    await modlog.send(embed= embed)
    


bot.run(bottoken.token)