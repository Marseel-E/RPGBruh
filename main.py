from discord import Intents, Status, Game
from slash_util import Bot
from random import randint
import os, topgg

from dotenv import load_dotenv
load_dotenv('.env')

from database import fetch_users, get_user
from utils import Icon


intents = Intents.default()
bot = Bot(command_prefix="r-", case_sensitive=True, intents=intents, help_command=None)

@bot.event
async def on_ready():
	print("running")
	await bot.change_presence(status=Status.online, activity=Game("RPGBruh.exe"))


@bot.event
async def on_message(message):
	if (message.author.bot): return

	if bot.user.mentioned_in(message): await message.channel.send("Type `/` and all of RPGBruh's slash commands should appear.\nIf they don't then you have to reinvite the bot, you can do that by pressing on the bot and clicking " + '"Add To Server"' + " and selecting your server. If you're not the server owner please let them know."); return
	
	users = fetch_users()
	if str(message.author.id) in users:
		user = get_user(message.author.id)

		if (user.exp >= (user.level * 4.231) * 100):
			coins = randint(100,1000)

			user.update(exp=0, level=user.level + 1, coins=user.coins + coins, health=100 + (50 * user.level), strength=10 * user.level, defence=10 * user.level)

			await mesasge.channel.send(f"{Icon.level_up} LEVEL UP! {Icon.level_up}\n{Icon.level} Level: {user.level}\n{Icon.coins} Coins: {user.coins}\n{Icon.health} Health: {user.health}\n{Icon.strength} Strength: {user.strength}\n{Icon.defence} Defence: {user.defence}")

	await bot.process_commands(message)



bot.topggpy = topgg.DBLClient(bot, os.environ.get("TOPGG_TOKEN"), autopost=True, post_shard_count=False)

@bot.event
async def on_autopost_success():
	print(f"Posted server count ({bot.topggpy.guild_count}), shard count ({bot.shard_count})")


bot.remove_command("help")
@bot.command(aliases=["?", "h"])
async def help(ctx):
    await ctx.send("Type `/` and all of RPGBruh's slash commands should appear.\nIf they don't then you have to reinvite the bot, you can do that by pressing on the bot and clicking " + '"Add To Server"' + " and selecting your server. If you're not the server owner please let them know.")


if __name__ == ('__main__'):
	for file in os.listdir("cogs"):
		if file.endswith(".py"):
			try: bot.load_extension(f"cogs.{file[:-3]}")
			except Exception as e: print(f"[Main]: Failed to load '{file[:-3]}': {e}\n")
			else: print(f"[{file[:-3]}]: Loaded..\n")

bot.run(os.environ.get("TOKEN"))
