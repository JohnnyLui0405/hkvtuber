import discord
import os
from discord.ext import commands
from decouple import config

developers = [334534960654450690]
intents = discord.Intents.all()
bot = commands.Bot(command_prefix= 'hkv!', intents=intents)
bot.remove_command('help')

@bot.command()
async def load(ctx, extension):
  if ctx.author.id in developers:
    bot.load_extension(f'cogs.{extension}')
    await ctx.send(f'{ctx.author.mention} 已載入 {extension}')

@bot.command()
async def unload(ctx, extension):
  if ctx.author.id in developers:
    bot.unload_extension(f'cogs.{extension}')
    await ctx.send(f'{ctx.author.mention} 已取消載入 {extension}')

@bot.command()
async def reload(ctx, extension):
  if ctx.author.id in developers:   
    bot.reload_extension(f'cogs.{extension}')
    await ctx.send(f'{ctx.author.mention} 已重新載入 {extension}')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

if __name__ == "__main__":
    bot.run("Nzk1MTkyNzE3MzAyMzAwNzIy.X_Fy7Q.5TVl-g7sP0ky_sSd7wUbmtwx08E")
#Nzk1MTkyNzE3MzAyMzAwNzIy.X_Fy7Q.5TVl-g7sP0ky_sSd7wUbmtwx08E
#ODQxODk5OTYxNzM4MTk5MDUx.YJtecA.7lT3TpGeG9yvPIIraS9y2RgtyJU