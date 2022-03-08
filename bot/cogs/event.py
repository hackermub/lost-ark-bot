import discord
from discord.ext import commands
import logging

#Cog for discord event handling
class EventHandler(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self,payload: discord.RawReactionActionEvent):
        if payload.member.bot:
            return

        if payload.emoji.name == "🔔":
            channel = await self.bot.fetch_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)

            if not len(message.embeds):
                return
            
            embed = message.embeds[0]

            if embed.title == "Click on the bell to get role Rappel":
                await message.remove_reaction(payload.emoji,payload.member)
                rapple = self.bot.guild.get_role(int(self.bot.ROLE_ID))
                if rapple in payload.member.roles:
                    return
                await payload.member.add_roles(rapple)
                await channel.send(f"{payload.member.mention} received the role `{rapple.name}`!")



    # @commands.Cog.listener()
    # async def on_message(self, message:discord.Message):
    #     pass 

    
    # Member joins server
    # @commands.Cog.listener()
    # async def on_guild_join(self, guild:discord.Guild):
    #     pass

    # Member leaves server
    # @commands.Cog.listener()
    # async def on_guild_remove(self, guild:discord.Guild):
    #     pass
        

def setup(bot:commands.Bot):
    bot.add_cog(EventHandler(bot))