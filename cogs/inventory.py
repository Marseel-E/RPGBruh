from slash_util import Cog, slash_command, Context
from discord import Embed, User as DUser

from database import get_user, fetch_users
from utils import Default, Paginator, Color


class _inv(Cog):
	def __init__(self, bot):
		self.bot = bot


	@slash_command()
	async def inventory(self, ctx: Context, member: DUser = None):
		discord_user = ctx.author if not (member) else member

		if ((member) and (str(discord_user.id) in fetch_users())):
			await ctx.send("empty", ephemeral=True)
			return

		user = get_user(discord_user.id)

		if (len(user.inventory) < 1):
			await ctx.send("empty", ephemeral=True)
			return

		pages = []
		content = ""
		for i, item in enumerate(user.inventory):
			content += f"{i+1}. {item.icon} {item.name} `({item.amount})`\n"

			if ((i + 1 in [10,20,30,40,50]) or (i + 1 >= len(user.inventory))):
				embed = Embed(title="Inventory", description=content, color=Color.default)
				pages.append(embed)
				content = ""

		await Paginator(ctx, pages).start(True)


def setup(bot):
	bot.add_cog(_inv(bot))