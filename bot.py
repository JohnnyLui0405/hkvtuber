import discord
import os
from discord.ext import commands
from decouple import config

intents = discord.Intents.all()
bot = commands.Bot(command_prefix= 'hkv!', intents=intents)

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

if __name__ == "__main__":
    bot.run("ODQxODk5OTYxNzM4MTk5MDUx.YJtecA.Hddddztg7lIQFqfCS-qwPVZgT0A")
#Nzk1MTkyNzE3MzAyMzAwNzIy.X_Fy7Q.-Abr1W-5Xfuy3cthNHRYx0Q3VmM