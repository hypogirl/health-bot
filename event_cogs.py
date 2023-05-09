import asyncio
from datetime import datetime
import discord
from discord.ext import commands
import useful
from useful import config

mod_support = (int(config['MOD_SUPPORT_MESSAGE_ID']),int(config['MOD_SUPPORT_CHANNEL_ID']))
merch_support = (int(config['MERCH_SUPPORT_MESSAGE_ID']),int(config['MERCH_SUPPORT_CHANNEL_ID']))
open_tickets = {}
closed_tickets = {}
open_tickets_id = set()
closed_tickets_id = set()
intents = discord.Intents.all()
temp_bot = commands.Bot(command_prefix="!", intents=intents)

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @temp_bot.event
    async def on_message(message):
        if message.author == commands.bot.user:
            return

        if message.content.startswith(config["COMMAND_PREFIX"]):
            if message.content.startswith(config["COMMAND_PREFIX"] + "<:dovide:734404973466484816>"):
                message.content = config["COMMAND_PREFIX"] + "timeout" + message.content[29:]
            await commands.bot.process_commands(message)
            return

        if not(useful.checkmod(message)):
            if str(message.channel.id) == config['ART_CLUB_ID']:
                roles_names = [role.name for role in message.author.roles]
                if "CLUB LEADER" in roles_names and message.content and not(message.attachments) and not(useful.check_url(message.content)):
                    await message.delete()

            elif str(message.channel.id) in [config['WHOLESOME_MEMES_ID'], config['ART_SHARE_ID'], config['GLITCHTOBER_ID']]:
                if message.content and not(message.attachments) and not(useful.check_url(message.content)):
                    await message.delete()

    @temp_bot.event
    async def on_message_edit(before,after):
        if before.author.bot or before.content == after.content:
            return
        
        user_str = before.author.name + "#" + before.author.discriminator

        avatar_url = before.author.avatar.url if before.author.avatar else "https://cdn.discordapp.com/avatars/774402228084670515/5ef539d5f3e8d576c4854768727bc75a.png"

        embed = discord.Embed(title= "Message edited in #" + before.channel.name, description= f"**Before:** {before.content}\n**After:** {after.content}",color= 0x45b6fe)
        embed.set_author(name=user_str, icon_url=avatar_url)
        await commands.bot.get_channel(int(config['BIG_BROTHER_ID'])).send(embed= embed)

        if after.channel.id == int(config['WHOLESOME_MEMES_ID']) or after.channel.id ==int (config['ART_SHARE_ID']):
            if after.content and not(after.attachments) and not(useful.check_url(after.content)):
                await after.delete()

    @temp_bot.event
    async def on_message_delete(message):
        if message.author.bot:
            return
        
        user_str = message.author.name + "#" + message.author.discriminator
        avatar_url = message.author.avatar.url if message.author.avatar else "https://cdn.discordapp.com/avatars/774402228084670515/5ef539d5f3e8d576c4854768727bc75a.png"

        if message.content:
            description = message.content
        else:
            description = "*[This message only contained attachements.]*"
        embed=discord.Embed(title="Message deleted in #" + message.channel.name, description= description,color=0xff0000)
        embed.set_author(name=user_str, icon_url=avatar_url)
        await message.guild.get_channel(int(config['BIG_BROTHER_ID'])).send(embed= embed)

    @temp_bot.event
    async def on_member_join(member):
        avatar_url = member.avatar.url if member.avatar else "https://cdn.discordapp.com/avatars/774402228084670515/5ef539d5f3e8d576c4854768727bc75a.png"
        member_str = member.name + "#" + member.discriminator
        embed = discord.Embed(title= " ", description= f"User ID: {member.id}\n\n{member.mention}", color= 0xff0000)
        embed.set_author(name= member_str + " has joined the server.", icon_url= avatar_url)
        await member.guild.get_channel(int(config['NEW_USERS_ID'])).send(embed= embed)

    @temp_bot.event
    async def on_member_update(before, after):
        if after.id == 697891299080142919 and before.status != after.status:
            beej_embed = discord.Embed(color=0xff0000)
            if after.status == discord.Status.online:
                beej_embed.set_author(name="A wild BEEJ appeared!")
                await after.guild.get_channel(int(config['GENERAL_ID'])).send(embed= beej_embed)
            elif after.status == discord.Status.offline:
                beej_embed.set_author(name="BEEJ has fled.")
                await after.guild.get_channel(int(config['GENERAL_ID'])).send(embed= beej_embed)

    @temp_bot.event
    async def on_member_remove(member):
        now = datetime.utcnow()
        users_leaving = member.guild.get_channel(int(config['USERS_LEAVING_ID']))
        member_str = member.name + "#" + member.discriminator
        time_on_server = (now - member.joined_at).total_seconds()
        (time_text, _) = useful.time_builder(time_on_server, "s")
        
        avatar_url = member.avatar.url if member.avatar else "https://cdn.discordapp.com/avatars/774402228084670515/5ef539d5f3e8d576c4854768727bc75a.png"

        roles_str = ", ".join([role.mention for role in member.roles[1:]])

        embed = discord.Embed(title = "Member left", description = f"{member.mention} joined {time_text} ago.\n**Roles:** {roles_str}", color=0xff0000)
        embed.set_author(name= member_str, icon_url= avatar_url)
        await users_leaving.send(embed= embed)

    @temp_bot.event
    async def on_guild_channel_delete(channel):
        for message in open_tickets:
            if message.channel.id == channel.id:
                open_tickets.pop(message)
                open_tickets_id.remove(message.id)
                break

    @temp_bot.event
    async def on_member_update(before, after):
        new_roles = [role for role in after.roles if role not in before.roles]
        for role in new_roles:
            if role.name == "KILLER ELITE":
                new_user_embed = discord.Embed(title="", description="", color=0xff0000)
                new_user_embed.set_author(name= f"WELCOME {after.nick} TO THE KILLER ELITE")
                patrons_channel = after.guild.get_channel(int(config['PATREON_CHANNEL_ID']))
                await patrons_channel.send(after.mention, embed=new_user_embed)
                break


class ReactionAdd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @temp_bot.event
    async def on_raw_reaction_add(payload):
        if payload.user_id == commands.bot.user.id:
            return
        
        # tickets
        global mod_support
        global merch_support
        global roles_support
        global open_tickets
        global open_tickets_id
        global closed_tickets
        global closed_tickets_id

        if payload.channel_id in [mod_support[1],merch_support[1],roles_support[1]] or payload.message_id in open_tickets_id or payload.message_id in closed_tickets_id:
            # converting payload to usable variables
            healthcord = commands.bot.get_guild(payload.guild_id)
            user = healthcord.get_member(payload.user_id)
            channel = healthcord.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            amanda = healthcord.get_member(int(config['AMANDA_ID']))
            reaction = None
            for reaction_temp in message.reactions:
                if str(reaction_temp.emoji) == str(payload.emoji):
                    reaction = reaction_temp
                    break
            init_message = "Hello! " + user.mention
            if await useful.support_check(mod_support, reaction, user):
                for ticket_message,ticket_info in open_tickets.items():
                    if ticket_info == (user,"general-ticket"):
                        await ticket_message.channel.send(user.mention + " hello! You still have this opened ticket. A mod can assist you on whatever else you might need.")
                        return
                init_message += "\nWhat's the issue?\nA <@&{0}> will help you shortly.\n\n``(React to this message with 🔒 to close this ticket.)``".format(config['MOD_ROLE_ID'])
                await useful.create_ticket_channel(init_message,"general-ticket",user)
            elif await useful.support_check(merch_support, reaction, user):
                for ticket_message,ticket_info in open_tickets.items():
                    if ticket_info == (user,"merch-ticket"):
                        await ticket_message.channel.send(user.mention + " hello! You still have this opened ticket. A mod can assist you on whatever else you might need.")
                        return
                init_message += "\nIf you ordered from HEALTH's US-based merch site (<https://fashion.youwillloveeachother.com>), please DM {0} with your merch issue.\n\nIf you ordered from Loma Vista or Deathwish EU, please contact them via the below links:\n\nLoma Vista: <https://bodega.lomavistarecordings.com/pages/contact-us>\nDeathwish EU: <https://deathwishinc.eu/pages/contact>\n".format(amanda.mention)
                await useful.create_ticket_channel(init_message,"merch-ticket",user)
            elif await useful.support_check(roles_support, reaction, user):
                for ticket_message,ticket_info in open_tickets.items():
                    if ticket_info == (user,"roles-ticket"):
                        await ticket_message.channel.send(user.mention + " hello! You still have this opened ticket. A mod can assist you on whatever else you might need.")
                        return
                init_message += "\nAre you missing some roles?\n\n``(React to this message with 🔒 to close this ticket.)``"
                await useful.create_ticket_channel(init_message,"roles-ticket",user)

            if message in open_tickets:
                if reaction.emoji == "🔒":
                    await reaction.remove(user)
                    closed_ticket_cat = user.guild.get_channel(int(config['CLOSED_TICKET_CAT_ID']))
                    await reaction.message.channel.move(category= closed_ticket_cat, end= True)
                    mod_role = user.guild.get_role(int(config['MOD_ROLE_ID']))
                    overwrites = {user.guild.default_role: discord.PermissionOverwrite(read_messages=False), open_tickets[message][0]: discord.PermissionOverwrite(read_messages=False), mod_role: discord.PermissionOverwrite(read_messages=True)}
                    if "merch" in reaction.message.channel.name:
                        overwrites[user.guild.get_role(int(config['MERCH_SUPPORT_ID']))] = discord.PermissionOverwrite(read_messages=True)
                    await reaction.message.channel.edit(overwrites= overwrites)
                    new_message = await reaction.message.channel.send("``React to this message with 🔓 to re-open this ticket.``")
                    await new_message.add_reaction("🔓")
                    closed_tickets[new_message] = open_tickets[message]
                    closed_tickets_id.add(new_message.id)
                    open_tickets.pop(message)
                    open_tickets_id.remove(message.id)
                elif reaction.emoji == "❌" and user.id == amanda.id:
                    await reaction.message.channel.send("Deleting this channel...")
                    await asyncio.sleep(2)
                    await reaction.message.channel.delete(reason="merch ticket closed")
                    open_tickets.pop(message)
                    open_tickets_id.remove(message.id)
                    

            elif message in closed_tickets and reaction.emoji == "🔓":
                await reaction.remove(user)
                open_ticket_cat = user.guild.get_channel(int(config['OPEN_TICKET_CAT_ID']))
                await reaction.message.channel.move(category= open_ticket_cat, end= True)
                overwrites = {user.guild.default_role: discord.PermissionOverwrite(read_messages=False), closed_tickets[message][0]: discord.PermissionOverwrite(read_messages=True)}
                if "merch" in reaction.message.channel.name:
                    overwrites[user.guild.get_role(int(config['MERCH_SUPPORT_ID']))] = discord.PermissionOverwrite(read_messages=True)
                await reaction.message.channel.edit(overwrites= overwrites)
                new_message = await reaction.message.channel.send("``React to this message with 🔒 to close this ticket.``")
                await new_message.add_reaction("🔒")
                open_tickets[new_message] = closed_tickets[message]
                open_tickets_id.add(new_message.id)
                closed_tickets.pop(message)
                closed_tickets_id.remove(message.id)

        # curation
        global curated_messages
        if payload.emoji != str(payload.emoji) and (payload.emoji.name == "cacostar" or payload.emoji.name == "russtar") and payload.message_id not in curated_messages:
            healthcord = commands.bot.get_guild(payload.guild_id)
            channel = healthcord.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            reaction = None
            for reaction_temp in message.reactions:
                if str(reaction_temp.emoji) == str(payload.emoji):
                    reaction = reaction_temp
                    break
            if reaction.count == 7:
                curated_messages.add(payload.message_id)
                serverid = str(message.guild.id)
                channelid = str(message.channel.id)
                messageid = str(message.id)
                messageurl = "https://discord.com/channels/" + serverid + "/" + channelid + "/" + messageid
                
                avatar_url = message.author.avatar.url if message.author.avatar else "https://cdn.discordapp.com/avatars/774402228084670515/5ef539d5f3e8d576c4854768727bc75a.png"

                if message.embeds and message.author.id == 372175794895585280: # haiku bot ID
                    description = message.embeds[0].description.replace("\n\n","\n")
                    embed = discord.Embed(description= description, color=0xff0000)
                    embed.set_author(name= "Haiku by " + message.embeds[0].footer.text[2:])
                else:
                    embed = discord.Embed(description= message.content, color=0xff0000)
                    embed.set_author(name= message.author.display_name, icon_url=avatar_url)

                if message.attachments:
                    embed.set_image(url= message.attachments[0].url)

                embed.add_field(name="#" + message.channel.name, value="[Jump to message!](" + messageurl + ")", inline=False)

                if message.reference:
                    replied_message = await message.channel.fetch_message(message.reference.message_id) # getting the message it's being replied to
                    replied_avatar_url = replied_message.author.avatar.url if replied_message.author.avatar else "https://cdn.discordapp.com/avatars/774402228084670515/5ef539d5f3e8d576c4854768727bc75a.png"

                    embed.add_field(name="──────", value= "*This was a reply to:*")
                    embed.set_footer(text=replied_message.author.display_name + "\n" + replied_message.content, icon_url=replied_avatar_url)

                else:
                    embed.set_footer(text= str(message.created_at)[:-10] + " UTC")

                health_curated = healthcord.get_channel(int(config['CURATION_CHANNEL_ID']))
                await health_curated.send(embed= embed)