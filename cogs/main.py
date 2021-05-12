import discord
# from googleapiclient.discovery import build
from discord.ext import commands,tasks
from pymongo import MongoClient
import pymongo
from decouple import config

client = MongoClient(config("mongodb"))
db = client.HKVTuber
collection = db.channel

class main(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.Version = "v0.2.0"
        print("正在初始化...")

    def insert_info(self,ctx):
        if collection.count_documents({"_id": ctx.guild.id}) == 0:
            info = {"_id": ctx.guild.id, "guild_name": ctx.guild.name, "channel_id":None}
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
    async def setup(self, ctx, platform = "all", channel: discord.TextChannel = None):
        self.insert_info(ctx)
        channel = ctx.channel
        collection.update_one({"_id": ctx.guild.id}, {"$set": {"channel_id": channel.id}})
        await ctx.send(f"你已設定直播通知頻道為 {channel.mention}")
        print(f"YoutubeChannelChange: {ctx.guild.id} / {channel.id}")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def remove(self, ctx, platform = None):
        if collection.count_documents({"_id": ctx.guild.id}) == 1:
                    channel_id = collection.update_one({"_id": ctx.guild.id},{"$set": {"channel_id": None}})
                    channel = self.bot.get_channel(channel_id)
                    await ctx.send(f"你已移除直播通知頻道")
                    print(f" YoutubeLiveChannelRemove: {ctx.guild.id} / None")
        else:
            await ctx.send("此伺服器並沒有設定直播通知頻道 請先用`hkv!setup`設定")

    @commands.command()
    async def forcesetup(self, ctx, platform = "all", channel: discord.TextChannel = None):
        if not ctx.author.id == 334534960654450690:
            await ctx.send("只有開發者能使用此指令")
            return
        self.insert_info(ctx)
        channel = ctx.channel
        collection.update_one({"_id": ctx.guild.id}, {"$set": {"channel_id": channel.id}})
        await ctx.send(f"你已設定直播通知頻道為 {channel.mention}")
        print(f"YoutubeChannelChange: {ctx.guild.id} / {channel.id}")

    @commands.command()
    async def forceremove(self, ctx, platform = "all"):
        if not ctx.author.id == 334534960654450690:
            await ctx.send("只有開發者能使用此指令")
            return
        if collection.count_documents({"_id": ctx.guild.id}) == 1:
            channel_id = collection.update_one({"_id": ctx.guild.id},{"$set": {"channel_id": None}})
            channel = self.bot.get_channel(channel_id)
            await ctx.send(f"你已移除直播通知頻道")
            print(f" YoutubeLiveChannelRemove: {ctx.guild.id} / None")
        else:
            await ctx.send("此伺服器並沒有設定直播通知頻道 請先用`hkv!setup`設定")

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
            await ctx.send("只有開發者能使用此指令")

    @commands.Cog.listener()
    async def on_command(self,ctx):
        text = "[{}] {} 執行 {}{} 指令 ".format(ctx.guild.name,ctx.author.display_name,ctx.prefix,ctx.command.name)
        print(text)


    @tasks.loop(minutes=2)
    async def changePresence(self):
        choices = [f"{len(self.bot.guilds)} 個伺服器 | hkv!setup",f"{len(self.bot.users)} 個用戶 |hkv!setup",f"{self.Version} | miru!setup"]
        choice = choices[self.count]
        print(choice)
        if self.count == len(choices)-1:
            self.count = 0
        else:
            self.count += 1
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=choice))

def setup(bot):
    bot.add_cog(main(bot))
