from email import message
from email.policy import default
from tabnanny import check
import discord
from discord.ext import commands
from discord.commands import slash_command,permissions

# Admin/Dev only commands
class Admin(commands.Cog):

    GUILD_IDS = []

    def __init__(self, bot:commands.Bot):

        self.bot = bot

        Admin.GUILD_IDS.append(int(self.bot.GUILD_ID))


    async def cog_check(self, ctx: discord.ApplicationContext):

        if not ctx.guild:
            interaction = await ctx.respond(f"{ctx.command.name} is a guild only command")
            await interaction.delete_original_message(delay=5)
            return False

        if not ctx.author.guild_permissions.administrator and str(ctx.author.id) not in ctx.bot.DEVS:
            interaction = await ctx.respond(f"{ctx.command.name} is a admin only command")
            await interaction.delete_original_message(delay=5)
            return False

        return True;

    @slash_command(
        name = "role" , 
        usage="/role" , 
        description = "Get and pin the role message in text channel (Admin only command, intended for one time use)" ,
        guild_ids=GUILD_IDS
    )
    async def role(self,ctx):
        if not await self.cog_check(ctx):
            return 
        
        interaction = await ctx.respond("Sending and pinning role message")

        embed = discord.Embed(title="Click on the bell to get role Rappel" , color= discord.Color.dark_magenta())

        msg = await ctx.channel.send(embed = embed)
        await msg.pin()
        await msg.add_reaction("🔔")
        
        await interaction.delete_original_message()

        

    @slash_command(
        name = "move" , 
        usage="/move" , 
        description = "Move all users in a different voice channel" ,
        guild_ids=GUILD_IDS,
        default_permissions = False 
    )
    @permissions.has_any_role("Leader Stratège" , "Leader Mokokos Anonymes")
    async def move(self,ctx, current_channel: discord.VoiceChannel, move_to: discord.VoiceChannel):
        
        if current_channel == move_to:
            await ctx.respond("Cant move to the same channel.")
            return

        tot =  len(current_channel.members)
        
        if not tot:
            await ctx.respond("No one is in that channel")
            return

        for member in current_channel.members:
            await member.move_to(move_to)

        await ctx.respond(f"Moved `{tot}` people from `{current_channel.name}` to `{move_to.name}`")
        
def setup(bot:commands.Bot):
    bot.add_cog(Admin(bot))

