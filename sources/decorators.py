import discord
import functools
import traceback
import aiohttp
from discord.ext import commands

from local_io import JSONHandler
from firebase import Firebase

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

def authenticate():
	async def predicate(ctx):
		try:
			assert ctx.guild is not None
			
			firebase = Firebase()
			
			connection = firebase.firebase_connection("root")

			users = connection.child(f"users").get()

			if not users or not str(ctx.author.id) in users.keys():
				from sources.buttons.auth_button import AuthButton
				from sources.embeds import CustomEmbed

				embed = (
					CustomEmbed(
						None, 
						"Hey! To begin our journey together, you first need to be authenticated!"
					)
					.set_image("https://cdn.pfps.gg/banners/7834-shirakami-fubuki-white-background.gif")
					.create_embed()
				)

				await ctx.send(embed=embed, view=AuthButton(), ephemeral=True)
				return True
			
			user_credentials = connection.child(f"users/{str(ctx.author.id)}/credentials").get()
			
			if not user_credentials:
				from sources.buttons.auth_button import AuthButton
				from sources.embeds import CustomEmbed
				
				embed = (
                    CustomEmbed(
                        "Gensen Authentication",
                        "You need to provide me with some information so things can work ^^"
                    )
                	.set_image("https://cdn.pfps.gg/banners/7834-shirakami-fubuki-white-background.gif")
                	.create_embed()
                )
				await ctx.send(embed=embed, view=AuthButton(), ephemeral=True)
				return True
		except Exception as error:
			print(f"ERROR: {error}")
			tb = traceback.format_exc()
			print(tb)
	return commands.check(predicate)
