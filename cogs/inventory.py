from slash_util import Cog, slash_command, Context
from discord import Embed, Interaction, ButtonStyle
from discord.ui import View, button, Button

from database import get_user
from utils import Default, Color


page = 1

class Paginator(View):
	def __init__(self, author):
		super().__init__()
		self.author = author
		self.quit = False

	async def interaction_check(self, interaction: Interaction) -> bool:
		return (interaction.user.id == self.author.id)

	async def on_timeout(self):
		self.quit = True
		self.stop()


	@button(label="Previous", style=ButtonStyle.blurple)
	async def previous(self, button : Button, interaction : Interaction):
		global page
		page -= 1
		self.stop()

	@button(label="Next", style=ButtonStyle.blurple)
	async def next(self, button : Button, interaction : Interaction):
		global page
		page += 1
		self.stop()


class Inventory(Cog):
	def __init__(self, bot):
		self.bot = bot


	@slash_command(guild_id=Default.test_server)
	async def inventory(self, ctx : Context):
		user = get_user(ctx.author.id)

		embed = Embed(title="Inventory", color=Color.default)

		global page

		if not (len(user.inventory) >= 1):
			embed.description = "empty"

			await ctx.send(embed=embed)
			return

		msg = await ctx.send("Loading...")
		page_max = 5

		while True:
			embed.description = ""

			page_max_multiples = [n for n in range(page * page_max, len(user.inventory)) if n % page_max == 0]

			for index, item in enumerate(user.inventory):
				if page_max_multiples != []:
					if (index == page_max_multiples[-1]): break

				embed.description += f"{index + 1}. {item.icon} {item.name} `({item.amount})`\n"

			embed.set_footer(text=f"Page: {page}/{round(len(user.inventory) / page_max)}")

			view = Paginator(ctx.author)
			view.next.disabled = True if ((page * page_max) >= len(user.inventory)) else False
			view.previous.disabled = True if (page <= 1) else False

			await msg.edit(content="", embed=embed, view=view)
			await view.wait()

			if (view.quit): break

		await msg.delete()


def setup(bot):
	bot.add_cog(Inventory(bot))