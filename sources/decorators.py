import discord
import functools
import traceback

from discord.ext import commands

from datetime import datetime as dt, timedelta
import datetime
import pytz

from local_io import JSONHandler
# from sources.translationT import (
#     discord,
#     json
# )
# from sources.paypal import (
# 	aiohttp
# )

import aiohttp
import os


data_options = JSONHandler(file_path="./infra/options.json").read_json()


def is_bot_owner(func):
	@functools.wraps(func)
	async def wrapper(*args, **kwargs):
		interaction = args[0] if isinstance(args[0], discord.Interaction) else args[1]

		owners_list = data_options["decorators"]["bot_owners"]

		if interaction.author.id not in owners_list:
			msg = data_options["decorators"]["warning_owner"]
			await interaction.send(f"{msg} ⚠️", ephemeral=True)
			return False
		return await func(*args, **kwargs)
	return wrapper


def handle_aiohttp_errors(func):
	@functools.wraps(func)
	async def wrapper(*args, **kwargs):
		try:
			result = await func(*args, **kwargs)
			return result
		except aiohttp.ClientError as e:
			print(f"Aiohttp error occurred: {e}")
			return None
		except Exception as e:
			print(f"An unexpected error occurred: {e}")
			return None
	return wrapper
