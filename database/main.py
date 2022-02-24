from redis import Redis
from redis_om import (HashModel, JsonModel, Field, Migrator)
from redis_om.model.model import NotFoundError

import os
from dotenv import load_dotenv
load_dotenv('../.env')

redis = Redis(host=os.environ.get("DB_HOST"), port=os.environ.get("DB_PORT"), db=0, password=os.environ.get("DB_PASSWORD"))

from typing import Optional, List, Union
from pprint import pprint
from datetime import datetime

from utils import Armor, Weapon, Stats, Item


class User(JsonModel):
	ID             : str = Field(index=True)
	
	coins          : Optional[int] = 1000
	exp            : Optional[int] = 0
	level          : Optional[int] = 1

	health         : Optional[int] = 100
	strength       : Optional[int] = 10
	defence        : Optional[int] = 10

	armor          : Optional[List[Armor]] = []
	weapon         : Optional[Weapon] = None

	stats          : Optional[Stats] = Stats()

	equiptment     : Optional[List[dict]] = []
	inventory      : Optional[List[Item]] = []

	in_dual        : Optional[bool] = False

	mine_cooldown  : Optional[datetime] = datetime.utcnow()
	chop_cooldown  : Optional[datetime] = datetime.utcnow()

	class Meta:
		database = redis

class Guild(HashModel):
	ID       : str = Field(index=True)
	
	prefix   : Optional[str] = 'c-'
	is_world : Optional[bool] = False

	class Meta:
		database = redis


from pydantic import BaseModel

class MarketplaceItem(BaseModel):
	user  : User
	data  : Union[Weapon, Armor]
	price : int

	class Config:
		arbitary_types_allowed = True

class Marketplace(JsonModel):
	ID   : str = Field(index=True)
	
	items : Optional[List[MarketplaceItem]] = []

	class Meta:
		database = redis


Migrator().run()

try: Global_Marketplace = Marketplace.find(Marketplace.ID == "global").first()
except NotFoundError: Global_Marketplace = Marketplace(ID="global").save()


def fetch_users() -> list:
	""" Returns a list of every user ID """
	return [user.ID for user in User.find(User.ID != "0").all()]
def fetch_guilds() -> list:
	""" Returns a list of every guild ID """
	return [guild.ID for guild in Guild.find(Guild.ID != "0").all()]

def get_user(ID) -> User:
	""" Gets a User or creates one if it doesn't exist """
	return User.find(User.ID == str(ID)).first() if (str(ID) in fetch_users()) else User(ID=str(ID)).save()