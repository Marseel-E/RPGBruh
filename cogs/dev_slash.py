from slash_util import Cog, slash_command, Context, Modal, TextInput, TextInputStyle
from discord.ext.commands import is_owner
from discord.enums import DefaultAvatar
from discord import User as DUser
from asyncio import TimeoutError
from typing import Literal
import discord

from database import get_user
from utils import Data, Weapon, Armor, Default


class Dev_slash(Cog):
	def __init__(self, bot):
		self.bot = bot

	async def slash_command_error(self, ctx : Context, error):
		await ctx.send(error, ephemeral=True)


	@slash_command(description="Developer only command")
	@is_owner()
	async def give_item(self, ctx : Context, item_name : str, user : DUser = None):
		items_list = []
		[items_list.append(item) for item in Data.fetch_names('weapons')]
		[items_list.append(item) for item in Data.fetch_names('armor')]

		if not (item_name in items_list):
			await ctx.send(f"{item_name} ain't shit bruh", ephemeral=True)
			return

		modal = Modal(title="Give item", items=[
			TextInput(label="Rarity", custom_id="rarity", required=False, style=TextInputStyle.short, placeholder="rarity", default_value="common"),
			TextInput(label="Icon", custom_id="icon", required=False, style=TextInputStyle.short, placeholder="icon", default_value=":paperclip:"),
			TextInput(label="Health", custom_id="health", required=False, style=TextInputStyle.short, placeholder="health", default_value=100),
			TextInput(label="Power", custom_id="power", required=False, style=TextInputStyle.short, placeholder="power", default_value=10),
			TextInput(label="Defence", custom_id="defence", required=False, style=TextInputStyle.short, placeholder="defence", default_value=10)
		])
		await ctx.send(modal=modal)

		try: interaction = await modal.wait(timeout=120.0)
		except TimeoutError:
			await interaction.response.send_message("You didn't respond in time.", ephemeral=True)
			return
		else: data = modal.response

		if (item_name in get_weapons_names()):
			data.pop('defence')
			item = Weapon(name=item_name, **data)

		else:
			data.pop('power')
			item = Armor(name=item_name, **data)

		discord_user = ctx.author if not (user) else user  
		user = get_user(discord_user.id)

		new_equiptment = user.equiptment
		new_equiptment.append(item)

		user.update(equiptment=new_equiptment)

		assert item in user.equiptment

		await interaction.response.send_message(f"Added {item.icon} {item.name} `({item.rarity})` to `{discord_user}`", ephemeral=True)


	# FIX
	@slash_command()
	@is_owner()
	async def update(self, ctx : Context, member : discord.User = None, page : Literal[1, 2, 3] = 1):
		discord_user = ctx.author if not (member) else member
		user = get_user(discord_user.id)

		fields = []
		for key, value in user.dict().items():
			if (key in ['pk', 'ID']): continue

			short_or_long = TextInputStyle.paragraph if (key in ['equiptment', 'inventory', 'stats', 'armor']) else TextInputStyle.short
			fields.append(TextInput(label=key.capitalize(), style=short_or_long, custom_id=key, required=False, default_value=str(value), placeholder=key))

		modal = Modal(title="Update {discord_user}", items=fields)
		await ctx.send(modal=modal)

		try: interaction = await modal.wait(timeout=600.0)
		except TimeoutError:
			await interaction.response.send_message("didn't respond in time.", ephemeral=True)
			return
		else: data = modal.response

		user.update(**data)

		await interaction.response.send_message(f"```py\n{user}\n```", ephemeral=True)


def setup(bot):
	bot.add_cog(Dev_slash(bot))