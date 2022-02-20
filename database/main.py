from redis import Redis

from redis_om import (HashModel, JsonModel, Field, Migrator)
from typing import Optional, List
from pprint import pprint

from utils.items import Weapon, Armor, Monster


redis = Redis(host='redis-11026.c241.us-east-1-4.ec2.cloud.redislabs.com', port=11026, db=1, password="xdaBgyVkr6gELOBNKtPvh8cxbX3NSc5Y")

OWNER = '470866478720090114'


class User(JsonModel):
	ID             : str = Field(index=True)
	
	coins          : Optional[int] = 1000
	exp            : Optional[int] = 0
	level          : Optional[int] = 1

	health         : Optional[int] = 100
	strength       : Optional[int] = 10
	defence        : Optional[int] = 10

	armor          : Optional[List[Armor]] = None
	weapon         : Optional[Weapon] = None

	stats_kills    : Optional[dict] = {}
	stats_deaths   : Optional[dict] = {}

	inventory      : Optional[list] = []
	
	class Meta:
		database = redis
		arbitary_types_allowed = True

class Guild(HashModel):
	ID       : str = Field(index=True)
	
	prefix   : Optional[str] = 'c-'
	is_world : Optional[bool] = False
	
	class Meta:
		database = redis


Migrator().run()


def fetch_users(): return [user.ID for user in User.find(User.ID != '0').all()]

def fetch_guilds(): return [guild.ID for guild in Guild.find(Guild.ID != '0').all()]


def get_user(ID): return User.find(User.ID == str(ID)).first() if (str(ID) in fetch_users()) else User(ID=str(ID)).save()


if __name__ == '__main__':
	while True:
		print(eval(input(">>> ")))