from slash_util import Cog, slash_command, describe, Context
import discord

from database import User, fetch_users, get_user
from utils import Default, Icon


class Profile_slash(Cog):
	def __init__(self, bot):
		self.bot = bot


	@slash_command(guild_id=Default.test_server)
	@describe(member="View another user's profile")
	async def profile(self, ctx : Context, member : discord.User = None):
		discord_user = ctx.author if not member else member
		
		if (str(discord_user.id) not in fetch_users()) and (member):
			await ctx.send('This user has no profile')
			return

		user = get_user(discord_user.id)

		embed = discord.Embed(color=int("5261f8", 16))
		embed.set_footer(text=f"Exp: {user.exp} / {round((user.level * 4.231) * 100)}")
		embed.set_thumbnail(url=discord_user.display_avatar)

		embed.add_field(name=f"{Icon.level} Level", value=f"{user.level}", inline=False)
		embed.add_field(name=f"{Icon.coins} Coins", value=f"{user.coins}", inline=False)

		embed.add_field(name=f"{Icon.health} Health", value=user.health)
		embed.add_field(name=f"{Icon.strength} Strength", value=user.strength)
		embed.add_field(name=f"{Icon.defence} Defence", value=user.defence)

		if (user.weapon):
			embed.add_field(name=f"Weapon:\n 	{user.weapon.icon} {user.weapon.name} `({user.weapon.rarity})`", value=f"```\nHealth: {user.weapon.health}%\nPower: {user.weapon.power}\n```", inline=False)

		if (user.armor):
			for armor in user.armor:
				embed.add_field(name=f"Armor:\n 	{armor.icon} {armor.name} `({armor.rarity})`", value=f"```\nHealth: {armor.health}%\nDefence: {armor.defence}```", inline=False)

		await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(Profile_slash(bot))