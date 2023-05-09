import asyncio
import discord
from discord.ext import commands
import useful
from useful import config, mod_team, club_channels

class UserCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def timeout(self, ctx, *, arg):
        _, time, _ = useful.get_mute_info(ctx, arg, muting= False)
        
        if not(time[0]):
            await ctx.send("Please enter a valid time unit.")
            return
        
        muted_role = ctx.guild.get_role(config["MUTED_ROLE_ID"])
        await ctx.author.add_roles(muted_role, reason= "Self-requested timeout", atomic= True)
        embed = discord.Embed(title= " ", color= 0xff0000)
        embed.set_author(name= f"Enjoy your timeout. ({time[0]})")
        await ctx.channel.send(embed= embed)
        await asyncio.sleep(time[1])
        await ctx.author.remove_roles(muted_role, reason= "Timout ended", atomic= True)
        await ctx.author.send("Your timeout in HEALTHcord has ended.")
    
    @commands.command()
    @commands.has_any_role(int(config['CLUB_LEADER_ID']), *mod_team, int(config['WARBOSS_ID']))
    async def pin(self, ctx, arg):
        if ctx.channel.id in club_channels:
            if not(ctx.message.reference):
                await ctx.reply("Reply to the message you want to pin.")
            else:
                message_to_pin = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                await message_to_pin.pin(reason="Pinned by " + ctx.author.name)
                await ctx.message.delete()
                
        elif useful.check_mod(ctx, config["MOD_ROLE_ID"], config["ADMIN_ROLE_ID"]):
            if not(ctx.message.reference):
                await ctx.reply("Reply to the message you want to pin.")
            else:
                message_to_pin = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                await message_to_pin.pin(reason="Pinned by " + ctx.author.name)
                await ctx.message.delete()

    @commands.command()
    @commands.has_any_role(int(config['CLUB_LEADER_ID']), *mod_team, int(config['WARBOSS_ID']))
    async def unpin(self, ctx, arg):
        if str(ctx.channel.id) in club_channels:
            if not(ctx.message.reference):
                await ctx.reply("Reply to the message you want to pin.")
            else:
                message_to_unpin = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                pinned_messages = await ctx.channel.pins()
                for message in pinned_messages:
                    if message.id == message_to_unpin.id:
                        await message.unpin(reason="Unpinned by " + ctx.author.name)
                        await ctx.message.delete()
                        break

        elif useful.check_mod(ctx, config["MOD_ROLE_ID"], config["ADMIN_ROLE_ID"]):
            if not(ctx.message.reference):
                await ctx.reply("Reply to the message you want to pin.")
            else:
                message_to_unpin = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                pinned_messages = await ctx.channel.pins()
                for message in pinned_messages:
                    if message.id == message_to_unpin.id:
                        await message.unpin(reason="Unpinned by " + ctx.author.name)
                        await ctx.message.delete()
                        break