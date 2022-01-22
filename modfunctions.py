import auxfunctions as aux
import asyncio
from dotenv import dotenv_values

config = dotenv_values('.env')

async def ban(ctx, member, reason):
    if not(reason):
        await ctx.guild.ban(member, delete_message_days= 0)
    else:
        await ctx.guild.ban(member,reason= reason, delete_message_days= 0)

async def unban(ctx, member, reason):
    if not(reason):
        await ctx.guild.unban(member)
    else:
        await ctx.guild.unban(member,reason= reason)
    
async def eject(ctx, member):
    if member.avatar:
            avatarurl = f"https://cdn.discordapp.com/avatars/{str(member.id)}/{member.avatar}.webp"
    else:
        avatarurl = "https://cdn.discordapp.com/avatars/774402228084670515/5ef539d5f3e8d576c4854768727bc75a.png"
    memberstr = member.name + "#" + member.discriminator
    await aux.eject_animation(memberstr,avatarurl,ctx.channel)
    await member.kick()

async def ban_eject(ctx, member, reason):
    if member.avatar:
        avatarurl = "https://cdn.discordapp.com/avatars/" + str(member.id) + "/" + member.avatar + ".webp"
    else:
        avatarurl = "https://cdn.discordapp.com/avatars/774402228084670515/5ef539d5f3e8d576c4854768727bc75a.png"
    memberstr = member.name + "#" + member.discriminator
    if reason =="":
        await aux.eject_animation(memberstr,avatarurl,ctx.channel)
        await ctx.guild.ban(member, delete_message_days= 0)
    else:
        await aux.eject_animation(memberstr,avatarurl,ctx.channel)
        await ctx.guild.ban(member,reason=reason, delete_message_days= 0)

async def mute(bot, ctx, member, reason, color):
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
    
    await member.add_roles(muted,reason="Muted", atomic=True)
    await ctx.send(embed= embed)
    try:
        await member.send(message)
    except:
        print(member.mention + " doesn't allow DMs. It's likely a bot.")

    embed2,modlog = aux.modlogembed(bot, type, reason, ctx, color, member)
    await modlog.send(embed = embed2)

    if timestr:
        await asyncio.sleep(secondsint)
        await member.remove_roles(muted, reason="Unmuted", atomic=True)

async def unmute(ctx, member, reason):
    muted = ctx.guild.get_role(int(config['MUTED_ROLE_ID']))
    await member.remove_roles(muted, reason="Unmuted", atomic=True)


async def main_aux(type, bot, ctx, member, reason):
    if type in ["ban", "unban"]:
        embed,message = aux.modactions(ctx, reason, member, type + "ned")
    else:
        embed,message = aux.modactions(ctx, reason, member, type + "ed")

    if embed:
        color = 0xff0000
        if type == "ban":
            await ban(ctx, member, reason)
            color = 0xff0000
        if type == "unban":
            await unban(ctx, member, reason)
            color = 0x149414
        elif type == "warn":
            color = 0xfffcbb
        elif type == "eject":
            await eject(ctx, member)
            color = 0xff0000
        elif type == "ban eject":
            await ban_eject(ctx, member, reason)
            color = 0xff0000
        elif type == "mute":
            color = 0xfffcbb
            await mute(bot, ctx, member, reason, color)
            return
        elif type == "unmute":
            await unmute(ctx, member, reason)
            color = 0x149414
        elif type == "kick":
            await member.kick()
            color = 0xfffcbb

        await ctx.send(embed= embed)
        embed2,modlog = aux.modlogembed(bot, type, reason, ctx, color, member)
        await modlog.send(embed = embed2)
        try:
            await member.send(message)
        except:
            print(member.mention + " doesn't allow DMs. It's likely a bot.")
    else:
        await ctx.send(f"You cannot {type} {member.name}#{member.discriminator}.")

async def main(type, bot, ctx, members, reason):
    for member in members:
        await main_aux(type, bot, ctx, member, reason)