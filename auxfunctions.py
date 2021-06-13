import discord
import random
from dotenv import dotenv_values
from urllib.parse import urlparse

config = dotenv_values('.env')

def checkmod(ctx):
    mod = ctx.guild.get_role(int(config['MOD_ROLE_ID']))
    admin = ctx.guild.get_role(int(config['ADMIN_ROLE_ID']))
    return mod in ctx.author.roles or admin in ctx.author.roles or ctx.author.id == ctx.guild.owner.id

def getvars(bot, ctx, arg): # gets the user, reason and member for the mod functions
    member_id = ""

    for x in range(len(arg)):
        if arg[x].isnumeric():
            member_id += arg[x]
        if arg[x] == ">" or arg[x] == " ":
            break

    member_id = int(member_id)
    reason = arg[x+2:]
    member = ctx.guild.get_member(member_id)
    
    return reason, member

def modactions(ctx, reason, member, action): # writes the embed and dm for the mod functions
    if ctx.author.top_role > member.top_role or ctx.author.id == ctx.guild.owner.id:
        if member.avatar:
            avatarurl = "https://cdn.discordapp.com/avatars/" + str(member.id) + "/" + member.avatar + ".webp"
        else:
            avatarurl = "https://cdn.discordapp.com/avatars/774402228084670515/5ef539d5f3e8d576c4854768727bc75a.png"
        memberstr = member.name + "#" + member.discriminator
        embed = False
        message = False
        if reason:
            embed=discord.Embed(title=" ", description="**Reason:** "+reason, color=0xff0000)
            embed.set_author(name= memberstr + " has been " + action + ".", icon_url= avatarurl)
            message = "**You have been "+action+" by a moderator in HEALTHcord.\nReason:** " + reason
        else:
            embed=discord.Embed(title=" ", color=0xff0000)
            embed.set_author(name= memberstr + " has been " + action + ".", icon_url= avatarurl)
            message = "**You have been " + action + " by a moderator in HEALTHcord.**"
        return embed,message
    return False, False

def modlogembed(bot, action, reason, message, colour, user): # building the embed for the mod log channel
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

def timestrbuilder(seconds, secondsint, suffix):
    if seconds[-1] == "s":
        if secondsint == 1:
            suffix += " second"
        else:
            suffix += " seconds"
    elif seconds[-1] == "m":
        if secondsint == 1:
            suffix += " minute"
        else:
            suffix += " minutes"
        secondsint *= 60
    elif seconds[-1] == "h":
        if secondsint == 1:
            suffix += " hour"
        else:
            suffix += " hours"
        secondsint *= 60 * 60
    elif seconds[-1] == "d":
        if secondsint == 1:
            suffix += " day"
        else:
            suffix += " days"
        secondsint *= 60 * 60 * 24
    elif seconds[-1] == "y":
        if secondsint == 1:
            suffix += " year"
        else:
            suffix += " years"
        secondsint *= 60 * 60 * 24 * 365
    return suffix,secondsint

def remove_spoiler(m):
    c_list = [(0,0)]
    c = 0

    while True:
        for c in range(c,len(m)):
            if m[c:c+2] == "||":
                c_list.append((c,c+2))
                break
        c += 2
        if c >= len(m) - 1:
            break

    m_removed = str()
    for c in range(0,len(c_list)-1,2):
        m_removed += m[c_list[c][1]:c_list[c+1][0]]
    if len(c_list) % 2:
        m_removed += m[c_list[-1][1]:]
    else:
        m_removed += m[c_list[-1][1]-2:]
    
    return m_removed

def album(m,mentions):
    albuml = []
    m = "".join(m.lower().split()) # remove spaces, all lowercase, makes it easier for search
    if "||" in m:
        m = remove_spoiler(m) # removes spoiler text, not to react to it

    health = (["heaven", "girlattorney", "triceratops", "crimewave", "courtship", "zoothorns", "tabloidsores", "glitterpills", "perfectskin", "losttime","//m\\\\"],755047461734580306)
    getcolor = (["getcolor", "inheat","dieslow","nicegirls","death+","beforetigers","severin","eatflesh","wearewater","inviolet"],755047462640681030)
    deathmagic = (["deathmagic","victim","stonefist","mentoday","fleshworld","courtshipii","darkenough","salvia","newcoke","lalooks","l.a.looks","hurtyourself","drugsexist"],755047460019372062)
    vol4 = (["vol4","vol.4","psychonaut","feelnothing","godbotherer","blackstatic","lossdeluxe","nc-17","nc17","themessage","ratwars","strangedays","wrongbag","slavesoffear","decimation"],755047461944557618)
    disco4 = (["disco4","cyberpunk2020","cyberpunk2.0.0.0","cyberpunk2.0.0.0.","body/prison","bodyprison","powerfantasy","judgmentnight","innocence","fullofhealth","colors","hateyou","dflooks","d.f.looks","massgrave","deliciousape","hardtobeagod"],755050227215630426)
    disco3 = (["disco3","euphoria","slumlord","crusher"],755050414008696852)
    disco2 = (["disco2","usaboys","u.s.a.boys"],755050225751556117)
    payne = (["pain", "<:max:697638034937479239>"],697638034937479239)
    powercaco = (["powerfantasy"],766716666540326932)
    #ping = (["774402228084670515"],788902728658452481)

    cacoheart = ([("good","love","based","thank","great","amazing","well"),("bad","racist","racism","cringe","dumb","idiot","stupid","bug","n'twork","notwork","suck","shit","poo","bitch")],804113756622684220,[697627002202750976,708429172737048606,735209358379450471,736196814654668830,"notfunny"])
    albums = [health,getcolor,deathmagic,vol4,disco2,disco3,payne,powercaco]

    if "disco4+" in m or "disco4plus" in m:
        albuml.append(827609782176972801)
    else:
        for x in disco4[0]:
            if x in m:
                albuml.append(disco4[1])
                break

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

def check_url_aux(message):
    try:
        result = urlparse(message)
        return all([result.scheme, result.netloc, result.path])
    except:
        return False

def check_url(message):
    return check_url_aux(message) or check_url_aux(message + "/")