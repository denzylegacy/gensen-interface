import discord
import functools
import aiohttp

from local_io import JSONHandler


data_options = JSONHandler(file_path="./infra/options.json").read_json()


def bot_owner(func):
	@functools.wraps(func)
	async def wrapper(*args, **kwargs):
		interaction = args[0] if isinstance(args[0], discord.Interaction) else args[1]

		if interaction.author.id not in data_options["decorators"]["bot_owners"]:
			await interaction.send(f'{data_options["decorators"]["warning_owner"]} ⚠️', ephemeral=True)
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
