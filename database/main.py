from redis import Redis
from redis_om import (HashModel, JsonModel, Field, Migrator)

import os
from dotenv import load_dotenv
load_dotenv('../.env')

redis = Redis(host=os.environ.get("DB_HOST"), port=os.environ.get("DB_PORT"), db=0, password=os.environ.get("DB_PASSWORD"))

from typing import Optional, List
from pprint import pprint

from utils import Armor, Weapon, Stats


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

	inventory      : Optional[List[dict]] = []

	in_dual        : Optional[bool] = False

	class Meta:
		database = redis

class Guild(HashModel):
	ID       : str = Field(index=True)
	
	prefix   : Optional[str] = 'c-'
	is_world : Optional[bool] = False

	class Meta:
		database = redis

Migrator().run()


def fetch_users(): return [user.ID for user in User.find(User.ID != "0").all()]
def fetch_guilds(): return [guild.ID for guild in Guild.find(Guild.ID != "0").all()]

def get_user(ID): return User.find(User.ID == str(ID)).first() if (str(ID) in fetch_users()) else User(ID=str(ID)).save()