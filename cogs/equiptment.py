from discord import Embed, Interaction, ButtonStyle, SelectOption
from discord.ui import View, button, Button, select, Select
from slash_util import Cog, slash_command, Context
import json

from database import get_user
from utils import Data, Default, Color, Icon, Paginator, Weapon, Armor


class Use_select(Select):
	def __init__(self, user, items):
		self.user = user
		self.items = items

		super().__init__(placeholder="Use", min_values=1, max_values=1, options=self.items, row=2)

	async def callback(self, interaction : Interaction):
		if (json.loads(self.values[0])['name'] in Data.fetch_names('weapons')):
			new_value = Weapon(**json.loads(self.values[0]))

			new_equiptment = self.user.equiptment
			new_equiptment.pop(new_equiptment.index(new_value))

			if (self.user.weapon): new_equiptment.append(self.user.weapon)

			current_weapon_strength = self.user.weapon.power if (self.user.weapon) else 0
			new_strength = (self.user.strength - current_weapon_strength) + new_value.power
			
			self.user.update(weapon=new_value, equiptment=new_equiptment, strength=new_strength)

			new_strength_status = Icon.increase if (new_strength >= self.user.strength) else Icon.decrease

			await interaction.response.send_message(f"Equipped {new_value.icon} {new_value.name} `({new_value.rarity})`\n{Icon.strength} Strength: {new_strength} ({new_strength_status}{new_value.power}{new_strength_status})", ephemeral=True)
		
		else: await interaction.response.send_message("soon", ephemeral=True)

		self.view.stop()


class Unequip_weapon(Button):
	def __init__(self, user):
		self.user = user

		super().__init__(label="Unequip weapon", style=ButtonStyle.red, row=3)

	async def callback(self, interaction : Interaction):
		weapon = self.user.weapon

		new_equiptment = self.user.equiptment
		new_equiptment.append(weapon)

		new_strength = self.user.strength - weapon.power

		self.user.update(equiptment=new_equiptment, weapon=None, strength=new_strength)

		await interaction.response.send_message(f"Unequippted {weapon.icon} {weapon.name} `({weapon.rarity})`\n{Icon.strength} Strength: {new_strength} ({Icon.decrease}{weapon.power}{Icon.decrease})", ephemeral=True)

		self.view.stop()

class Unequip_armor(Button):
	def __init__(self, user):
		self.user = user

		super().__init__(label="Unequip armor", style=ButtonStyle.red, row=3)

	async def callback(self, interaction : Interaction):
		await interaction.response.send_message("soon", ephemeral=True)

		self.view.stop()


class Equiptment(Cog):
	def __init__(self, bot):
		self.bot = bot


	@slash_command()
	async def equiptment(self, ctx : Context):
		user = get_user(ctx.author.id)

		if (len(user.equiptment) <= 0):
			await ctx.send("empty", ephemeral=True)
			return

		pages = []; items = []
		embed = Embed(title="Equiptment", color=Color.default)
		for i, item in enumerate(user.equiptment):
			items.append(SelectOption(label=item['name'], description=item['rarity'], value=json.dumps(item)))

			if ('power' in item.keys()): item_stats = f"```\nHealth: {item['health']}\nPower: {item['power']}\n```" 
			if ('defence' in item.keys()): item_stats = f"```\nHealth: {item['health']}\nDefence: {item['defence']}\n```"

			embed.add_field(name=f"{item['icon']} {item['name']} `({item['rarity']})`", value=item_stats, inline=True)

			if ((i + 1 in [5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100]) or (i + 1 >= len(user.equiptment))):
				pages.append(embed)
				embed = Embed(title="Equiptment", color=Color.default)

		assert (pages and items)

		custom_buttons = [Use_select(user, items)]
		if (user.weapon): custom_buttons.append(Unequip_weapon(user))
		if (user.armor): custom_buttons.append(Unequip_armor(user))

		await Paginator(ctx, pages, custom_buttons).start(True)


def setup(bot):
	bot.add_cog(Equiptment(bot))