from pydantic import BaseModel
from typing import Optional, List, Union
from discord import Sticker
import json


with open('utils/data.json', 'r') as f:
	all_items = json.loads(f.read())

def get_weapons_names(): return all_items['weapons'].keys()
def get_armor_names(): return all_items['armor'].keys()
def get_monsters_names(): return all_items['monsters'].keys()


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