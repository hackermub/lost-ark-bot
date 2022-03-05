import discord
from discord.ext import commands

#Reloader cog for loading and unloading Cogs directly from discord
class Reloader(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx: discord.ApplicationContext):
        if str(ctx.author.id) not in ctx.bot.DEVS:
            msg = await ctx.send(f"{ctx.command.name} is a dev only command")
            await msg.delete(delay=5)
            return False
        return True;

    #A command to load extension directly from discord
    @commands.command(name = "load", aliases=["l"])
    async def  load(self, ctx:commands.Context,extension:str):
        try:
            self.bot.load_extension('bot.cogs.'+extension)
        except Exception as exc:
            msg = await ctx.send(f'Failed to load {extension}: {exc}')
        else:
            msg = await ctx.send(f'{extension} loaded')
        await self.bot.register_commands()
        await ctx.message.delete(delay=5)
        await msg.delete(delay=5)

    #A command to unload extension directly from discord
    @commands.command(name = "unload", aliases=["u"])
    async def  unload(self, ctx:commands.Context,extension:str):
        try:
            self.bot.unload_extension('bot.cogs.'+extension)
        except Exception as exc:
            msg = await ctx.send(f'Failed to unload {extension}: {exc}')
        else:
            msg = await ctx.send(f'{extension} Unloaded')
        await self.bot.register_commands()
        await ctx.message.delete(delay=5)
        await msg.delete(delay=5)
    

    # A command to reload cogs directly from discord
    @commands.command(name = "reload",aliases=["r"])
    async def reload(self,ctx: commands.Context,extension:str):
        try:
            self.bot.unload_extension('bot.cogs.'+extension)
            self.bot.load_extension('bot.cogs.'+extension)
        except Exception as exc:
            msg = await ctx.send(f'Failed to reload {extension}: {exc}')
        else:
            msg = await ctx.send(f'{extension} Reloaded')
        await self.bot.register_commands()
        await ctx.message.delete(delay=5)
        await msg.delete(delay=5)


def setup(bot:commands.Bot):
    bot.add_cog(Reloader(bot))
