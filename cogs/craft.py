from discord import Embed, Interaction, ButtonStyle, SelectOption
from discord.ui import View, button, Button, select, Select
from slash_util import Cog, slash_command, Context
from random import randint

from database import get_user
from utils import Default, Color, Data, decide_rarity, Weapon, Armor


class Craft_view(View):
	def __init__(self, author):
		super().__init__()
		self.author = author
		self.category = ""
		self.value = ""

	async def interaction_check(self, interaction: Interaction) -> bool:
		return (interaction.user.id == self.author.id)

	async def on_timeout(self) -> None: self.stop()


	@button(label="Weapons", style=ButtonStyle.blurple)
	async def weapons(self, button: Button, interaction: Interaction):
		self.category = "weapons"
		self.stop()

	@button(label="Armor", style=ButtonStyle.blurple)
	async def armor(self, button: Button, interaction: Interaction):
		self.category = "armor"
		self.stop()


class Type_button(Button):
	def __init__(self, name):
		self.name = name
		super().__init__(label=self.name, style=ButtonStyle.blurple)


	async def callback(self, interaction: Interaction):
		self.view.value = self.name

		self.view.stop()


class Select_item(Select):
	def __init__(self, user, items):
		self.user = user

		super().__init__(placeholder="Craft item", min_values=1, max_values=1, options=items)


	async def callback(self, interaction: Interaction):
		item_data = Data.fetch(self.values[0])
		
		has_items = 0
		for item in self.user.inventory:
			if (item.name in item_data['recipe'].keys()) and (item.amount >= item_data['recipe'][item.name]):
				has_items += 1

		if (has_items < len(item_data['recipe'])):
			await interaction.response.send_message("You don't have enough materials to craft this item.", ephemeral=True)
			return

		new_inv = self.user.inventory

		for name, amount in item_data['recipe'].items():
			for item in new_inv:
				if (item.name == name):
					if (item.amount - amount <= 0):
						new_inv.pop(new_inv.index(item))
						continue
					
					item.amount -= amount
		
		new_equiptment = self.user.equiptment

		if (self.values[0] in Data.fetch_names('weapons')):
			power = randint(item_data['power'][0], item_data['power'][1])
			rarity = decide_rarity(power, item_data['power'][0], item_data['power'][1])
			
			item = Weapon(name=self.values[0], icon=item_data['icon'], power=power, rarity=rarity)
		
		else:
			defence = randint(item_data['defence'][0], item_data['defence'][1])
			rarity = decide_rarity(defence, item_data['defence'][0], item_data['defence'][1])

			item = Armor(name=self.values[0], icon=item_data['icon'], defence=defence, rarity=rarity)

		new_equiptment.append(item)

		exp = randint(10,30)

		self.user.update(inventory=new_inv, equiptment=new_equiptment, exp=exp)

		await interaction.response.send_message(f"Crafted {item.icon} {item.name} `({item.rarity})`\nExp: {exp}", ephemeral=True)

		self.view.stop()


class Craft(Cog):
	def __init__(self, bot):
		self.bot = bot


	@slash_command()
	async def craft(self, ctx: Context):
		user = get_user(ctx.author.id)

		embed = Embed(title="Crafting", color=Color.default)

		view = Craft_view(ctx.author)
		msg = await ctx.send(embed=embed, view=view)
		await view.wait()

		if not (view.category):
			await msg.delete()
			return

		category = view.category

		view = Craft_view(ctx.author)
		view.clear_items()

		item_types = ['sword', 'bow', 'spear', 'axe'] if (category == "weapons") else ['helmet', 'chestplate', 'boots']
		for name in item_types:
			view.add_item(Type_button(name))

		await msg.edit(view=view)
		await view.wait()

		if not (view.value):
			await msg.delete()
			return

		items = []
		for name, data in Data.data[category].items():
			if not (view.value in name.split('_')): continue

			recipe = "```\n"
			for item, amount in data['recipe'].items():
				recipe += f"{amount} {item}\n"

			items.append(SelectOption(label=name, value=name, description=recipe[3:]))

			recipe += "```"

			embed.add_field(name=f"{data['icon']} {name}", value=recipe)

		view = Craft_view(ctx.author)
		view.clear_items()
		view.add_item(Select_item(user, items))

		await msg.edit(embed=embed, view=view)
		await view.wait()


def setup(bot):
	bot.add_cog(Craft(bot))