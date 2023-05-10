import discord
import re
import asyncio
from urllib.parse import urlparse
from dotenv import dotenv_values
import random

config = dotenv_values('.env')

mod_team = ["ADMIN", "THE VIBEGUARD"]
club_channels = [config['MOVIE_CLUB_ID'],config['BOOK_CLUB_ID'],config['ANIME_CLUB_ID'],config['MUSIC_CLUB_ID'],config['ART_CLUB_ID'],config['GAMING_CLUB_ID'],config['FOOD_CLUB_ID'], config['HEALTH_BOYZ_ID']]


def check_mod(ctx):
    return ctx.guild.get_role(config['MOD_ROLE_ID']) in ctx.author.roles or ctx.guild.get_role(config['ADMIN_ROLE_ID']) in ctx.author.roles


def get_modding_info(ctx, arg):
    members = list()

    for user_id in re.findall(r"<?@?(\d{18})>?", arg):
        if member_tmp := ctx.guild.get_member(int(user_id)):
            members.append(member_tmp)

    reason_list = re.findall(r"(?:(?:<@\d{18}>|\d{18})\s+)+((?:(?!<@\d{18}>|\d{18})\S+(?:\s+|$))+)$", arg)
    reason = reason_list[0] if reason_list else str()

    return members, reason

def get_mute_info(arg):
    time_list = re.findall(r"(?:(?:<@\d{18}>|\d{18})\s+)*(\d+)([smhdy])", arg)
    reason_list = re.findall(r"^(?:(?:<@\d{18}>|\d{18})\s+)+(?:\d+[smhdy]\s+)?((?:(?!<@\d{18}>|\d{18}|\d+[smhdy])\S+(?:\s+|$))+)$", arg)
    (time, unit) = time_list[0] if time_list else (0, None)
    reason = reason_list[0] if reason_list else str()

    return time_builder(int(time), unit), reason

def create_messages(user, reason, action):
    avatar_url = user.avatar.url if user.avatar else "https://cdn.discordapp.com/avatars/774402228084670515/5ef539d5f3e8d576c4854768727bc75a.png"
    user_str = user.name + "#" + user.discriminator
    mod_embed = discord.Embed(title=" ", color=0xff0000)
    mod_embed.set_author(name= f"{user_str} has been {action}.", icon_url= avatar_url)
    user_message = f"**You have been {action} by a moderator in HEALTHcord.**"

    if reason:
        mod_embed.description = "**Reason:** " + reason
        user_message += "\n**Reason:** " + reason

    return user_message, mod_embed

def create_modlog_embed(ctx, action, reason, colour, user):
    message = ctx.message
    modlog = ctx.guild.get_channel(int(config["MOD_LOG_ID"]))
    message_url = f"https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{message.id}"

    if not(reason):
        reason = "No reason given by the moderator."

    embed = discord.Embed(title= f"{action} | #{message.channel.name}", description= f"**Offender:** {user.mention}\n**Reason:** {reason }\n**Responsible moderator: **{message.author.mention}",color=colour)
    embed.add_field(name="-----", value="[Jump to incident](" + message_url + ")", inline=False)
    return embed, modlog

def get_unban_ids(arg):
    return re.findall(r"<?@?(\d{18})>?", arg)

async def generic_modding_action(ctx, arg, action, action_past, colour, reason = None):
    members, reason_tmp = get_modding_info(ctx, arg)

    if action != "mute":
        reason = reason_tmp

    for member in members:
        if ctx.author.top_role <= member.top_role:
            await ctx.send(f"You cannot {action} **{member.nick or member.name}**.")
            continue
        user_message, mod_embed = create_messages(member, reason, action_past)
        modlog_embed, modlog = create_modlog_embed(ctx, action, reason, colour, member)
        try:
            await member.send(user_message.replace("and their messages have been purged", ""))
        except:
            print(member.id, "doesn't allow DMs.")

        await ctx.send(embed= mod_embed)
        await modlog.send(embed= modlog_embed)

    return members, reason

def time_builder(amount, unit):
    if not(amount):
        return (None, 0)
    
    time_units = {
    "y": [60 * 60 * 24 * 365, "year"],
    "d": [60 * 60 * 24, "day"],
    "h": [60 * 60, "hour"],
    "m": [60, "minute"],
    "s": [1, "second"],
    }

    final_amount = amount_in_seconds = amount * time_units[unit][0]
    final_units = list()

    for u, [seconds, unit_text] in time_units.items():
        value = amount_in_seconds // seconds
        if value:
            final_units.append((value, unit_text if value == 1 else unit_text + "s"))
        amount_in_seconds %= seconds

    time_text = ", ".join([f"{int(value)} {unit}" for value, unit in final_units[:-1]])

    if time_text:
        time_text += " and "
    time_text += f"{final_units[-1][0]} {final_units[-1][1]}"

    return (time_text, final_amount)

async def eject_animation(ctx, member):
    member_name = member.name + "#" + member.discriminator
    avatar_url = member.avatar.url if member.avatar else "https://cdn.discordapp.com/avatars/774402228084670515/5ef539d5f3e8d576c4854768727bc75a.png"

    animation = [member_name+"ඞ", member_name+" was an ඞ", member_name+" was an Impostor. ඞ"]
    description = ".             .        .\n    .\n                 .\nඞ\n.          .\n                 .\n .                  ."
    animation_embed = discord.Embed(title=" ", description= description, color=0xff0000)
    animation_embed.set_author(name= member_name + " is being ejected.", icon_url= avatar_url)
    animation_message = await ctx.send(embed= animation_embed)

    for frame in animation:
        await asyncio.sleep(2)
        description = f".             .        .\n    .\n                 .\n{frame}\n.          .\n                 .\n .                  ."
        animation_embed.description = description
        animation_embed.set_author(name= member_name + " is being ejected.", icon_url= avatar_url)
        await animation_message.edit(embed= animation_embed)
    
    await asyncio.sleep(2)
    final_frame = member_name + " was an Impostor."
    description = f".             .        .\n    .\n                 .\n{final_frame}\n.          .\n                 .\n .                  ."
    animation_embed.description = description
    animation_embed.set_author(name= member_name + " has been ejected.", icon_url= avatar_url)
    await animation_message.edit(embed= animation_embed)

def check_url_aux(message):
    try:
        result = urlparse(message)
        return all([result.scheme, result.netloc, result.path])
    except:
        return False

def check_url(message):
    return check_url_aux(message) or check_url_aux(message + "/")

async def support_check(ids, reaction, user):
    if reaction.message.id == ids[0]:
        await reaction.remove(user)
        return reaction.emoji == "📩"

async def create_ticket_channel(init_message,name,user, open_tickets, open_tickets_id):
    merch_support_role = user.guild.get_role(int(config['MERCH_SUPPORT_ID']))
    mod_role = user.guild.get_role(int(config['MOD_ROLE_ID']))
    if name == "merch-ticket":
        overwrites = {user.guild.default_role: discord.PermissionOverwrite(read_messages=False), user: discord.PermissionOverwrite(read_messages=True, send_messages=False), mod_role:discord.PermissionOverwrite(read_messages=True)}
        overwrites[merch_support_role] = discord.PermissionOverwrite(read_messages=True, manage_channels=True)
    else:
         overwrites = {user.guild.default_role: discord.PermissionOverwrite(read_messages=False), user: discord.PermissionOverwrite(read_messages=True), mod_role:discord.PermissionOverwrite(read_messages=True)}

    open_ticket_cat = user.guild.get_channel(int(config['OPEN_TICKET_CAT_ID']))
    channel = await user.guild.create_text_channel(name + "-" + user.name, category= open_ticket_cat, overwrites= overwrites)
    message = await channel.send(init_message)
    if name != "merch-ticket":
        await message.add_reaction("🔒")
    open_tickets[message] = (user,name)
    open_tickets_id.add(message.id)

    return open_tickets, open_tickets_id