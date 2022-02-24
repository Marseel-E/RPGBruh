from slash_util import Cog, slash_command, Context, Modal, TextInput, TextInputStyle
from discord.ext.commands import cooldown, cooldowns
from datetime import datetime, timedelta
from random import choices, randint
from humanize import precisedelta
from asyncio import TimeoutError
from discord import Embed

from database import get_user
from utils import Default, generate_equation, Item, all_items


class Mine(Cog):
	def __init__(self, bot):
		self.bot = bot


	@slash_command(guild_id=Default.test_server)
	async def mine(self, ctx : Context):
		user = get_user(ctx.author.id)

		if (datetime.utcnow() < user.mine_cooldown):
			await ctx.send(f"Try again in {precisedelta(user.mine_cooldown - datetime.utcnow())}", ephemeral=True)
			return

		right_answer, equation = generate_equation()

		modal = Modal(title="Mine", items=[TextInput(label=equation, custom_id="answer", placeholder="answer", style=TextInputStyle.short, required=False)])

		await ctx.send(modal=modal)

		try: interaction = await modal.wait(timeout=30.0)
		except TimeoutError:
			await ctx.send("You didn't respond in time.", ephemeral=True)
			user.update(mine_cooldown=datetime.utcnow() + timedelta(minutes=5))
			return
		else: answer = modal.response['answer']

		if ((answer == '') or (not (answer.isnumeric()) and not (answer.startswith('-'))) or (int(answer) != right_answer)):
			await interaction.response.send_message(f"Wrong answer!", ephemeral=True)
			user.update(mine_cooldown=datetime.utcnow() + timedelta(minutes=5))
			return

		ores_data = {
			'stone': 50.0,
			'copper': 25.0,
			'iron': 12.5,
			'gold': 6.25,
			'ruby': 3.125,
			'sapphire': 1.5625,
			'emerald': 0.78125
		}

		ores = set(choices(list(ores_data.keys()), weights=list(ores_data.values()), k=randint(1,3)))

		text = ""
		new_inv = user.inventory
		for ore in ores:
			random_amount = round(randint(5,15) / (list(ores_data.keys()).index(ore) + 1))

			if (len(user.inventory) >= 1):
				for item in user.inventory:
					if item.name == ore:
						amount = (random_amount + item.amount)
						new_inv.pop(new_inv.index(item))
						break

			icon = all_items['items'][ore]

			new_inv.append(Item(name=ore, icon=icon, amount=amount));

			text += f"+ `{random_amount}` {icon} {ore}\n"

		exp = randint(10,30)
		user.update(inventory=new_inv, exp=user.exp + exp, mine_cooldown=datetime.utcnow() + timedelta(minutes=5))

		await interaction.response.send_message(f"Correct!\nExp: +{exp}\n{text}", ephemeral=True)


def setup(bot):
	bot.add_cog(Mine(bot))