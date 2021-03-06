import discord
from discord.ext import commands,tasks
import urllib
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as soup

class News():

    def __init__(self):
        self.name = "Lost Ark"
        self.names = ["lao", "lost ark", "Lost Ark"]
        self.news = {"title": None, "url": None, "desc": None, "image": None}
        self.color = 30070
        self.thumbnail = "https://cpz.github.io/Lost-Ark-SDK/GameIcon.ico"

    @classmethod
    def from_embed(cls, embed):
        news = cls()
        news.news["title"] = embed.title
        news.news["url"] = embed.url
        news.news["desc"] = embed.description
        news.news["image"] = embed.thumbnail.url
        return news

    def different(self,last_news):
        if not last_news:
            return True
        
        title = last_news.news["title"]
        
        # remove beginning and trailing space
        title = title.strip()
        news_title = self.news["title"].strip()

        return title != news_title

    def get_news_info(self):

        # Gets source of Lost Ark news page.
        try:
            request = Request("https://www.playlostark.com/fr-fr/news", headers={'User-Agent': 'Mozilla/5.0'})
            source = urlopen(request).read()
        except:
            raise Exception("Couldn't connect to " + self.name + "' website.")

        try:
            news_divs = soup(source, "html.parser").findAll("div",{"class":"ags-SlotModule ags-SlotModule--blog ags-SlotModule--threePerRow"})
        except:
            raise Exception("Error retrieving news_divs")

        # Gets Lost Ark news url.
        try:
            self.news["url"] = "https://www.playlostark.com" + news_divs[0].a["href"]
            if self.news["url"] is None:
                raise Exception("Could not find " + self.name + " url.")
            # print("url = " + self.news["url"])
        except:
            raise Exception("Error retrieving " + self.name + " url. 1")

        # Gets Lost Ark news title.
        try:
            news_title = soup(source, "html.parser").find("span",{"class":"ags-SlotModule-contentContainer-heading ags-SlotModule-contentContainer-heading ags-SlotModule-contentContainer-heading--blog"})
            self.news["title"] = news_title.find(text=True)
            if self.news["title"] is None:
                raise Exception("Could not find " + self.name + " title.")
            # print("title = " + self.news["title"])
        except:
            raise Exception("Error retrieving " + self.name + " title.")

        # Gets Lost Ark news description.
        try:
            news_description = soup(source, "html.parser").find("div",{"class":"ags-SlotModule-contentContainer-text ags-SlotModule-contentContainer-text--blog ags-SlotModule-contentContainer-text"})
            self.news["desc"] = news_description.find(text=True)
            if self.news["desc"] is None:
                raise Exception("Could not find " + self.name + " description.")
            # print("desc = " + self.news["desc"])
        except:
            raise Exception("Error retrieving " + self.name + " description.")

        # Gets Lost Ark news image.
        try:
            self.news["image"] = "https:" + soup(source, "html.parser").find("img",{"class":"ags-SlotModule-imageContainer-image"})["src"]
            if self.news["image"] is None:
                raise Exception("Could not find " + self.name + " url.")
            # print("image = " + self.news["image"])
        except:
            raise Exception("Error retrieving " + self.name + " url.")  


class LostArk(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.last_news = None
        self.news = News()
        self.update_news.start()

    def cog_unload(self):
        self.update_news.cancel()

    # Updates Lost Ark news every 5 minutes.
    @tasks.loop(minutes=5)
    async def update_news(self):
        await self.bot.wait_until_ready()
        news_channel = await self.bot.fetch_channel(int(self.bot.NEWS_CHANNEL_ID))

        if self.last_news is None:
            async for message in news_channel.history(limit=None):
                if message.author == self.bot.user:
                    self.last_news = News.from_embed(message.embeds[0])
                    break

        try:
            self.news.get_news_info()
           
            if self.news.different(self.last_news):
                self.last_news = self.news
                embed = discord.Embed(title=self.news.news["title"], url=self.news.news["url"], description=self.news.news["desc"], color=self.news.color)
                embed.set_thumbnail(url=self.news.thumbnail)
                embed.set_image(url=self.news.news["image"])
                await news_channel.send(embed=embed)

        except Exception as e:
            print(e)

def setup(bot:commands.Bot):
    bot.add_cog(LostArk(bot))