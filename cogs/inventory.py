from slash_util import Cog, slash_command, Context
from discord import Embed, Interaction, ButtonStyle, SelectOption
from discord.ui import View, button, Button, select, Select

from database import *
from utils import *


class Inv(Cog):
	def __init__(self, bot):
		self.bot = bot


	@slash_command(guild_id=Default.test_server)
	async def inventory(self, ctx : Context):
		user = get_user(ctx.author.id)
		embed = Embed(title="Inventory", color=Color.default)

		if (len(user.inventory) > 0):
			for item in user.inventory:
				if ('power' in item.keys()): item_stats = f"```\nHealth: {item['health']}\nPower: {item['power']}\n```" 
				if ('defence' in item.keys()): item_stats = f"```\nHealth: {item['health']}\nDefence: {item['defence']}\n```"

				embed.add_field(name=f"{item['icon']} {item['name']} `({item['rarity']})`", value=item_stats)
		
		else: embed.description = "empty"

		await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(Inv(bot))