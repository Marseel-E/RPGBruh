from discord.enums import ButtonStyle
from slash_util import Cog, slash_command, Context
from discord import Embed, Interaction, ButtonStyle, User as DUser
from discord.ui import View, Button, button
from random import randint

from utils import *
from database import *


from pydantic import BaseModel

class Dual(BaseModel):
	player_1 : User
	player_2 : User
	winner   : Optional[User] = None
	turn     : Optional[User] = None
	bet      : Optional[int] = 0

	class Config:
		arbitary_types_allowed = True


class Ask_to_play(View):
	def __init__(self, author):
		super().__init__()
		self.author = author
		self.accept = False

	async def interaction_check(self, interaction: Interaction):
		if (self.author.in_dual):
			await interaction.response.send_message("Your opponent is in another dual currently", ephemeral=True)
			return False

		return (str(interaction.user.id) == self.author.ID)


	@button(label="Accept", style=ButtonStyle.green)
	async def accept(self, button : Button, interaction : Interaction):
		self.accept = True
		self.stop()

	@button(label="Deny", style=ButtonStyle.red)
	async def deny(self, button : Button, interaction : Interaction):
		self.stop()


class Dual_slash(Cog):
	def __init__(self, bot):
		self.bot = bot


	@slash_command(guild_id=Default.test_server)
	async def dual(self, ctx : Context, member : DUser, bet : int = 0):
		player = get_user(ctx.author.id)
		opponent = get_user(member.id)

		if (player.in_dual):
			await ctx.send("You are in another dual currently", ephemeral=True)
			return

		view = Ask_to_play(opponent)
		msg = await ctx.send(f"{member.mention}, `{ctx.author}` invited you to a dual for :coin: {bet}", view=view)
		await view.wait()

		if not (view.accept):
			await msg.delete()
			await ctx.send(f"{ctx.author.mention}, `{member}` denied your request", ephemeral=True)
			return

		bet = 0 if ((player.coins < bet) or (opponent.coins < bet)) else bet

		player.update(in_dual=True, coins=player.coins - bet)
		opponent.update(in_dual=True, coins=opponent.coins - bet)

		dual = Dual(player_1=player, player_2=opponent, bet=bet * 2, turn=player)
		defender = opponent

		while True:
			strength = randint(round(dual.turn.strength / 2), dual.turn.strength)
			defence = randint(round(defender.defence / 2), defender.defence)

			attack = strength - defence
			defender.update(health=defender.health - attack)

			if (defender.health <= 0): break

			# turn switch
			if (dual.turn.ID == player.ID):
				dual.turn = opponent
				defender = player
			else:
				dual.turn = player
				defender = opponent

		exp_amount = randint(1,30) * dual.turn.level

		dual.turn.update(exp=exp_amount, health=100, in_dual=False, coins=dual.turn.coins + dual.bet)
		defender.update(health=100, in_dual=False)

		winner = await self.bot.fetch_user(int(dual.turn.ID))

		await msg.delete()
		await ctx.send(f":tada: {winner.mention} WON! :tada:\n+ :coins: {dual.bet}\n+ {exp_amount} Experience")


def setup(bot):
	bot.add_cog(Dual_slash(bot))