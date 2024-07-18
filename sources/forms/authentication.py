import discord
import traceback
from discord.ui import Modal, TextInput
from utils.utils import Utilities
from local_io import JSONHandler

from infra import log
from api import Coingecko, Coinbase
from firebase import Firebase


textstyle = Utilities().textstyle
data_options = JSONHandler().read_options_json("./../infra/options.json")


class Authenticate(Modal, title="Authentication"):

	coingecko_api_key = TextInput(
		label="Coingecko API Key",
		placeholder="(Mandatory)",
		required=True,
		max_length=300
	)
	
	coinbase_api_key_name = TextInput(
		label="Coinbase API Key Name",
		placeholder="(Mandatory)",
		required=True,
		max_length=300
	)
	
	coinbase_api_private_key = TextInput(
        label="Coinbase API Private Key",
		placeholder="(Mandatory)",
		required=True,
		max_length=300
	)

	async def on_submit(self, interaction: discord.Interaction):
		await interaction.response.defer()
		if not Coingecko(coingecko_api_key=self.coingecko_api_key.value).auth():
			embed = discord.Embed(
				title="Watch out!",
				description=f"Coingecko's API key is invalid!!!",
				color=0xffa07a
			)
			embed.add_field(
				name="", 
				value="Please check whether the information you entered is correct. If you believe this is a bug, please contact my developer!",
				inline=False
			)
			await interaction.followup.send(embed=embed, ephemeral=True)
		
		if not Coinbase(
			api_key=self.coinbase_api_key_name.value, 
			api_secret=self.coinbase_api_private_key.value
		).auth():
			embed = discord.Embed(
				title="Watch out!",
				description=f"The set of credentials provided to Coinbase are invalid!!!",
				color=0xffa07a
			)
			embed.add_field(
				name="", 
				value="Please check whether the information you entered is correct. If you believe this is a bug, please contact my developer!",
				inline=False
			)
			await interaction.followup.send(embed=embed, ephemeral=True)
			return
		
		log.info("COINGECKO API KEY IS VALID!")
		log.info("CONBASE CREDENTIALS ARE VALID!")

	async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
		await interaction.response.send_message(
			f'Oops! Ocorreu um erro ao processar suas informações: {error}', ephemeral=True
		)
		traceback.print_exception(type(error), error, error.__traceback__)