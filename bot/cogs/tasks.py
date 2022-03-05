import discord
from discord.ext import commands,tasks
from datetime import datetime

class Tasks(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.auto_message.start()

    def cog_unload(self):
        self.auto_message.cancel()

    @tasks.loop(minutes=1)
    async def auto_message(self):
        now = datetime.now(self.bot.TIMEZONE)
        if now.hour==11 and now.minute==0:
            channel = await self.bot.guild.fetch_channel(self.bot.MESSAGE_CHANNEL_ID)
            embed = discord.Embed(title = "Rappel : N'oubliez pas de faire vos dons de guilde" , color= discord.Color.dark_magenta())
            await channel.send(embed = embed)

def setup(bot:commands.Bot):
    bot.add_cog(Tasks(bot))