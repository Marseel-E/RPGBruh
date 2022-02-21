import discord
from discord.ext.commands import Cog, command, is_owner
from discord import Embed
import traceback, sys, os
from io import StringIO
from typing import Optional, Literal, List

from discord.message import DeletedReferencedMessage

from database import *
from utils import *


class Developer(Cog):
	def __init__(self, bot):
		self.bot = bot


	async def cog_check(self, ctx):
		return (await self.bot.is_owner(ctx.author))


	@command(hidden=True, aliases=['python', 'eval', 'ev'])
	async def py(self, ctx, unformatted : Optional[bool], *, cmd):
		try: await ctx.message.delete()
		except: pass

		old_stdout = sys.stdout
		redirected_output = sys.stdout = StringIO()
		
		try: exec(str(cmd))
		except Exception as e:
			traceback.print_stack(file=sys.stdout)
			print(sys.exc_info())

		sys.stdout = old_stdout
		
		if (unformatted):
			msg = str(redirected_output.getvalue())
			msg = [await ctx.send(msg[i:i+2000]) for i in range(0, len(msg), 2000)]
		
		else:
			msg = str(redirected_output.getvalue())
			
			for i in range(0, len(msg), 2048):

				embed = Embed(description=f"Input:\n```py\n{cmd}\n```\nOutput:\n```bash\n{msg[i:i+2000]}\n```", color=Color.default)
				await ctx.send(embed=embed)


	@command(aliases=['few'])
	async def force_equip_weapon(self, ctx, weapon : str, rarity : str, power : int, health : Optional[int] = 100, member : Optional[discord.User] = None):
		if not (weapon in get_weapons_names()):
			await ctx.send(f"Not a weapon, {weapon}", delete_after=15)
			return

		discord_user = ctx.author if not (member) else member
		
		user = get_user(discord_user.id)
		new_weapon = Weapon(name=weapon, rarity=rarity, power=power, health=health)
		user.update(weapon=new_weapon, strength=user.strength + new_weapon.power)

		await ctx.send(f"Given `{weapon} ({rarity})` to `{discord_user}`", delete_after=15)

	@command(aliases=['fuw'])
	async def force_unequip_weapon(self, ctx, weapon : str, member : Optional[discord.User] = None):
		if not (weapon in get_weapons_names()):
			await ctx.send(f"Not a weapon {weapon}", delete_after=15)
			return

		discord_user = ctx.author if not (member) else member

		user = get_user(discord_user.id)
		user.update(strength=user.strength - user.weapon.power, weapon=None)

		await ctx.send(F"Took `{weapon}` from `{discord_user}`", delete_after=15)


	@command(hidden=True)
	async def load(self, ctx, cog : Optional[str] = None):
		if not (cog):
			for cog in os.listdir("cogs"):
				if not (cog.endswith(".py")) or (cog.startswith("dev")): continue

				try: self.bot.load_extension(f"cogs.{cog[:-3]}")
				except Exception as e: await ctx.author.send(f"[Main]: Failed to load '{cog[:-3]}': {e}")
				else: await ctx.send(f"[{cog[:-3]}]: Loaded..")

			return

		try: self.bot.load_extension(f"cogs.{cog}")
		except Exception as e: await ctx.author.send(f"[Main]: Failed to load '{cog}': {e}")
		else: await ctx.send(f"[{cog}]: Loaded..")

	@command(hidden=True)
	async def unload(self, ctx, cog : Optional[str] = None):
		if not (cog):
			for cog in os.listdir("cogs"):
				if not (cog.endswith(".py")) or (cog.startswith("dev")): continue

				try: self.bot.unload_extension(f"cogs.{cog[:-3]}")
				except Exception as e: await ctx.author.send(f"[Main]: Failed to unload '{cog[:-3]}': {e}")
				else: await ctx.send(f"[{cog[:-3]}]: Unloaded..")

			return

		try: self.bot.unload_extension(f"cogs.{cog}")
		except Exception as e: await ctx.author.send(f"[Main]: Failed to unload '{cog}': {e}")
		else: await ctx.send(f"[{cog}]: Unloaded..")

	@command(hidden=True)
	async def reload(self, ctx, cog : Optional[str] = None):
		if not (cog):
			for cog in os.listdir("cogs"):
				if not (cog.endswith(".py")): continue

				try: self.bot.reload_extension(f"cogs.{cog[:-3]}")
				except Exception as e: await ctx.author.send(f"[Main]: Failed to reload '{cog[:-3]}': {e}")
				else: await ctx.send(f"[{cog[:-3]}]: Reloaded..")

			return

		try: self.bot.reload_extension(f"cogs.{cog}")
		except Exception as e: await ctx.author.send(f"[Main]: Failed to reload '{cog}': {e}")
		else: await ctx.send(f"[{cog}]: Reloaded..")


def setup(bot):
	bot.add_cog(Developer(bot))