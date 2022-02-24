from slash_util import Cog, slash_command, Context, Modal, TextInput, TextInputStyle
from discord import Embed, Interaction, ButtonStyle, SelectOption, interactions
from discord.ui import View, button, Button, select, Select
from asyncio import TimeoutError
import json

from database import get_user, Global_Marketplace, MarketplaceItem 
from utils import get_weapons_names, Weapon, Armor, Default, Color, Icon


class Buy_sell(View):
	def __init__(self, author, message):
		super().__init__()
		self.author = author
		self.message = message
		self.value = None

	async def interaction_check(self, interaction: Interaction):
		return (interaction.user.id == self.author.id)

	async def on_timeout(self): self.stop()


	@button(label="Buy", style=ButtonStyle.green)
	async def buy(self, button : Button, interaction : Interaction):
		self.value = "buy"
		self.stop()

	@button(label="Sell", style=ButtonStyle.red)
	async def sell(self, button : Button, interaction : Interaction):
		self.value = "sell"
		self.stop()


page = 1

class Sell_select(Select):
	def __init__(self, user, items):
		self.user = user
		self.items = items

		super().__init__(placeholder="Select item", min_values=1, max_values=1, options=self.items)

	async def callback(self, interaction : Interaction):
		modal = Modal(title="Set a price", items=[TextInput(label="price", style=TextInputStyle.short, default_value=0, placeholder="0", custom_id="price")])
		await interaction.response.send_modal(modal)

		try: interaction = await modal.wait(timeout=120.0)
		except TimeoutError:
			await interaction.response.send_message("You didn't respond in time.", ephemeral=True)
			self.view.on_timeout()
			return
		else: data = modal.response

		if (json.loads(self.values[0])['name'] in get_weapons_names()): new_value = Weapon(**json.loads(self.values[0]))
		else: new_value = Armor(**json.loads(self.values[0]))

		new_equiptment = self.user.equiptment
		new_equiptment.pop(new_equiptment.index(new_value))
		
		self.user.update(equiptment=new_equiptment)

		new_items = Global_Marketplace.items
		new_items.append(MarketplaceItem(user=self.user, data=new_value, price=int(data['price'])))

		Global_Marketplace.update(items=new_items)

		await interaction.response.send_message(f"Listed {new_value.icon} {new_value.name} `({new_value.rarity})` for {Icon.coins} {data['price']}", ephemeral=True)

		self.view.stop()

class Buy_select(Select):
	def __init__(self, user, items, items_data, bot):
		self.user = user
		self.items = items
		self.items_data = items_data
		self.bot = bot

		super().__init__(placeholder="Select item", min_values=1, max_values=1, options=self.items)

	async def callback(self, interaction : Interaction):
		new_value = self.items_data[int(self.values[0])]

		if (self.user.coins < new_value.price):
			await interaction.response.send_message("You don't have enough coins to buy this item.", ephemeral=True)
			return

		new_equiptment = self.user.equiptment
		new_equiptment.append(new_value.data)

		self.user.update(coins=self.user.coins - new_value.price, equiptment=new_equiptment)

		new_items = Global_Marketplace.items
		new_items.pop(Global_Marketplace.items.index(new_value))

		new_value.user.update(coins=new_value.user.coins + new_value.price)

		Global_Marketplace.update(items=new_items)

		item_user = await self.bot.fetch_user(int(new_value.user.ID))
		author_user = await self.bot.fetch_user(int(self.user.ID))

		await item_user.send(f"{author_user} bought your {new_value.data.icon} {new_value.data.name} `({new_value.data.rarity})` for {Icon.coins} {new_value.price}")

		await interaction.response.send_message(f"Bought {item_user.display_name}'s {new_value.data.icon} {new_value.data.name} `({new_value.data.rarity})` for {Icon.coins} {new_value.price}", ephemeral=True)

		self.view.stop()

class Select_item(View):
	def __init__(self, author):
		super().__init__()
		self.author = author

	async def interaction_check(self, interaction: Interaction):
		return (interaction.user.id == self.author.id)

	async def on_timeout(self): self.stop()


class Marketplace(Cog):
	def __init__(self, bot):
		self.bot = bot


	@slash_command(guild_id=Default.test_server)
	async def marketplace(self, ctx : Context):
		embed = Embed(title="Marketplace", color=Color.default)

		if (len(Global_Marketplace.items) >= 1):
			for item in Global_Marketplace.items:
				if ('power' in item.data.dict().keys()): power_or_defence = f"Power: {item.data.power}"
				else: power_or_defence = f"Defence: {item.data.defence}"

				item_user = await self.bot.fetch_user(int(item.user.ID))
				embed.add_field(name=f"{item.data.icon} {item.data.name} `({item.data.rarity})` {Icon.coins} {item.price}", value=f"```\nHealth: {item.data.health}\n{power_or_defence}\n```By: **{item_user}**", inline=False)

		if (len(embed.fields) <= 0): embed.description = "nothing to buy/sell"

		user = get_user(ctx.author.id)

		if not (len(user.equiptment) >= 1):
			await ctx.send(embed=embed)
			return

		msg = await ctx.send("Loading...")

		view = Buy_sell(ctx.author, msg)
		await msg.edit(content="", embed=embed, view=view)
		await view.wait()

		await msg.delete()
		msg = await ctx.send("Loading...")

		if view.value == "sell":
			user_items = []
			for item in user.equiptment:
				user_items.append(SelectOption(label=item['name'], description=item['rarity'], value=json.dumps(item)))

			view = Select_item(ctx.author)
			view.add_item(Sell_select(user, user_items))

			await msg.edit(embed=embed, view=view)
			await view.wait()
			await msg.delete()
			return

		if view.value == "buy":
			marketplace_items = []
			items_data = []
			extra_index = 0

			for item in Global_Marketplace.items:
				if (int(item.user.ID) == ctx.author.id):
					extra_index += 1
					continue

				item_user = await self.bot.fetch_user(int(item.user.ID))
				marketplace_items.append(SelectOption(label=f"{item.data.name} ({item.data.rarity})", description=f"Price: {item.price}\nBy: {item_user}", value=Global_Marketplace.items.index(item) - extra_index))
				items_data.append(item)

			view = Select_item(ctx.author)
			content = ""

			if (len(marketplace_items) >= 1): view.add_item(Buy_select(user, marketplace_items, items_data, self.bot))
			else: content = "There's nothing to buy."

			await msg.edit(content=content, embed=embed, view=view)
			await view.wait()
			await msg.delete()
			return


def setup(bot):
	bot.add_cog(Marketplace(bot))