import os
from discord import Intents, Status, Game
from slash_util import Bot

from dotenv import load_dotenv
load_dotenv('.env')


intents = Intents.default()
bot = Bot(command_prefix=".", case_sensitive=True, intents=intents, help_command=None)

@bot.event
async def on_ready():
	await bot.change_presence(status=Status.online, activity=Game("codeBot.exe"))


@bot.event
async def on_message(message):
	await bot.process_commands(message)


if __name__ == ('__main__'):
	for file in os.listdir("cogs"):
		if file.endswith(".py"):
			try: bot.load_extension(f"cogs.{file[:-3]}")
			except Exception as e: print(f"[Main]: Failed to load '{file[:-3]}': {e}\n")
			else: print(f"[{file[:-3]}]: Loaded..\n")


bot.run(os.environ.get("DEV_TOKEN"))