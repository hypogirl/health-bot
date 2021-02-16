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
import auxfunctions as aux

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
    if arg == "help" or not(arg):
        helpstr = "Use ``!help [command]`` for more info on a command.\n\n**__List of commands:__\n!help** shows the list of commands and info about them.\n**!ping** not sure what this does even."
        helpstr += "\n\n\n__User commands:__\n**!timeout** [amount of time]"
        helpstr += "\n\n\n__Mod commands:__\n**!kick** [mention user] [optional reason]\n**!ban** [mention user] [optional reason]\n**!warn** [mention user] [optional reason]\n**!mute** [mention user] [optional reason]\n**!unmute** [mention user] [optional reason]\n**!unban (not recommended)** [mention user] [optional reason]"
        helpstr += "\n\n**!purge** [no. of messages]\n**!purgeuser (unstable for now)** [mention user] [no. of messages]\n**!spam** [no. of messages]\n**!motd** [mention user]\n\n**!createtrigger (inactive)** [name] [content]\n**!deletetrigger (inactive)** [name]"
        embed=discord.Embed(title="Help",description=helpstr,color=0xff0000)
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

## MOD COMMANDS ##

@bot.command()
async def warn(ctx, *, arg):
    healthguild = bot.get_guild(688206199992483851)
    mod = healthguild.get_role(689280713153183795)
    user,reason,member,memberID = aux.getvars(bot,ctx,arg,healthguild)
    if not(member):
        await ctx.channel.send("<@!" + str(memberID) + "> is not a member of HEALTHcord.")
        return
    embed,message = aux.modactions(ctx,user,reason,member,healthguild,mod,"warned")
    if embed == "notmod":
        return
    elif embed:
        await ctx.channel.send(embed=embed)
        embed2,modlog = aux.modlogembed(bot,"warn", reason, ctx, 0xfffcbb, user)
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
    user,reason,member,memberID = aux.getvars(bot,ctx,arg,healthguild)
    if not(member):
        await ctx.channel.send("<@!" + str(memberID) + "> is not a member of HEALTHcord.")
        return
    embed,message = aux.modactions(ctx,user,reason,member,healthguild,mod,"banned")
    if embed == "notmod":
        return
    elif embed:
        if reason =="":
            await healthguild.ban(user,reason="​​​", delete_message_days=0)
        else:
            await healthguild.ban(user,reason=reason + "​​​", delete_message_days=0)
        await ctx.channel.send(embed=embed)
        embed2,modlog = aux.modlogembed(bot,"ban", reason, ctx, 0xff0000, user)
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
    user,reason,member,memberID = aux.getvars(bot,ctx,arg,healthguild)
    if not(member):
        await ctx.channel.send("I cannot find this user. Please unban <@!" + str(memberID) + "> manually.")
        return
    embed,message = aux.modactions(ctx,user,reason,member,healthguild,mod,"unbanned")
    if embed == "notmod":
        return
    elif embed:
        if reason == "":
            await healthguild.unban(user,reason="​​​")
        else:
            await healthguild.unban(user,reason=reason + "​​​")
        await ctx.channel.send(embed=embed)
        embed2,modlog = aux.modlogembed(bot,"unban", reason, ctx, 0x149414, user)
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
    user,reason,member,memberID = aux.getvars(bot,ctx,arg,healthguild)
    if not(member):
        await ctx.channel.send("<@!" + str(memberID) + "> is not a member of HEALTHcord.")
        return
    embed,message = aux.modactions(ctx,user,reason,member,healthguild,mod,"kicked")
    if embed == "notmod":
        return
    elif embed:
        await member.kick()
        await ctx.channel.send(embed=embed)
        embed2,modlog = aux.modlogembed(bot,"kick", reason, ctx, 0xffa500, user)
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
    user,reason,member,memberID = aux.getvars(bot,ctx,arg,healthguild)

    if not(member):
        await ctx.channel.send("<@!" + str(memberID) + "> is not a member of HEALTHcord.")
        return

    seconds = ""
    x = 0
    for x in range(len(reason)):
        seconds += reason[x]
        if not(reason[x].isnumeric()):
            break

    suffix = seconds[:-1]
    if suffix:
        reason = reason[x+2:]
        secondsint = int(seconds[:-1])
        timestr,secondsint = aux.timestrbuilder(seconds,secondsint,suffix)
        embed,message = aux.modactions(ctx,user,reason,member,healthguild,mod,"muted for " + timestr)
    else:
        embed,message = aux.modactions(ctx,user,reason,member,healthguild,mod,"muted")
    muted = healthguild.get_role(716467961631866922)
    if embed == "notmod":
        return
    elif embed:
        await member.add_roles(muted,reason="Muted", atomic=True)
        await ctx.channel.send(embed=embed)
        embed2,modlog = aux.modlogembed(bot,"mute", reason, ctx, 0xfffcbb, user)
        await modlog.send(embed = embed2)
        try:
            await user.send(message)
        except:
            print(user.mention + " doesn't allow DMs. It's likely a bot.")
        if timestr:
            await asyncio.sleep(secondsint)
            await member.remove_roles(muted, reason="Unmuted", atomic=True)
            embed2,modlog = aux.modlogembed(bot,"unmute", "Timed unmute", ctx, 0x149414, user)
            await modlog.send(embed = embed2)
    else:
        await ctx.channel.send("You cannot mute this user.")

@bot.command()
async def unmute(ctx, *, arg):
    healthguild = bot.get_guild(688206199992483851)
    mod = healthguild.get_role(689280713153183795)
    user,reason,member,memberID = aux.getvars(bot,ctx,arg,healthguild)
    if not(member):
        await ctx.channel.send("<@!" + str(memberID) + "> is not a member of HEALTHcord.")
        return
    embed,message = aux.modactions(ctx,user,reason,member,healthguild,mod,"unmuted")
    muted = healthguild.get_role(716467961631866922)
    if embed == "notmod":
        return
    elif embed:
        await member.remove_roles(muted, reason="Unmuted", atomic=True)
        await ctx.channel.send(embed=embed)
        embed2,modlog = aux.modlogembed(bot,"unmute", reason, ctx, 0x149414, user)
        await modlog.send(embed = embed2)
        try:
            await user.send(message)
        except:
            print(user.mention + " doesn't allow DMs. It's likely a bot.")
    else:
        await ctx.channel.send("You cannot unmute this user.")

@bot.command()
async def spam(ctx, *, arg):
    if not(aux.checkmod(bot,ctx)):
        return
    for x in range(int(arg)):
        await ctx.channel.send("spam")

@bot.command()
async def purge(ctx, *, arg):
    if not(aux.checkmod(bot,ctx)):
        return
    await ctx.message.delete()
    deleted = await ctx.channel.purge(limit= int(arg))
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

@bot.command()
async def motd(ctx, *, arg):    # setting someone as the member of the day
    if not(aux.checkmod(bot,ctx)):
        return
    healthguild = bot.get_guild(688206199992483851)
    role = healthguild.get_role(753720334993326161)
    userID = ""

    for x in range(len(arg)):
        if arg[x].isnumeric():
            userID += arg[x]
        if arg[x] == ">":
            break

    userID = int(userID)
    member = healthguild.get_member(userID)
    emojis = [697621015337107466,737315507509657661,697879872391086113,697880868743544903,753291933950017627,753291934008606762,804113756622684220,709794793051390153]
    emoji = bot.get_emoji(random.choice(emojis))
    await member.add_roles(role,reason="Member of the day", atomic=True)
    message = await ctx.channel.send(member.mention + " is member of the day!")
    await message.add_reaction(emoji)
    await asyncio.sleep(86400)
    await member.remove_roles(role,reason="End of the member of the day", atomic=True)


@bot.command()
async def createtrigger(ctx, *, arg):
    if aux.checkmod(bot,ctx):
        '''sql = "INSERT INTO `Trigger` (name, content,embed) VALUES (%s, %s, 0)"
        val = (arg1, arg2)
        mycursor = healthbot.cursor()
        mycursor.execute(sql, val)
        healthbot.commit()
        await ctx.channel.send("Trigger created successfully.")'''
        left = False
        for x in range(len(arg)):
            if arg[x] == " ":
                left = arg[:x]
                right = arg[x+1:]
                break
        if not(left):
            await ctx.channel.send("Invalid trigger.")

@bot.command()
async def deletetrigger(ctx, *, arg):
    if aux.checkmod(bot,ctx):
        '''mycursor = healthbot.cursor()
        sql = "DELETE FROM `Trigger` WHERE name = '" + arg + "'"
        mycursor.execute(sql)
        healthbot.commit()
        await ctx.channel.send("Trigger deleted successfully.")'''
        # temporary solution #

@bot.command()
async def timeout(ctx, *, arg):
    seconds = arg
    suffix = seconds[:-1]
    secondsint = int(seconds[:-1])
    healthguild = bot.get_guild(688206199992483851)
    muted = healthguild.get_role(716467961631866922)
    timestr,secondsint = aux.timestrbuilder(seconds,secondsint,suffix)
    embed=discord.Embed(title=" ", color=0xff0000)
    embed.set_author(name="Enjoy your timeout. (" + timestr + ")")
    await ctx.author.add_roles(muted,reason="Self-requested timeout", atomic=True)
    await ctx.channel.send(embed=embed)
    await asyncio.sleep(secondsint)
    await ctx.author.remove_roles(muted, reason="Timout ended", atomic=True)
    await ctx.author.send("Your timeout in HEALTHcord has ended.")


## temporary commands (prob) ##
@bot.command()
async def riff(ctx):
    embed=discord.Embed(title=" ", description="https://open.spotify.com/playlist/4rjHTKoc6UW6vZ3OtsRskC?si=OusEsIvdQPaHLnY2ae1bjw \n\nhttps://music.apple.com/us/playlist/tricils-riff-of-the-week/pl.u-GgAxqabhZxeVBG", color=0xff0000)
    embed.set_author(name="TRICIL'S RIFF OF THE WEEK PLAYLISTS! UPDATED EVERY WEDNESDAY!")
    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/732593127352696942.png")
    await ctx.channel.send(embed=embed)



def album(m,mentions):
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
    payne = (["pain", "<:max:697638034937479239>"],697638034937479239)
    powercaco = (["powerfantasy"],766716666540326932)
    ping = (["774402228084670515"],788902728658452481)

    cacoheart = ([("good","love","based","thank","great","amazing","well"),("bad","racist","racism","cringe","dumb","idiot","stupid","bug","n'twork","notwork","suck","shit","poo","bitch")],804113756622684220,[697627002202750976,708429172737048606,735209358379450471,736196814654668830,"notfunny"])

    
    albums = [health,getcolor,deathmagic,vol4,disco2,disco3,disco4,mp3,payne,powercaco]

    for x in albums:
        for y in x[0]:
            if y in m:
                albuml.append(x[1])
                break

    if "bot" in m:
        flag = True
        for x in cacoheart[0][0]:
            if x in m:
                albuml.append(cacoheart[1])
                flag = False
                break
        if flag:
            for x in cacoheart[0][1]:
                if x in m:
                    emojiID = random.choice(cacoheart[2])
                    if emojiID == "notfunny":
                        albuml.append(733376041816424489)
                        albuml.append(733376041686532127)
                        break
                    else:
                        albuml.append(emojiID)
                        break

    for x in mentions:
        if x.id == 774402228084670515:
            albuml.append(788902728658452481)
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
        if message.content.startswith("!<:dovide:734404973466484816>"):
            message.content = "!timeout" + message.content[29:]
        try:
            await bot.process_commands(message)
        except:
            print(message.content + " is an invalid command.")
        return

    if message.author.id == 225522547154747392: #replacing the stock bot messages with HEALTH BOT messages
        embedc=discord.Embed(title= "STOCKS", description= message.embeds[0].description, color=0xff0000)
        embedc.set_footer(text= message.embeds[0].footer.text)
        embedc.add_field(name="​", value="[Command Help](https://stockbot.us/c/?m=1&g=1#statistics)", inline=False)
        await message.channel.send(embed= embedc)
        await message.delete()

    if message.content.lower() in ["musik make love to <@774402228084670515>","musik make love to health bot","musik make love to health :: bot"]:
        time.sleep(1)
        o = ["Oh no... not me.","Why would anyone want this","What is wrong with you?","No no no no no no"]
        await message.channel.send(random.choice(o))

    
    if message.channel.id != 707011962898481254: #we dont want this on #on-the-real certainly
        emojialbum = album(message.content,message.mentions) #finding if there is a mention to a HEALTH album in a message and reacting with the album cover
        if emojialbum:
            for x in emojialbum:
                emoji = bot.get_emoji(x)
                await message.add_reaction(emoji)

    #if message.content == "health joao qwerty":
    #    await message.channel.send("nothing to test")
    

## MISC EVENTS ##

@bot.event
async def on_message_edit(before,after):
    if before.channel.id in [733412404351991846,791453462063742987]: # curated channels, it prevents the channel to be spammed with cacostar counter updates
        return
    if before.content != after.content:
        userstr = before.author.name + "#" + before.author.discriminator
        avatarurl = "https://cdn.discordapp.com/avatars/" + str(before.author.id) + "/" + before.author.avatar + ".webp"
        embed=discord.Embed(title="Message edited in #" + before.channel.name, description= "**Before:** " + before.content + "\n**After:** " + after.content,color=0x45b6fe)
        embed.set_author(name=userstr, icon_url=avatarurl)
        await bot.get_channel(735169441729478717).send(embed= embed)

@bot.event
async def on_message_delete(message):
    if message.author.id in [372175794895585280,225522547154747392]: #its the haikubot and stock bot's ID, its kinda useless showing when these are deleted
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
    if not(logs.reason):
        logs.reason = "No reason was specified."
    if "​​​" in logs.reason:
        return
    modlog = bot.get_channel(733746271684263936)
    embed=discord.Embed(title= "manual ban", description= "**Offender:** " + user.mention + "\n**Reason:** " + logs.reason + "\n**Responsible moderator: **" + logs.user.mention,color= 0xff0000)
    await modlog.send(embed= embed)

@bot.event
async def on_member_unban(healthcord,user):
    logs = await healthcord.audit_logs(limit=1, action=discord.AuditLogAction.unban).flatten()
    logs = logs[0]
    if not(logs.reason):
        logs.reason = "No reason was specified."
    if "​​​" in logs.reason:
        return
    modlog = bot.get_channel(733746271684263936)
    embed = discord.Embed(title= "manual unban", description= "**Offender:** " + user.mention + "\n**Responsible moderator: **" + logs.user.mention, color= 0xff0000)
    await modlog.send(embed= embed)


invitemessage = {}

@bot.event
async def on_invite_create(invite):
    global invitemessage
    modlog = bot.get_channel(733746271684263936)
    user = invite.inviter
    userstr = user.name + "#" + user.discriminator
    if invite.max_uses:
        maxuses = " out of " + str(invite.max_uses)
    else:
        maxuses =  ""
    if user.avatar:
        avatarurl = "https://cdn.discordapp.com/avatars/" + str(user.id) + "/" + user.avatar + ".webp"
        embed = discord.Embed(title= "Created by " + userstr, description= "**Link:** " + invite.url + "\n**Channel: **" + invite.channel.mention + "\n**Uses:** " + str(invite.uses) + maxuses, color= 0xfffcbb)
        embed.set_author(name="New invite", icon_url= avatarurl)
    else:
        embed = discord.Embed(title= "Created by " + userstr, description= "**Link:** " + invite.url + "\n**Channel: **" + invite.channel.mention + "\n**Uses:** " + str(invite.uses) + maxuses + "\n```glsl\n# User has a default profile picture.\n```", color= 0xfffcbb)
        embed.set_author(name="New invite")
    embed.set_footer(text="React to this message with ❌ to delete this invite.")
    message = await modlog.send(embed= embed)
    await message.add_reaction("❌")
    invitemessage[message] = invite

@bot.event
async def on_reaction_add(reaction, user):
    global invitemessage
    if reaction.message in invitemessage and reaction.emoji == "❌" and user != bot.user:
        invite = invitemessage[reaction.message]
        if invite.max_uses:
            maxuses = " out of " + str(invite.max_uses)
        else:
            maxuses =  ""
        embed = discord.Embed(title= " ", description= "**Invite deleted** \n**Channel: **" + invite.channel.mention + "\n**Uses:** " + str(invite.uses) + maxuses, color= 0xfffcbb)
        embed.set_author(name="New invite (deleted)")
        await invite.delete()
        await reaction.message.edit(embed = embed)

@bot.event
async def on_member_remove(member):
    modlog = bot.get_channel(733746271684263936)
    memberstr = member.name + "#" + member.discriminator
    timeonserver = datetime.now() - member.joined_at
    healthcord = bot.get_guild(688206199992483851)
    logs = await healthcord.audit_logs(limit=1, action=discord.AuditLogAction.kick).flatten()
    logs = logs[0]
    if not(logs.reason):
        logs.reason = "No reason specified."
    if "​​​" not in logs.reason and member.id == logs.target.id:
        embed=discord.Embed(title= "manual kick", description= "**Offender:** " + member.mention + "\n**Reason:** " + logs.reason + "\n**Responsible moderator: **" + logs.user.mention,color= 0xff0000)
        await modlog.send(embed= embed)

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