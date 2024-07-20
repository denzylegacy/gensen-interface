import discord
import traceback
from discord.ui import Modal, TextInput
from utils.utils import Utilities
from local_io import JSONHandler

from infra import log
from api import Coingecko, Coinbase
from firebase import Firebase
from utils.encryptor import Encryptor


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

		coinbase_api_key_name = str(
			self.coinbase_api_key_name.value
		).replace("||", "\n")
		coinbase_api_private_key = str(
			self.coinbase_api_private_key.value
		).replace("||", "\n")

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
		
		log.info("COINGECKO API KEY IS VALID!")

		if not Coinbase(
			api_key=coinbase_api_key_name, 
			api_secret=coinbase_api_private_key
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
		
		log.info("CONBASE CREDENTIALS ARE VALID!")

		firebase = Firebase()
		
		connection = firebase.firebase_connection("root")

		connection.child(f"users/{interaction.user.id}/credentials").update(
			{
				"coingecko_api_key": Encryptor().encrypt_api_key(self.coingecko_api_key.value),
				"coinbase_api_key_name": Encryptor().encrypt_api_key(coinbase_api_key_name),
				"coinbase_api_private_key": Encryptor().encrypt_api_key(coinbase_api_private_key)
			}
		)
		log.info(f'[REGISTERED CREDENTIALS] {interaction.user.id}')
    
	async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
		await interaction.response.send_message(
			f"An error occurred while processing your information: {error}", ephemeral=True
		)
		traceback.print_exception(type(error), error, error.__traceback__)