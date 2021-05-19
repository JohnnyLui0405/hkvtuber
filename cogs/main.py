import discord
# from googleapiclient.discovery import build
from discord.ext import commands,tasks
from pymongo import MongoClient
import pymongo
import json
import math
from decouple import config

client = MongoClient(config("mongodb"))
db = client.HKVTuber
collection = db.channel

with open("./json/channels.json") as jfile:
    channels = json.load(jfile)
with open("./json/commands.json") as jfile:
    commandsList = json.load(jfile)

def generateEmbed(page):
    x = (page - 1) * 10
    y = page * 10
    datas = channels[x:y]
    nameList = ["[查看所有頻道](https://vtuber.hk/channels.html)"]
    for data in datas:
        nameList.append(f"[{data['name']}]({data['url']})({data['channelId']})")
    text = "\n\n".join(nameList)
    embed=discord.Embed(title="港V直播通知名單", description=text,color=0xccf500)
    embed.set_footer(text=f"第 {page} 頁 ")
    return embed

def isValidId(Id):
    for channel in channels:
        if channel["channelId"] == Id:
            return channel
    return None

class main(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.Version = "v0.1.2"
        print("正在初始化...")

    def insert_info(self,ctx):
        if collection.count_documents({"_id": ctx.guild.id}) == 0:
            info = {"_id": ctx.guild.id, "guild_name": ctx.guild.name, "channel_id":None, "YTChannels":None}
            collection.insert_one(info)

    @commands.Cog.listener()
    async def on_ready(self):
        print("完成載入 {}".format(self.Version))
        self.changePresence.start()
        self.count = 0

    # @commands.Cog.listener()
    # async def on_voice_state_update(self,member,before,after):
    #     if before.channel == None and member.guild.id == 754976890439335986:
    #         channel = self.bot.get_guild(754976890439335986).get_channel(754984820957773865)
    #         embed=discord.Embed(timestamp=datetime.datetime.utcnow(),description=":inbox_tray: " + member.mention + " **joined voice channel** " + f"**`{after.channel}`**",color=0x00cc18)
    #         embed.set_author(name=f'{member}',icon_url=member.avatar_url)
    #         embed.set_footer(text=' ')
    #         await channel.send(embed=embed)


    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def setup(self, ctx, channel: discord.TextChannel = None):
        self.insert_info(ctx)
        if channel == None:
          channel = ctx.channel
        collection.update_one({"_id": ctx.guild.id}, {"$set": {"channel_id": channel.id}})
        await ctx.send(f"你已設定直播通知頻道為 {channel.mention}")
        print(f"YoutubeChannelChange: {ctx.guild.id} / {channel.id}")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def delete(self, ctx):
        if collection.count_documents({"_id": ctx.guild.id}) == 1:
                    channel_id = collection.update_one({"_id": ctx.guild.id},{"$set": {"channel_id": None}})
                    channel = self.bot.get_channel(channel_id)
                    await ctx.send(f"你已移除直播通知頻道")
                    print(f" YoutubeLiveChannelRemove: {ctx.guild.id} / None")
        else:
            await ctx.send("此伺服器並沒有設定直播通知頻道 請先用`hkv!setup`設定")

    @commands.command(aliases=["add"])
    @commands.has_permissions(manage_channels=True)
    async def addnoticechannel(self, ctx, * ,ChannelId):
        if ChannelId == "all":
            collection.update_one({"_id":ctx.guild.id}, {"$set": {"YTChannels": "all"}})
            await ctx.send("已設定為 `all`")
        else:
            guild = collection.find_one({"_id":ctx.guild.id})
            ChannelIdList = ChannelId.split(" ")
            addedchannels = []
            for Id in ChannelIdList:
                channel = isValidId(Id)
                if channel:
                    if guild["YTChannels"] == ("all" or None):
                        guild["YTChannels"] = []
                    if not Id in guild["YTChannels"]:
                        guild["YTChannels"].append(Id)
                        addedchannels.append(f"[{channel['name']}]({channel['url']})")
            collection.update_one({"_id":ctx.guild.id}, {"$set": {"YTChannels": guild["YTChannels"]}})
            if not addedchannels == []:
                text = "\n".join(addedchannels)
                embed = discord.Embed(title="新增直播通知頻道", description=text, color=0xf901dc)
                await ctx.send(embed=embed)
            else:
                await ctx.send(embed=discord.Embed(description="頻道ID無效或已存在通知列表中", color=0xf901dc))

    @commands.command(aliases=["remove"])
    @commands.has_permissions(manage_channels=True)
    async def removenoticechannel(self, ctx, * ,ChannelId):
        guild = collection.find_one({"_id":ctx.guild.id})
        ChannelIdList = ChannelId.split(" ")
        removedchannels = []
        for Id in ChannelIdList:
            channel = isValidId(Id)
            if channel:
                if guild["YTChannels"] == ("all" or None):
                    guild["YTChannels"] = []
                if Id in guild["YTChannels"]:
                    guild["YTChannels"].remove(Id)
                    removedchannels.append(f"[{channel['name']}]({channel['url']})")
        collection.update_one({"_id":ctx.guild.id}, {"$set": {"YTChannels": guild["YTChannels"]}})
        if not removedchannels == []:
            text = "\n".join(removedchannels)
            embed = discord.Embed(title="移除直播通知頻道", description=text, color=0xf901dc)
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=discord.Embed(description="頻道ID無效或不存在通知列表中", color=0xf901dc))
                    
    @commands.command()
    async def noticechannellist(self, ctx):
        guild = collection.find_one({"_id":ctx.guild.id})
        ChannelList = []
        if guild["YTChannels"] == "all":
            await ctx.send(embed=discord.Embed(title="已新增頻道清單", description="[全部港V頻道](https://www.vtuber.hk/channels.html)", color=0xf901dc))
            return
        for Id in guild["YTChannels"]:
            channel = isValidId(Id)
            ChannelList.append(f"[{channel['name']}]({channel['url']})({channel['channelId']})")
        text = "\n".join(ChannelList)
        await ctx.send(embed=discord.Embed(title="已新增頻道清單", description=text, color=0xf901dc))

    @commands.command()
    async def forcesetup(self, ctx, channel: discord.TextChannel = None):
        if not ctx.author.id == 334534960654450690:
            await ctx.send("You have no permission to use this command")
            return
        self.insert_info(ctx)
        if channel == None:
            channel = ctx.channel
        collection.update_one({"_id": ctx.guild.id}, {"$set": {"channel_id": channel.id}})
        await ctx.send(f"你已設定直播通知頻道為 {channel.mention}")
        print(f"YoutubeChannelChange: {ctx.guild.id} / {channel.id}")

    @commands.command()
    async def forceremove(self, ctx):
        if not ctx.author.id == 334534960654450690:
            await ctx.send("You have no permission to use this command")
            return
        if collection.count_documents({"_id": ctx.guild.id}) == 1:
            channel_id = collection.update_one({"_id": ctx.guild.id},{"$set": {"channel_id": None}})
            channel = self.bot.get_channel(channel_id)
            await ctx.send(f"你已移除直播通知頻道")
            print(f" YoutubeLiveChannelRemove: {ctx.guild.id} / None")
        else:
            await ctx.send("此伺服器並沒有設定直播通知頻道 請先用`hkv!setup`設定")

    @commands.command()
    async def help(self, ctx):
        embed=discord.Embed(title="港V直播通知 v0.1.0", description="機械人由<@334534960654450690>(Johnnnny#4298)開發 感謝vtuber.hk站長提供資料\n當香港Vtuber直播時會發出通知\n如果有功能想新增歡迎搵我展開激烈討論\n\n機械人開發委託接受中\n有興趣可以搵我了解詳情", color=0xf901dc)
        embed.set_footer(text="使用 hkv!commands 取得所有指令")
        await ctx.send(embed=embed)

    @commands.command(aliases=["commands"])
    async def Commands(self, ctx):
        embed=discord.Embed(title="指令表", color=0xf901dc)
        for command in commandsList:
            embed.add_field(name=f"`{command['name']}`", value=command['value'], inline=False)
        embed.set_footer(text=f"港V直播通知 {self.Version}")
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self,ctx,error):
        print(error)
        if isinstance(error, commands.MissingPermissions):
            text = "{}, 你需要 `{}` 權限才能執行此指令".format(ctx.message.author.mention, ", ".join(error.missing_perms))
            await ctx.send(text)

    @commands.command()
    async def servers(self,ctx):
        if ctx.author.id == 334534960654450690:
            text = "\n".join(guild.name for guild in self.bot.guilds)
            await ctx.send(text)
        else:
            await ctx.send("You have no permission to use this command")

    @commands.Cog.listener()
    async def on_command(self,ctx):
        text = "[{}] {} 執行 {}{} 指令 ".format(ctx.guild.name,ctx.author.display_name,ctx.prefix,ctx.command.name)
        print(text)

    @commands.command()
    async def channels(self, ctx, page=1):
        msg = await ctx.send(embed=generateEmbed(1))
        await msg.add_reaction("⬆️")
        await msg.add_reaction("⬇️")

    @commands.Cog.listener()
    async def on_reaction_add(self,reaction,user):
        if user.bot:
          return
        if reaction.message.author == self.bot.user:
          if reaction.message.embeds[0].title == "港V直播通知名單":
            if reaction.emoji == "⬇️":
              page = int(reaction.message.embeds[0].footer.text.split(" ")[1])
              if page < math.ceil(len(channels)/10):
                page += 1
              await reaction.message.edit(embed=generateEmbed(int(page)))
            if reaction.emoji == "⬆️":
              page = int(reaction.message.embeds[0].footer.text.split(" ")[1])
              if page > 1:
                page -= 1
              await reaction.message.edit(embed=generateEmbed(int(page)))

    @commands.Cog.listener()
    async def on_reaction_remove(self,reaction,user):
        if user.bot:
          return
        if reaction.message.author == self.bot.user:
          if reaction.message.embeds[0].title == "港V直播通知名單":
            if reaction.emoji == "⬇️":
              page = int(reaction.message.embeds[0].footer.text.split(" ")[1])
              if page < math.ceil(len(channels)/10):
                page += 1
              await reaction.message.edit(embed=generateEmbed(int(page)))
            if reaction.emoji == "⬆️":
              page = int(reaction.message.embeds[0].footer.text.split(" ")[1])
              if page > 1:
                page -= 1
              await reaction.message.edit(embed=generateEmbed(int(page)))

    @tasks.loop(minutes=2)
    async def changePresence(self):
        choices = [f"{len(self.bot.guilds)} 個伺服器 | hkv!help",f"{len(self.bot.users)} 個用戶 | hkv!help",f"{self.Version} | hkv!help"]
        choice = choices[self.count]
        if self.count == len(choices)-1:
            self.count = 0
        else:
            self.count += 1
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=choice))

def setup(bot):
    bot.add_cog(main(bot))
