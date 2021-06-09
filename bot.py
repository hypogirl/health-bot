from datetime import datetime
from discord.ext import commands
from dotenv import dotenv_values
import asyncio
import auxfunctions as aux
import discord
import math
import mysql.connector
import random
import time
#from pathlib import Path

config = dotenv_values('.env')

'''
healthbot = mysql.connector.connect(
  host=config['DB_HOST'],
  user=config['DB_USERNAME'],
  password=config['DB_PASSWORD'],
  database=config['DB_NAME']
)
'''

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help') #removing the default help command
mod_support = (None,None)
merch_support = (None,None)
roles_support = (None,None)
open_tickets = {}
closed_tickets = {}

@bot.event
async def on_ready():
    print('HEALTHbot is online')

@bot.command()
async def ping(ctx):
    await ctx.message.reply("Pong!")

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
        await ctx.send(ctx.author.mention + ", I've sent you a DM with the help menu.")


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
    if not(aux.checkmod(ctx)):
        return
        
    reason, member = aux.getvars(bot, ctx, arg)
    if not(member):
        await ctx.send(member.mention + " is not a member of HEALTHcord.")
        return
    embed,message = aux.modactions(ctx, reason, member, "warned")
    if embed:
        await ctx.send(embed=embed)
        embed2,modlog = aux.modlogembed(bot,"warn", reason, ctx, 0xfffcbb, member)
        await modlog.send(embed= embed2)
        try:
            await member.send(message)
        except:
            print(member.mention + " doesn't allow DMs. It's likely a bot.")
    else:
        await ctx.send("You cannot warn this user.")

@bot.command()
async def ban(ctx, *, arg):
    if not(aux.checkmod(ctx)):
        return

    reason, member = aux.getvars(bot, ctx, arg)
    if not(member):
        await ctx.send(member.mention + " is not a member of HEALTHcord.")
        return
    embed,message = aux.modactions(ctx, reason, member, "banned")
    if embed:
        if reason =="":
            await ctx.guild.ban(member,reason="​​​", delete_message_days=0)
        else:
            await ctx.guild.ban(member,reason=reason + "​​​", delete_message_days=0)
        await ctx.send(embed=embed)
        embed2,modlog = aux.modlogembed(bot,"ban", reason, ctx, 0xff0000, member)
        await modlog.send(embed = embed2)
        try:
            await member.send(message)
        except:
            print(member.mention + " doesn't allow DMs. It's likely a bot.")
    else:
        await ctx.send("You cannot ban this user.")

@bot.command()
async def unban(ctx, *, arg):
    if not(aux.checkmod(ctx)):
        return

    reason, member = aux.getvars(bot, ctx, arg)
    if not(member):
        await ctx.send("I cannot find this user. Please unban " + member.mention + " manually.")
        return
    embed,message = aux.modactions(ctx, reason, member, "unbanned")
    if embed:
        if reason == "":
            await ctx.guild.unban(member,reason="​​​")
        else:
            await ctx.guild.unban(member,reason=reason + "​​​")
        await ctx.send(embed=embed)
        embed2,modlog = aux.modlogembed(bot,"unban", reason, ctx, 0x149414, member)
        await modlog.send(embed = embed2)
        try:
            await member.send(message)
        except:
            print(member.mention + " doesn't allow DMs. It's likely a bot.")
    else:
        await ctx.send("You cannot ban this user.")

@bot.command()
async def kick(ctx, *, arg):
    if not(aux.checkmod(ctx)):
        return

    reason, member = aux.getvars(bot, ctx, arg)
    if not(member):
        await ctx.send(member.mention + " is not a member of HEALTHcord.")
        return
    embed,message = aux.modactions(ctx, reason, member, "kicked")
    if embed:
        await member.kick()
        await ctx.send(embed=embed)
        embed2,modlog = aux.modlogembed(bot,"kick", reason, ctx, 0xffa500, member)
        await modlog.send(embed = embed2)
        try:
            await member.send(message)
        except:
            print(member.mention + " doesn't allow DMs. It's likely a bot.")
    else:
        await ctx.send("You cannot kick this user.")

@bot.command()
async def mute(ctx, *, arg):
    if not(aux.checkmod(ctx)):
        return

    reason, member = aux.getvars(bot, ctx, arg)

    if not(member):
        await ctx.send(member.mention + " is not a member of HEALTHcord.")
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
        timestr, secondsint = aux.timestrbuilder(seconds,secondsint,suffix)
        embed,message = aux.modactions(ctx, reason, member, "muted for " + timestr)
    else:
        embed,message = aux.modactions(ctx, reason, member, "muted")
    muted = ctx.guild.get_role(int(config['MUTED_ROLE_ID']))
    if embed:
        await member.add_roles(muted,reason="Muted", atomic=True)
        await ctx.send(embed=embed)
        embed2,modlog = aux.modlogembed(bot,"mute", reason, ctx, 0xfffcbb, member)
        await modlog.send(embed = embed2)
        try:
            await member.send(message)
        except:
            print(member.mention + " doesn't allow DMs. It's likely a bot.")
        if timestr:
            await asyncio.sleep(secondsint)
            await member.remove_roles(muted, reason="Unmuted", atomic=True)
            embed2,modlog = aux.modlogembed(bot,"unmute", "Timed unmute", ctx, 0x149414, member)
            await modlog.send(embed = embed2)
    else:
        await ctx.send("You cannot mute this user.")

@bot.command()
async def unmute(ctx, *, arg):
    if not(aux.checkmod(ctx)):
        return

    reason, member = aux.getvars(bot, ctx, arg)
    if not(member):
        await ctx.send(member.mention + " is not a member of HEALTHcord.")
        return
    embed,message = aux.modactions(ctx, reason, member, "unmuted")
    muted = ctx.guild.get_role(int(config['MUTED_ROLE_ID']))
    if embed:
        await member.remove_roles(muted, reason="Unmuted", atomic=True)
        await ctx.send(embed=embed)
        embed2,modlog = aux.modlogembed(bot,"unmute", reason, ctx, 0x149414, member)
        await modlog.send(embed = embed2)
        try:
            await member.send(message)
        except:
            print(member.mention + " doesn't allow DMs. It's likely a bot.")
    else:
        await ctx.send("You cannot unmute this user.")

@bot.command()
async def spam(ctx, *, arg):
    if not(aux.checkmod(ctx)):
        return
    for x in range(int(arg)):
        await ctx.send("spam")

@bot.command()
async def purge(ctx, *, arg):
    if not(aux.checkmod(ctx)):
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

    modlog = bot.get_channel(int(config['MOD_LOG_ID']))
    embed = discord.Embed(title=" ", description="Messages deleted:\n\n" + deletedstr, color=0xff0000)
    embed.set_author(name= str(len(deleted)) + " messages purged | #" + ctx.channel.name)
    await modlog.send(embed= embed)

@bot.command()
async def backup(ctx):
    if not(aux.checkmod(ctx)):
        return

    now = str(datetime.now())
    now = now.split(' ')[0]
    templates = await ctx.guild.templates()
    if templates:
        template = templates[0]
        await template.sync()
    else:
        await ctx.guild.create_template(name= "back up " + now)
        templates = await ctx.guild.templates()
        template = templates[0]
    
    backup_guild = await template.create_guild(name= "back up " + now)
    await template.delete()
    channel = await backup_guild.create_text_channel(name= "invite-link-channel")
    invite = await channel.create_invite(max_uses=1)
    await ctx.send("Backup server created.\n" + invite.url)

@bot.command()
async def ticketmessage(ctx, *, arg):
    global mod_support
    global merch_support
    global roles_support

    channel_id = ""
    for x in range(len(arg)):
        if arg[x].isnumeric():
            channel_id += arg[x]
        if arg[x] == ">" or arg[x] == " ":
            break
    channel_id = int(channel_id)
    ticket_type = arg[x+2:]
    channel = ctx.guild.get_channel(channel_id)
    await channel.purge()
    embed = discord.Embed(description="To create a ticket react with 📩", color=0xff0000)
    if ticket_type == "mod":
        embed.set_author(name="Raise an issue with the mod team")
        message = await channel.send(embed= embed)
        mod_support = (message.id, channel_id)
        await message.add_reaction("📩")
    elif ticket_type == "merch":
        embed.set_author(name="Got a problem with a merch order? Here's your place to raise a ticket.")
        message = await channel.send(embed= embed)
        await message.add_reaction("📩")
        merch_support = (message.id, channel_id)
    elif ticket_type == "roles":
        embed.set_author(name="Missing a role?")
        message = await channel.send(embed= embed)
        await message.add_reaction("📩")
        roles_support = (message.id, channel_id)

@bot.command()
async def deletebackup(ctx):
    await ctx.guild.delete()

@bot.command()
async def motd(ctx, *, arg):    # setting someone as the member of the day
    if not(aux.checkmod(ctx)):
        return

    motd = ctx.guild.get_role(int(config['MOTD_ROLE_ID']))
    reason, member = aux.getvars(bot, ctx, arg)

    emojis = [697621015337107466,737315507509657661,697879872391086113,697880868743544903,753291933950017627,753291934008606762,804113756622684220,709794793051390153]
    emoji = bot.get_emoji(random.choice(emojis))
    await member.add_roles(motd,reason="Member of the day", atomic=True)
    message = await ctx.send(member.mention + " is member of the day!")
    await message.add_reaction(emoji)
    await asyncio.sleep(86400)
    await member.remove_roles(motd,reason="End of the member of the day", atomic=True)

@bot.command()
async def roledump(ctx, *, arg):
    role_id, role_name = False, False
    try:
        role_id = int(arg)
    except:
        role_name = arg
    
    if role_id:
        role = ctx.guild.get_role(role_id)
        if not(role):
            await ctx.reply("Invalid role ID provided.")
            return
    else:
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if not(role):
            await ctx.reply("Invalid role name provided.")
            return
    
    memberlist = ""
    embed = discord.Embed(title="ROLE DUMP",description=role.name)
    i = 1
    j = 0
    for member in ctx.guild.members:
        if i == 40:
            j += 1
            embed.add_field(name="Part " + str(j), value=memberlist, inline=False)
            memberlist = ""
            i = 1
        if role in member.roles:
            i += 1
            memberlist += member.name + "#" + member.discriminator + "\n"
    if memberlist:
        j += 1
        embed.add_field(name="Part " + str(j), value=memberlist, inline=False)
    await ctx.send(embed= embed)

@bot.command()
async def createtrigger(ctx, *, arg):
    if not(aux.checkmod(ctx)):
        return

    '''sql = "INSERT INTO `Trigger` (name, content,embed) VALUES (%s, %s, 0)"
    val = (arg1, arg2)
    mycursor = healthbot.cursor()
    mycursor.execute(sql, val)
    healthbot.commit()
    await ctx.send("Trigger created successfully.")'''
    left = False
    for x in range(len(arg)):
        if arg[x] == " ":
            left = arg[:x]
            right = arg[x+1:]
            break
    if not(left):
        await ctx.send("Invalid trigger.")

@bot.command()
async def deletetrigger(ctx, *, arg):
    if not(aux.checkmod(ctx)):
        return

    '''mycursor = healthbot.cursor()
    sql = "DELETE FROM `Trigger` WHERE name = '" + arg + "'"
    mycursor.execute(sql)
    healthbot.commit()
    await ctx.send("Trigger deleted successfully.")'''

@bot.command()
async def timeout(ctx, *, arg):
    seconds = arg
    suffix = seconds[:-1]
    secondsint = int(seconds[:-1])
    muted = ctx.guild.get_role(int(config['MUTED_ROLE_ID']))
    timestr,secondsint = aux.timestrbuilder(seconds,secondsint,suffix)
    embed=discord.Embed(title=" ", color=0xff0000)
    embed.set_author(name="Enjoy your timeout. (" + timestr + ")")
    await ctx.author.add_roles(muted,reason="Self-requested timeout", atomic=True)
    await ctx.send(embed=embed)
    await asyncio.sleep(secondsint)
    await ctx.author.remove_roles(muted, reason="Timout ended", atomic=True)
    await ctx.author.send("Your timeout in HEALTHcord has ended.")

@bot.command()
async def pin(ctx):
    flag = False
    club_channels = [config['MOVIE_CLUB_ID'],config['BOOK_CLUB_ID'],config['ANIME_CLUB_ID'],config['MUSIC_CLUB_ID'],config['ART_CLUB_ID'],config['GAMING_CLUB_ID'],config['FOOD_CLUB_ID']]
    if str(ctx.channel.id) in club_channels:
        for role in ctx.author.roles:
            if role.name == "CLUB LEADER" or aux.checkmod(ctx):
                flag = True
                break
    if flag:
        if not(ctx.message.reference):
            await ctx.reply("Reply to the message you want to pin.")
        else:
            message_to_pin = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            await message_to_pin.pin(reason="Pinned by " + ctx.author.name)
            await ctx.message.delete()

@bot.command()
async def unpin(ctx):
    flag = False
    club_channels = [config['MOVIE_CLUB_ID'],config['BOOK_CLUB_ID'],config['ANIME_CLUB_ID'],config['MUSIC_CLUB_ID'],config['ART_CLUB_ID'],config['GAMING_CLUB_ID'],config['FOOD_CLUB_ID']]
    if str(ctx.channel.id) in club_channels:
        for role in ctx.author.roles:
            if role.name == "CLUB LEADER" or aux.checkmod(ctx):
                flag = True
                break
    if flag:
        if not(ctx.message.reference):
            await ctx.reply("Reply to the message you want to pin.")
        else:
            message_to_unpin = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            pinned_messages = await ctx.channel.pins()
            for message in pinned_messages:
                if message.id == message_to_unpin.id:
                    await message.unpin(reason="Unpinned by " + ctx.author.name)
                    break

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

    if message.channel.id == int(config['WHOLESOME_MEMES_ID']) or message.channel.id ==int (config['ART_SHARE_ID']):
        if message.content and not(message.attachments) and not(aux.check_url(message.content)):
            await message.delete()

    if message.content.lower() in ["musik make love to " + bot.user.mention,"musik make love to health bot","musik make love to health :: bot"]:
        await asyncio.sleep(1)
        o = ["Oh no... not me.","Why would anyone want this","What is wrong with you?","No no no no no no"]
        await message.channel.send(random.choice(o))


    if message.channel.id != 707011962898481254: #we dont want this on #on-the-real certainly
        emojialbum = aux.album(message.content,message.mentions) #finding if there is a mention to a HEALTH album in a message and reacting with the album cover
        if emojialbum:
            for x in emojialbum:
                emoji = bot.get_emoji(x)
                await message.add_reaction(emoji)


## MISC EVENTS ##

@bot.event
async def on_message_edit(before,after):
    if before.channel.id in [733412404351991846,791453462063742987]: # curated channels, it prevents the channel to be spammed with cacostar counter updates
        return
    if before.content != after.content:
        userstr = before.author.name + "#" + before.author.discriminator

        if before.author.avatar:
            avatarurl = "https://cdn.discordapp.com/avatars/" + str(before.author.id) + "/" + before.author.avatar + ".webp"
        else:
            avatarurl = "https://cdn.discordapp.com/avatars/774402228084670515/5ef539d5f3e8d576c4854768727bc75a.png"

        embed=discord.Embed(title="Message edited in #" + before.channel.name, description= "**Before:** " + before.content + "\n**After:** " + after.content,color=0x45b6fe)
        embed.set_author(name=userstr, icon_url=avatarurl)
        await bot.get_channel(int(config['BIG_BROTHER_ID'])).send(embed= embed)

    if after.channel.id == int(config['WHOLESOME_MEMES_ID']) or after.channel.id ==int (config['ART_SHARE_ID']):
        if after.content and not(after.attachments) and not(aux.check_url(after.content)):
            await after.delete()

@bot.event
async def on_message_delete(message):
    if message.author.id in [372175794895585280,225522547154747392]: #its the haikubot and stock bot's ID, its useless showing when these are deleted
        return
    userstr = message.author.name + "#" + message.author.discriminator
    
    if message.author.avatar:
        avatarurl = "https://cdn.discordapp.com/avatars/" + str(message.author.id) + "/" + message.author.avatar + ".webp"
    else:
        avatarurl = "https://cdn.discordapp.com/avatars/774402228084670515/5ef539d5f3e8d576c4854768727bc75a.png"
    
    if message.content:
        description = message.content
    else:
        description = "*[This message only contained attachements.]*"
    embed=discord.Embed(title="Message deleted in #" + message.channel.name, description= description,color=0xff0000)
    embed.set_author(name=userstr, icon_url=avatarurl)
    await bot.get_channel(int(config['BIG_BROTHER_ID'])).send(embed= embed)

@bot.event
async def on_member_ban(guild,user):
    logs = await guild.audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten()
    logs = logs[0]
    if not(logs.reason):
        logs.reason = "No reason specified."
    if logs.user.id != bot.user.id:
        modlog = bot.get_channel(int(config['MOD_LOG_ID']))
        embed=discord.Embed(title= "manual ban", description= "**Offender:** " + user.mention + "\n**Reason:** " + logs.reason + "\n**Responsible moderator: **" + logs.user.mention,color= 0xff0000)


@bot.event
async def on_member_unban(guild, user):
    logs = await guild.audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten()
    logs = logs[0]
    if not(logs.reason):
        logs.reason = "No reason specified."
    if logs.user.id != bot.user.id:
        modlog = bot.get_channel(int(config['MOD_LOG_ID']))
        embed = discord.Embed(title= "manual unban", description= "**Offender:** " + user.mention + "\n**Responsible moderator: **" + logs.user.mention, color= 0xff0000)
        await modlog.send(embed= embed)


invitemessage = {}

@bot.event
async def on_invite_create(invite):
    global invitemessage
    modlog = bot.get_channel(int(config['MOD_LOG_ID']))
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

last_curated_message_id = False

async def support_check(ids, reaction, user):
    if reaction.message.id == ids[0]:
        await reaction.remove(user)
        return reaction.emoji == "📩"

async def create_ticket_channel(init_message,name,user):
    global open_tickets
    merch_support_role = user.guild.get_role(int(config['MERCH_SUPPORT_ID']))
    overwrites = {user.guild.default_role: discord.PermissionOverwrite(read_messages=False), user: discord.PermissionOverwrite(read_messages=True)}
    if name == "merch-ticket":
        overwrites[merch_support_role] = discord.PermissionOverwrite(read_messages=True)

    open_ticket_cat = user.guild.get_channel(int(config['OPEN_TICKET_CAT_ID']))
    channel = await user.guild.create_text_channel(name + "-" + user.name, category= open_ticket_cat, overwrites= overwrites)
    message = await channel.send(init_message)
    await message.add_reaction("🔒")
    open_tickets[str(message.id)] = user

@bot.event
async def on_reaction_add(reaction, user):
    # tickets
    global mod_support
    global merch_support
    global roles_support
    global open_tickets
    global closed_tickets
    if user != bot.user:
        flag_mod = await support_check(mod_support, reaction, user)
        flag_merch = await support_check(merch_support, reaction, user)
        flag_roles = await support_check(roles_support, reaction, user)
        init_message = "Hello! " + user.mention
        if flag_mod:
            init_message += "\nWhat's the issue?\n\n``(React to this message with 🔒 to close this ticket.)``"
            await create_ticket_channel(init_message,"general-ticket",user)
        elif flag_merch:
            init_message += "\nDo you have an issue with a merch order?\n" + user.guild.get_role(int(config['MERCH_SUPPORT_ID'])).mention +" will get back to you shortly.\n\n``(React to this message with 🔒 to close this ticket.)``"
            await create_ticket_channel(init_message,"merch-ticket",user)
        elif flag_roles:
            init_message += "\nAre you missing some roles?\n\n``(React to this message with 🔒 to close this ticket.)``"
            await create_ticket_channel(init_message,"roles-ticket",user)
        

        if str(reaction.message.id) in open_tickets and reaction.emoji == "🔒":
            await reaction.remove(user) 
            closed_ticket_cat = user.guild.get_channel(int(config['CLOSED_TICKET_CAT_ID']))
            await reaction.message.channel.move(category= closed_ticket_cat, end= True)
            overwrites = {user.guild.default_role: discord.PermissionOverwrite(read_messages=False), open_tickets[str(reaction.message.id)]: discord.PermissionOverwrite(read_messages=False)}
            if "merch" in reaction.message.channel.name:
                overwrites[user.guild.get_role(int(config['MERCH_SUPPORT_ID']))] = discord.PermissionOverwrite(read_messages=True)
            await reaction.message.channel.edit(overwrites= overwrites)
            message = await reaction.message.channel.send("``React to this message with 🔓 to re-open this ticket.``")
            await message.add_reaction("🔓")
            closed_tickets[str(message.id)] = open_tickets[str(reaction.message.id)]
            open_tickets.pop(str(reaction.message.id))

        elif str(reaction.message.id) in closed_tickets and reaction.emoji == "🔓":
            await reaction.remove(user)
            open_ticket_cat = user.guild.get_channel(int(config['OPEN_TICKET_CAT_ID']))
            await reaction.message.channel.move(category= open_ticket_cat, end= True)
            overwrites = {user.guild.default_role: discord.PermissionOverwrite(read_messages=False), closed_tickets[str(reaction.message.id)]: discord.PermissionOverwrite(read_messages=True)}
            if "merch" in reaction.message.channel.name:
                overwrites[user.guild.get_role(int(config['MERCH_SUPPORT_ID']))] = discord.PermissionOverwrite(read_messages=True)
            await reaction.message.channel.edit(overwrites= overwrites)
            message = await reaction.message.channel.send("``React to this message with 🔒 to close this ticket.``")
            await message.add_reaction("🔒")
            open_tickets[str(message.id)] = closed_tickets[str(reaction.message.id)]
            closed_tickets.pop(str(reaction.message.id))

    # mod-log invites
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
        
    # curation
    global last_curated_message_id
    healthcurated = bot.get_channel(int(config['CURATION_CHANNEL_ID']))
    if reaction.message.id != last_curated_message_id and reaction.count == 5 and reaction.emoji != str(reaction.emoji) and (reaction.emoji.name == "cacostar" or reaction.emoji.name == "russtar"):
        serverid = str(reaction.message.guild.id)
        channelid = str(reaction.message.channel.id)
        messageid = str(reaction.message.id)
        messageurl = "https://discord.com/channels/" + serverid + "/" + channelid + "/" + messageid
        
        if reaction.message.author.avatar:
            avatarurl = "https://cdn.discordapp.com/avatars/" + str(reaction.message.author.id) + "/" + reaction.message.author.avatar + ".webp"
        else:
            avatarurl = "https://cdn.discordapp.com/avatars/774402228084670515/5ef539d5f3e8d576c4854768727bc75a.png"

        if reaction.message.embeds and reaction.message.author.id == 372175794895585280: # haiku bot ID
            description = reaction.message.embeds[0].description.replace("\n\n","\n")
            embed = discord.Embed(description=description, color=0xff0000)
            embed.set_author(name="Haiku by " + reaction.message.embeds[0].footer.text[2:])
        else:
            embed = discord.Embed(description=reaction.message.content, color=0xff0000)
            embed.set_author(name=reaction.message.author.display_name, icon_url=avatarurl)
            
        if reaction.message.attachments:
            embed.set_image(url=reaction.message.attachments[0].url)
        
        embed.add_field(name="#" + reaction.message.channel.name, value="[Jump to message!](" + messageurl + ")", inline=False)
        
        if reaction.message.reference:
            replied_message = await reaction.message.channel.fetch_message(reaction.message.reference.message_id) # getting the message it's being replied to
            
            if replied_message.author.avatar:
                replied_avatarurl = "https://cdn.discordapp.com/avatars/" + str(replied_message.author.id) + "/" + replied_message.author.avatar + ".webp"
            else:
                replied_avatarurl = "https://cdn.discordapp.com/avatars/774402228084670515/5ef539d5f3e8d576c4854768727bc75a.png"

            embed.add_field(name="──────", value= "*This was a reply to:*")
            embed.set_footer(text=replied_message.author.display_name + "\n" + replied_message.content, icon_url=replied_avatarurl)

        else:
            embed.set_footer(text=reaction.message.id)
        
        await healthcurated.send(embed=embed)

@bot.event
async def on_member_join(member):
    if member.avatar:
        avatarurl = "https://cdn.discordapp.com/avatars/" + str(member.id) + "/" + member.avatar + ".webp"
    else:
        avatarurl = "https://cdn.discordapp.com/avatars/774402228084670515/5ef539d5f3e8d576c4854768727bc75a.png"
    memberstr = member.name + "#" + member.discriminator
    embed = discord.Embed(title=" ", description="User ID: " + str(member.id), color=0xff0000)
    embed.set_author(name= memberstr + " has joined the server.", icon_url= avatarurl)
    await bot.get_channel(int(config['NEW_USERS_ID'])).send(embed= embed)

@bot.event
async def on_member_remove(member):
    now = datetime.now()
    modlog = bot.get_channel(int(config['MOD_LOG_ID']))
    memberstr = member.name + "#" + member.discriminator
    timeonserver = now - member.joined_at
    logs = await member.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick).flatten()
    logs = logs[0]
    if not(logs.reason):
        logs.reason = "No reason specified."
    if logs.user.id != bot.user.id and logs.target.id == member.id:
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

@bot.event
async def on_member_update(before, after):
    if after.id == 830204658370871306 and before.status != after.status:
        embed = discord.Embed(color=0xff0000)
        if after.status == discord.Status.online:
            embed.set_author(name="A wild BEEJ appeared!")
            await after.guild.get_channel(int(config['GENERAL_ID'])).send(embed= embed)
        elif after.status == discord.Status.offline:
            embed.set_author(name="BEEJ has fled.")
            await after.guild.get_channel(int(config['GENERAL_ID'])).send(embed= embed)



bot.run(config['BOT_TOKEN'])
