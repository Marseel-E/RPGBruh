import discord
from slash_util import Cog, slash_command, describe, Context

from database.main import *
from utils.tools import *

class Profile_slash(Cog):
	def __init__(self, bot):
		self.bot = bot


	@slash_command(guild_id=Default.test_server)
	@describe(member="View another user's profile")
	async def profile(self, ctx : Context, member : discord.User = None):
		try: await ctx.message.delete()
		except: pass

		discord_user = ctx.author if not member else member
		
		if str(discord_user.id) not in fetch_users():
			if member: await ctx.send('This user has no profile'); return
			else: User(ID=str(discord_user.id), coins=1000).save()

		user = User.find(User.ID == str(discord_user.id)).first()

		embed = discord.Embed(color=int("5261f8", 16))
		embed.set_footer(text=f"Exp: {user.exp} / {round((user.level * 4.231) * 100)}")
		embed.set_thumbnail(url=discord_user.display_avatar)

		embed.add_field(name=":beginner: Level", value=f"{user.level}", inline=False)
		embed.add_field(name=":coin: Coins", value=f"{user.coins}", inline=False)

		embed.add_field(name=":drop_of_blood: Health", value=user.health, inline=False)
		embed.add_field(name=":muscle: Strength", value=user.strength, inline=False)
		embed.add_field(name=":shield: Defence", value=user.defence, inline=False)

		if (user.weapon):
			embed.add_field(name=f"{user.weapon.icon} {user.weapon.name} `({user.weapon.rarity})`", value=f"Health: {user.weapon.health}%\nPower: {user.weapon.power}", inline=False)

		if (user.armor):
			for armor in user.armor:
				embed.add_field(name=f"{armor.icon} {armor.name} `({armor.rarity})`", value=f"Health: {armor.health}%\nDefence: {armor.defence}", inline=False)

		await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(Profile_slash(bot))