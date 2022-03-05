from glob import glob
import discord
from discord.ext import commands
from discord import ui
import os,json
from pathlib import Path
from pytz import timezone

# Bot subclass
class BotSubclass(commands.Bot):

    def __init__(self):

        config_path = "config.json"
        if os.path.exists('debugconfig.json'): # Use configurations for test server
            config_path = 'debugconfig.json'

        # Get Tokens and global variables
        with open(config_path, "r") as config:
            self._DATA = json.load(config)

            self._TOKEN = self._DATA["BOT_TOKEN"]
            self.PREFIX = self._DATA["BOT_PREFIX"]
            self.DEVS = self._DATA['DEVS']

            self.TIMEZONE = timezone(self._DATA['TIMEZONE'])

            self.GUILD_ID = self._DATA['GUILD_ID']
            self.MESSAGE_CHANNEL_ID = self._DATA['MESSAGE_CHANNEL_ID']
            self.ROLE_ID = self._DATA['ROLE_ID']

        self._cogs = [p.stem for p in Path(".").glob("./bot/cogs/*.py")]
        self._intents = discord.Intents().all()

        super().__init__(command_prefix=self.prefix, intents = self._intents, case_insensitive=True)
        self.setup()


    #Bot login,logout and setup

    def setup(self):

        print("Starting to load cogs...")
        for cog in self._cogs:
            try:
                self.load_extension(f"bot.cogs.{cog}")
                print(f"Extension {cog} loaded.")
            except Exception as exc:
                print(f"Failed to load extension {cog}: {exc}")
                raise exc
        print('Completed loading cogs')

    def run(self):

        print('Running Bot')
        super().run(self._TOKEN)

    async def shutdown(self):
        print("Closing connection to Discord...")
        await super().close()

    async def close(self):
        print("Closing on keyboard interrupt...")
        await self.shutdown()

    async def on_connect(self):
        print(f" Connected to Discord (latency: {self.latency*1000:,.0f} ms).")

    async def on_resumed(self):
        print("Bot resumed.")

    async def on_disconnect(self):
        print("Bot disconnected.")

    async def on_ready(self):

        await self.register_commands()
        
        print(f"Logged in as {self.user}")

        self.guild = await self.fetch_guild(self.GUILD_ID)

        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name =f"{self.PREFIX}help"))
        print(discord.__version__)

    async def prefix(self, bot, msg):
        return commands.when_mentioned_or(self.PREFIX)(bot, msg)


    