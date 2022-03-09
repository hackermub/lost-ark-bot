import discord
from discord.ext import commands

IMAGE_CHANNEL_ID = 951063741368270858 # Edit the id from here
class Image(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_message(self,message:discord.Message):
        if message.channel.id != IMAGE_CHANNEL_ID:
            return
        
        if not len(message.attachments):
            return

        try:
            delay = self.get_time(message.content)
        except:
            delay = 7*3600

        await message.delete(delay=delay)

    def get_time(self,content):
        hms = content.split(':')
        h = int(hms[0])
        m = int(hms[1]) if len(hms)>1 else 0
        s = int(hms[2]) if len(hms)>2 else 0
        return h*3600 + m*60 + s


def setup(bot:commands.Bot):
    bot.add_cog(Image(bot))
