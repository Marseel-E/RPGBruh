from discord import Interaction, SelectOption, User, ButtonStyle
from discord.ui import View, select, Select, button, Button
from typing import Optional, List, Union
from slash_util import Context


class _select(Select):
	def __init__(self, pages: List[str]):
		super().__init__(placeholder="Quick navigation", min_values=1, max_values=1, options=pages, row=0)


	async def callback(self, interaction: Interaction):
		self.view.current_page = int(self.values[0])

		await self.view.update_children(interaction)


class _view(View):
	def __init__(self, author: User, pages: List[SelectOption], embeded: bool):
		super().__init__()
		self.author = author
		self.pages = pages
		self.embeded = embeded

		self.current_page = 0

	async def interaction_check(self, interaction: Interaction) -> bool:
		return (interaction.user.id == self.author.id)


	async def update_children(self, interaction: Interaction):
		self.next.disabled = True if (self.current_page + 1 == len(self.pages)) else False
		self.previous.disabled = True if (self.current_page <= 0) else False

		kwargs = {'content': self.pages[self.current_page]} if not (self.embeded) else {'embed': self.pages[self.current_page]}
		kwargs['view'] = self

		await interaction.response.edit_message(**kwargs)


	@button(label="◀◀", style=ButtonStyle.gray, row=1)
	async def first(self, button: Button, interaction: Interaction):
		self.current_page = 0

		await self.update_children(interaction)

	@button(label="◀", style=ButtonStyle.blurple, row=1)
	async def previous(self, button: Button, interaction: Interaction):
		self.current_page -= 1

		await self.update_children(interaction)

	@button(label="▶", style=ButtonStyle.blurple, row=1)
	async def next(self, button: Button, interaction: Interaction):
		self.current_page += 1

		await self.update_children(interaction)

	@button(label="▶▶", style=ButtonStyle.gray, row=1)
	async def last(self, button: Button, interaction: Interaction):
		self.current_page = len(self.pages) - 1

		await self.update_children(interaction)


	@button(label="Quit", style=ButtonStyle.red, row=1)
	async def quit(self, button: Button, interaction: Interaction):
		self.stop()


class Paginator:
	def __init__(self, ctx: Context, pages: list, custom_children: Optional[List[Union[Button, Select]]] = []):
		self.ctx = ctx
		self.pages = pages
		self.custom_children = custom_children


	async def start(self, embeded: Optional[bool] = False):
		assert (self.pages)

		view = _view(self.ctx.author, self.pages, embeded)

		view.previous.disabled = True if (view.current_page <= 0) else False
		view.next.disabled = True if (view.current_page + 1 >= len(self.pages)) else False

		options = []
		for index, page in enumerate(self.pages):
			options.append(SelectOption(label=f"Page {index+1}", value=index))

		view.add_item(_select(options))

		if (len(self.custom_children) > 0):
			for child in self.custom_children:
				view.add_item(child)

		kwargs = {'content': self.pages[view.current_page]} if not (embeded) else {'embed': self.pages[view.current_page]}
		kwargs['view'] = view

		msg = await self.ctx.send(**kwargs)

		await view.wait()

		await msg.delete()