from slash_util import Cog, slash_command, Context, Modal, TextInput, TextInputStyle
from discord import Embed, Interaction, ButtonStyle
from discord.ui import View, button, Button
from random import randint, choices, choice
from datetime import datetime, timedelta
from humanize import precisedelta
from asyncio import TimeoutError

from database import get_user
from utils import Default, Data, Icon, Color, Armor, Weapon, Item, Monster


class Backend:
	def __init__(self, bot, ctx):
		self.bot = bot
		self.ctx = ctx
		self.user = get_user(self.ctx.author.id)


	async def gamble_with_traveller(self): await self.ctx.send("soon", ephemeral=True)

	async def monster_fight(self): await self.ctx.send("soon", ephemeral=True)

	async def collect_equiptment(self): await self.ctx.send("soon", ephemeral=True)
	
	async def collect_items(self):
		ores_data = {
			'wood': 50.0,
			'stone': 50.0,
			'copper': 25.0,
			'iron': 12.5,
			'gold': 6.25,
			'ruby': 3.125,
			'sapphire': 1.5625,
			'emerald': 0.78125
		}

		ores = set(choices(list(ores_data.keys()), weights=list(ores_data.values()), k=randint(1,4)))

		text = ""
		new_inv = self.user.inventory
		for ore in ores:
			random_amount = round(randint(5,15) / (list(ores_data.keys()).index(ore) + 1))
			amount = random_amount

			if (len(self.user.inventory) >= 1):
				for item in self.user.inventory:
					if item.name == ore:
						amount += item.amount
						new_inv.pop(new_inv.index(item))
						break

			icon = Data.data['items'][ore]

			new_inv.append(Item(name=ore, icon=icon, amount=amount));

			text += f"+ `{random_amount}` {icon} {ore}\n"

		exp = randint(10,30)
		self.user.update(inventory=new_inv, exp=self.user.exp + exp)

		await self.ctx.send(f"Correct!\nExp: +{exp}\n{text}", ephemeral=True)


class Explore(Cog):
	def __init__(self, bot):
		self.bot = bot


	@slash_command(guild_id=Default.test_server)
	async def explore(self, ctx: Context):
		backend = Backend(self.bot, ctx)

		if (datetime.utcnow() < backend.user.explore_cooldown):
			await ctx.send(f"Try again in {precisedelta(backend.user.explore_cooldown - datetime.utcnow())}", ephemeral=True)
			return

		found = choice(['gamble', 'monster', 'equiptment', 'items'])

		if found == "gamble": await backend.gamble_with_traveller()  # Traveller gamble (black jack)
		if found == "monster": await backend.monster_fight()         # Monster fight
		if found == "equiptment": await backend.collect_equiptment() # Equiptment collect
		if found == "items": await backend.collect_items()           # Items collect

		backend.user.update(explore_cooldown=datetime.utcnow() + timedelta(seconds=0))


def setup(bot):
	bot.add_cog(Explore(bot))