from discord import Interaction, SelectOption, User, ButtonStyle
from discord.ui import View, select, Select, button, Button
from typing import Optional, List
from slash_util import Context


current_page = 0


class _select(Select):
	def __init__(self, pages: List[str]):
		super().__init__(placeholder="Quick navigation", min_values=1, max_values=1, options=pages, row=0)


	async def callback(self, interaction: Interaction):
		global current_page
		current_page = int(self.values[0])

		self.view.stop()

class _view(View):
	def __init__(self, author: User, pages: List[SelectOption]):
		super().__init__()
		self.author = author
		self.pages = pages
		self.quit = False

	async def interaction_check(self, interaction: Interaction) -> bool:
		return (interaction.user.id == self.author.id)

	async def on_timeout(self):
		self.quit = True


	@button(label="◀◀", style=ButtonStyle.gray, row=1)
	async def first(self, button: Button, interaction: Interaction):
		global current_page
		current_page = 0

		self.stop()


	@button(label="◀", style=ButtonStyle.blurple, row=1)
	async def previous(self, button: Button, interaction: Interaction):
		global current_page
		current_page -= 1

		self.stop()

	@button(label="▶", style=ButtonStyle.blurple, row=1)
	async def next(self, button: Button, interaction: Interaction):
		global current_page
		current_page += 1

		self.stop()

	@button(label="▶▶", style=ButtonStyle.gray, row=1)
	async def last(self, button: Button, interaction: Interaction):
		global current_page
		current_page = len(self.pages) - 1

		self.stop()

	@button(label="Quit", style=ButtonStyle.red, row=1)
	async def quit(self, button: Button, interaction: Interaction):
		self.quit = True

		self.stop()


class Paginator:
	def __init__(self, ctx: Context, pages: list, current_page: Optional[int] = 0):
		self.ctx = ctx
		self.pages = pages
		self.current_page = current_page


	async def start(self, embeded: Optional[bool] = False):
		assert (self.pages)

		global current_page
		current_page = self.current_page or current_page

		msg = await self.ctx.send("Loading...")

		while True:
			view = _view(self.ctx.author, self.pages)

			minus_disabled = True if (current_page <= 0) else False
			plus_disabled = True if (current_page + 1 >= len(self.pages)) else False

			view.first.disabled = minus_disabled
			view.previous.disabled = minus_disabled
			view.last.disabled = plus_disabled
			view.next.disabled = plus_disabled

			options = []
			for index, page in enumerate(self.pages):
				options.append(SelectOption(label=index+1, value=index))

			view.add_item(_select(options))

			await msg.edit(content=self.pages[current_page], view=view) if not (embeded) else await msg.edit(content=""
				, embed=self.pages[current_page], view=view)
			await view.wait()

			if (view.quit): break

		await msg.delete()