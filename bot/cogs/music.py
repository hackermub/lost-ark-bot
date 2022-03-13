from random import choices
import discord 
from discord import Interaction, slash_command,ui
from discord.ext import commands
from discord.commands import Option, permissions
import wavelink
import logging

from .music_files import player,track,api
from .music_files.player import Player
from .music_files.track import Track
from bot.cogs.error import Error

class Music(commands.Cog):

    GUILD_IDS = []

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        Music.GUILD_IDS.append(int(self.bot.GUILD_ID))

        bot.loop.create_task(self.connect_nodes())

    # Default checks for all commands in the cog
    async def cog_check(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send('Music commands are not available in DM')
            return False
        return True

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node):
        print(f"Wavelink node '{node.identifier}' ready.")

    async def connect_nodes(self):
        await self.bot.wait_until_ready()
        self.bot.node = await wavelink.NodePool.create_node(bot=self.bot,
                                                            host='127.0.0.1',  # '172.31.21.15',
                                                            port=2333,
                                                            password='youshallnotpass')

    async def get_player(self, payload: discord.RawReactionActionEvent):
        if not payload.member.voice or (channel:=payload.member.voice.channel) is None:
            raise Error.NoVoiceChannel
        if pl:=self.bot.node.get_player(self.bot.get_guild(payload.guild_id)):
            if pl.is_connected():
                if pl.channel==channel:
                    return pl
                raise Error.AlreadyConnectedToChannel
        return await channel.connect(cls=Player)


    # listeners
    @commands.Cog.listener()
    async def on_wavelink_track_end(self,player: Player, track: Track, reason):
        if(reason=="REPLACED" or reason=="STOPPED"):
            return
        logging.info(reason)
        await player.next_track()

    @commands.Cog.listener()
    async def on_wavelink_track_exception(self,player: Player, track: Track,error):
        logging.warning(error)

    @commands.Cog.listener()
    async def on_wavelink_track_stuck(self,player: Player, track: Track,threshold):
        logging.warning('threshold: '+threshold)
        player.restart_track()

    @commands.Cog.listener()
    async def on_wavelink_websocket_closed(self,player,reason,code):
        await player.cleanup_and_disconnect()

    async def get_player(self, author: discord.Member, guild: discord.Guild):
        if not author.voice or (channel:=author.voice.channel) is None:
            raise Error.NoVoiceChannel
        if pl:=self.bot.node.get_player(guild):
            if pl.is_connected():
                if pl.channel==channel:
                    return pl
                raise Error.AlreadyConnectedToChannel
        return await channel.connect(cls=player.Player)

    # Commands
    @slash_command(
        name = "play" , 
        usage="/play" , 
        description = "play songs from youtube search, youtube link or spotify link" ,
        guild_ids=GUILD_IDS
    )
    @commands.guild_only()
    @commands.cooldown(1, 2, commands.BucketType.member)
    async def play(
        self,
        ctx:commands.Context,
        method: Option(str,"Select search/link type",choices=["search","youtube link","spotify link"]),
        query: Option(str, "Paste the link or type what to search (Based on your chosen method)")
    ):
        try:
            vc = await self.get_player(ctx.author,ctx.guild)
        except Error.NoVoiceChannel:
            interaction = await ctx.respond(f"{ctx.author.mention}, you need to be in a voice channel first")
            return await interaction.delete_original_message(delay=5)
        except Error.AlreadyConnectedToChannel:
            interaction = await ctx.respond(f"{ctx.author.mention}, music already playing in {ctx.guild.voice_client.channel}")
            return await interaction.delete_original_message(delay=5)


        if method == "search":
            youtubeTrack = await api.searchYoutube(self.bot,query)
            if not track:
                return await ctx.respond("No song found")

        elif method == "youtube link":
            link = api.checkYoutube(query)
            if not link:
                return await ctx.respond("Invalid youtube link")

            try:
                youtubeTrack = await api.getYoutubeTrack(self.bot,link)
            except:
                return await ctx.respond("Invalid or unavailable link")

        else:
            return await ctx.respond("Spotify link not yet implemented")

        song = track.Track(self.bot,ctx.author,youtubeTrack)
        response = f" `{song.get_title()}` added to queue"
        try:
            await vc.add_track(song,ctx.channel)
        except Error.TrackAlreadyInQueue:
            response = f" `{song.get_title()}` is already in queue"
        
        interaction = await ctx.respond(ctx.author.name+response)
        await interaction.delete_original_message(delay=5)



def setup(bot: commands.Bot):
    bot.add_cog(Music(bot))


