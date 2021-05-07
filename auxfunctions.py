import discord
from dotenv import dotenv_values

config = dotenv_values('.env')

def checkmod(ctx):
    mod = ctx.guild.get_role(config['MOD_ROLE_ID'])
    admin = ctx.guild.get_role(config['ADMIN_ROLE_ID'])
    return mod in ctx.author.roles or admin in ctx.author.roles

def getvars(bot, ctx, arg): # gets the user,reason and member for the mod functions
    memberID = ""

    for x in range(len(arg)):
        if arg[x].isnumeric():
            memberID += arg[x]
        if arg[x] == ">" or arg[x] == " ":
            break

    reason = arg[x+2:]
    member = ctx.guild.get_member(memberID)
    
    return reason, member, memberID 

def modactions(ctx, reason, member, action): # writes the embed and dm for the mod functions
    if ctx.author.top_role > member.top_role or ctx.author.id == config['OWNER_ID']:
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
