from slash_util import Cog, slash_command, Context, Modal, TextInput, TextInputStyle
from discord.ext.commands import cooldown, cooldowns
from datetime import datetime, timedelta
from random import choices, randint, random
from humanize import precisedelta
from asyncio import TimeoutError
from discord import Embed

from database import get_user
from utils import Default, generate_equation, Item, all_items


class Chop(Cog):
	def __init__(self, bot):
		self.bot = bot


	@slash_command()
	async def chop(self, ctx : Context):
		user = get_user(ctx.author.id)

		if (datetime.utcnow() < user.chop_cooldown):
			await ctx.send(f"Try again in {precisedelta(user.chop_cooldown - datetime.utcnow())}", ephemeral=True)
			return

		right_answer, equation = generate_equation()

		modal = Modal(title="Chop", items=[TextInput(label=equation, custom_id="answer", placeholder="answer", style=TextInputStyle.short, required=False)])

		await ctx.send(modal=modal)

		try: interaction = await modal.wait(timeout=30.0)
		except TimeoutError:
			await ctx.send("You didn't respond in time.", ephemeral=True)
			user.update(chop_cooldown=datetime.utcnow() + timedelta(minutes=5))
			return
		else: answer = modal.response['answer']

		if ((answer == '') or (not (answer.isnumeric()) and not (answer.startswith('-'))) or (int(answer) != right_answer)):
			await interaction.response.send_message(f"Wrong answer!", ephemeral=True)
			user.update(chop_cooldown=datetime.utcnow() + timedelta(minutes=5))
			return

		text = ""
		new_inv = user.inventory

		random_amount = randint(5,15)

		if (len(user.inventory) >= 1):
			for item in user.inventory:
				amount = random_amount

				if item.name == "wood":
					amount += item.amount
					new_inv.pop(new_inv.index(item))
					break

		icon = all_items['items']["wood"]

		new_inv.append(Item(name="wood", icon=icon, amount=amount));

		text += f"+ `{random_amount}` {icon} wood\n"

		exp = randint(10,30)
		user.update(inventory=new_inv, exp=user.exp + exp, chop_cooldown=datetime.utcnow() + timedelta(minutes=5))

		await interaction.response.send_message(f"Correct!\nExp: +{exp}\n{text}", ephemeral=True)


def setup(bot):
	bot.add_cog(Chop(bot))