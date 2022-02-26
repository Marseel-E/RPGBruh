from typing import Optional, List, Union
from pydantic import BaseModel
from discord import Sticker
import json


def decide_rarity(power: int, MIN: int, MAX: int) -> str:
	""" Decides item rarity """
	power_range = range(MIN, MAX, round(MAX / MIN))

	rarities = {
		'common': MIN,
		'good': power_range[1],
		'rare': power_range[3],
		'epic': power_range[-2],
		'legendary': power_range[-1],
		'mythic': MAX
	}

	rarity = "common"
	for name, max_power in rarities.items():
		if power < max_power: break
		rarity = name

	return rarity


with open('utils/data.json', 'r') as f:
	all_items = json.loads(f.read())

class _data:
	def __init__(self):
		self.data = all_items

	def fetch_names(self, category : str) -> list:
		""" Returns a list of keys for the given category """
		return list(self.data[category].keys())

	def fetch(self, item : str) -> dict:
		""" Returns the data of the given item """
		return [data[item] for category, data in self.data.items() if (item in data.keys())][0]

	def get(self, item : str, key : str) -> str:
		""" Returns the value of the key for the item """
		return [data[item][key] for category, data in self.data.items() if (item in data.keys())][0]

Data = _data()


class Item(BaseModel):
	name   : str = ""
	icon   : Optional[str] = ":paperclip:"

	data   : Optional[dict] = {}
	amount : Optional[int] = 1


class Stats(BaseModel):
	kills  : Optional[list] = []
	deaths : Optional[list] = []
	duals  : Optional[dict] = {}


class Weapon(BaseModel):
	name   : str
	rarity : str = "common"
	icon   : str = ":paperclip:"
	power  : int = 10

	health : Optional[int] = 100


class Armor(BaseModel):
	name    : str
	rarity  : str = "common"
	icon    : str = ":paperclip:"
	defence : int = 10

	health : Optional[int] = 100


class Monster(BaseModel):
	name     : str
	level    : int = 1
	image    : str = ""

	health   : int = 100
	strength : int = 10
	defence  : int = 10

	weapon   : Optional[Weapon] = None
	armor    : Optional[List[Armor]] = None

	class Config:
		arbitary_types_allowed = True