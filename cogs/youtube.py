import discord
import json
import pytz
import requests
from datetime import datetime
from discord.ext import commands,tasks
from pymongo import MongoClient
from decouple import config
from requests_html import AsyncHTMLSession
from bs4 import BeautifulSoup as bs


client = MongoClient(config("mongodb"))
db = client.HKVTuber
collection = db.data
class youtube(commands.Cog):


    def __init__(self, bot):
        """Youtube Notification"""
        self.bot = bot
        self.streaming = False
        self.VideosData = []
        self.oldVideosData = None
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("IPv4: " + requests.get("https://api.ipify.org").text)
        self.is_live.start()

    async def live_send(self, video, update_time): #發送直播通知
        url = "https://www.youtube.com/watch?v={}".format(video["videoId"])
        guilds = db.channel.find({})
        for guild in guilds:
            try:
                if video["channelUrl"].split("/channel/")[1] in guild["YTChannels"] or guild["YTChannels"] == all:
                    channel_id = guild["channel_id"]
                    if not channel_id == None:
                        channel = self.bot.get_channel(channel_id)
                        embed=discord.Embed(title=video["title"], description=f"[{video['channelTitle']}]({video['channelUrl']})", url=url, color=0xdb0000)
                        embed.add_field(name="直播狀態", value="直播中", inline=True)
                        embed.set_footer(text=f"更新於 {self.upcomingtime(int(update_time))}")
                        embed.set_image(url=video["thumbnail"])
                        await channel.send(embed=embed)
            except Exception as e:
                print(e)

    async def upcoming_send(self, video, update_time):
        url = "https://www.youtube.com/watch?v={}".format(video["videoId"])
        guilds = db.channel.find({})
        for guild in guilds:
            try:
                if video["channelUrl"].split("/channel/")[1] in guild["YTChannels"] or guild["YTChannels"] == "all":
                    print(True)
                    channel_id = guild["channel_id"]
                    if not channel_id == None:
                        channel = self.bot.get_channel(channel_id)
                        embed=discord.Embed(title=video["title"], description=f"[{video['channelTitle']}]({video['channelUrl']})", url=url, color=0x636363)
                        embed.add_field(name="直播狀態", value="預定", inline=True)
                        embed.add_field(name="預定開台時間", value=self.upcomingtime(int(video["upcoming"])), inline=True)
                        embed.set_footer(text=f"更新於 {self.upcomingtime(int(update_time))}")
                        embed.set_image(url=self.bigpicture(video["thumbnail"]))
                        await channel.send(embed=embed)
            except Exception as e:
                print(e)


    async def video_send(self): #發送影片通知
        video_url = "https://www.youtube.com/watch?v={}".format(self.VideosData[0][1])
        # request = self.video_service.videos().list(part='liveStreamingDetails',id=self.VideosData[0][1])
        # response = request.execute()
        # try:
        #     ScheduledTime = response["items"][0]["liveStreamingDetails"]["scheduledStartTime"]
        # except KeyError:
        #     ScheduledTime = None
        for guild in self.bot.guilds:
            try:
                channel_id = collection.find_one({"_id": guild.id})["YoutubeVideoChannelId"]
                if not channel_id == None:
                    channel = self.bot.get_channel(channel_id)
                    await channel.send(f"{guild.default_role} 老大發精神糧食了 快去看 \n {video_url}")
            except Exception as e:
                print(e)
        print(f"New Video {video_url}")

    def bigpicture(self, url):
        url = url.split("hqdefault")
        newurl = url[0] + "maxresdefault.jpg"
        return newurl

    def upcomingtime(self,ts):
        LQ = datetime.fromtimestamp(ts).astimezone(pytz.timezone("Asia/Hong_Kong")).strftime('%p')
        if LQ == "AM":
            LQ = "上午"
        elif LQ == "PM":
            LQ = "下午"
        time = datetime.fromtimestamp(ts).astimezone(pytz.timezone("Asia/Hong_Kong")).strftime(f'%Y/%m/%d {LQ}%I:%M:%S')
        return time

    def isNewStream(self, videoId):
        for i in self.LiveData["streaming"]:
            if i["videoId"] == videoId:
                return False
        return True

    def isNewUpcome(self, videoId):
        for i in self.LiveData["upcoming"]:
            if i["videoId"] == videoId:
                return False
        return True

    def isNewVideo(self):
        if self.oldVideosData == None:
            return False
        if (self.oldVideosData[0][0] == self.VideosData[0][0]) and (self.oldVideosData[0][1] == self.VideosData[0][1]):
            return False
        return True

    def isStream(self,items):
        for video in items:
            if "watching" in video["text"] or "正在觀看" in video["text"]:
                return True
        return False

    def isUpcome(self,items):
        for video in items:
            if "waiting" in video["text"] or "正在等候" in video["text"]:
                return True
        return False



    # @tasks.loop(minutes=15)
    # async def is_live(self): #檢查是否在直播
    #     print(True)
    #     request = self.service.search().list(part='snippet',channelId="UCFahBR2wixu0xOex84bXFvg",type="video",eventType="live")
    #     response = request.execute()
    #     if response["pageInfo"]["totalResults"] != 0 and self.streaming == False:
    #         self.streaming = True
    #         self.liveId = response['items'][0]['id']['videoId']
    #         await self.video_send()
    #         self.is_live.change_interval(hours=1)
    #     if response["pageInfo"]["totalResults"] == 0:
    #         self.streaming = False
    #         self.is_live.change_interval(minutes=10)
    @tasks.loop(minutes=2)
    async def is_live(self):
        r = requests.get("https://vtuber.hk/data/live.json?t=")
        videodata = r.json()
        with open('./json/data.json', mode="w") as jfile:
            json.dump(videodata, jfile)
        with open('./json/videoId.json', mode="r") as jfile:
            data = json.load(jfile)
        newdata = {"Streaming":[],"Upcoming":[]}
        for video in videodata["videos"]:
            if video["status"] == "live":
                newdata["Streaming"].append(video["videoId"])
                if (not video["videoId"] in data["Streaming"]):
                    print(video["videoId"] + " is Streaming")
                    await self.live_send(video, videodata["updateTime"])

            elif video["status"] == "upcoming":
                newdata["Upcoming"].append(video["videoId"])
                if (not video["videoId"] in data["Upcoming"]):
                    print(video["videoId"] + " is Upcoming")
                    await self.upcoming_send(video, videodata["updateTime"])

        with open('./json/videoId.json', mode="w") as jfile:
            json.dump(newdata, jfile)
        


    @tasks.loop(minutes=2)
    async def VideoUpload(self):
        self.oldVideosData = collection.find_one({"_id": "LiveData"})["VideoData"]
        request = self.video_service.playlistItems().list(part='snippet',playlistId="PLHHwxaEhb01Py-10Fsi3cp3KDmtoi5S_f")
        # PLHHwxaEhb01Py-10Fsi3cp3KDmtoi5S_f
        # UUFahBR2wixu0xOex84bXFvg
        response = request.execute()
        i = 0
        titles = []
        videoids = []
        while i < len(response["items"]):
            titles.append(response["items"][i]["snippet"]["title"])
            videoids.append(response["items"][i]["snippet"]["resourceId"]["videoId"])
            i += 1
        self.VideosData = []
        for title in titles:
            tempList = []
            tempList.append(title)
            tempList.append(videoids[titles.index(title)])
            self.VideosData.append(tempList)
        if not self.isNewVideo():
            self.oldVideosData = self.VideosData
        else:
            await self.video_send()
            self.oldVideosData = self.VideosData
        collection.update_one({"_id": "LiveData"},{"$set": {"VideoData": self.oldVideosData}})

    @commands.command()
    async def reboot(self,ctx,function=None):
        if ctx.author.id == 334534960654450690:
            if function == "islive":
                self.is_live.start()
                await ctx.send("已重新啟動islive")
        else:
            await ctx.send("You have no permission to use this command")

    @commands.command()
    async def check(self,ctx):
        if ctx.author.id == 334534960654450690:
            await ctx.send(f"is_live {self.is_live.is_running()}")
            await ctx.send(f"VideoUpload {self.VideoUpload.is_running()}")
        else:
            await ctx.send("You have no permission to use this command")

    # @commands.command()
    # @commands.cooldown(1, 5, commands.BucketType.user)
    # async def upcoming(self,ctx):
    #     upcoming = self.LiveData["upcoming"]
    #     for List in upcoming:
    #         url = "https://www.youtube.com/watch?v={}".format(List["videoId"])
    #         embed=discord.Embed(title=List["title"], url=url, color=0xdb0000)
    #         embed.add_field(name="直播狀態", value="預定", inline=True)
    #         embed.add_field(name="排定開台時間", value=self.upcomingtime(int(List["starttime"])), inline=True)
    #         embed.set_image(url=List["imageurl"])
    #         await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self,ctx,error):
        print(error.text)
        if isinstance(error, commands.CommandOnCooldown):
            text = "請在 `{}` 秒後重試".format(int(error.retry_after))
            await ctx.send(text)
        



            

def setup(bot):
    bot.add_cog(youtube(bot))