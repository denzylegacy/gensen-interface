import discord
import traceback
from discord.ui import Modal, TextInput
from utils.utils import Utilities
from local_io import JSONHandler
from firebase import Firebase
from infra import log

textstyle = Utilities().textstyle
data_options = JSONHandler().read_options_json("./../infra/options.json")


class AssetRegistration(Modal, title="Asset registration"):

	asset = TextInput(
		label="Asset Acronym",
		placeholder="(Mandatory)",
		required=True,
		max_length=15
	)

	base_balance = TextInput(
		label="Base Balance (BRL)",
		placeholder="100",
		required=True,
		max_length=4
	)

	fixed_profit_brl = TextInput(
		label="Fixed Profit (BRL)",
		placeholder="5",
		required=True,
		max_length=4
	)

	async def on_submit(self, interaction: discord.Interaction):
		await interaction.response.defer()

        # Search for the Asset on Coingecko and validate its existence

		resp = (
			f"Asset: {self.asset.value}\n"
			f"Base Balance (BRL): {self.base_balance.value}\n"
			f"Fixed Profit (BRL): {self.fixed_profit_brl.value}"
		)

		embed = discord.Embed(title="", description=resp, color=0x6AA84F)

		embed.add_field(name="", value=f"Your asset has been registered successfully!", inline=False)

		firebase = Firebase()
		# system_user_var = connection.child(f"{interaction.user.id}").get()

		# if system_user_var:
		
		connection = firebase.firebase_connection("users")
		connection.child(f"{interaction.user.id}/assets/{self.asset.value}").update(
            {
                "asset_name": "bitcoin",
                "available_balance": 0.00141621,
                "base_balance": 100,
                "brl": 498,
                "usd": 93.77,
            }
        )
		log.info(f"+ {self.asset.value} - {interaction.user.name} ({interaction.user.id})")
		await interaction.followup.send(embed=embed, ephemeral=True)
        
		# else:
		# 	await interaction.followup.send("Hey! Your username is not in my database!", ephemeral=True)

	async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
		await interaction.response.send_message(
			f"An error occurred while processing your information: {error}", ephemeral=True
		)
		traceback.print_exception(type(error), error, error.__traceback__)
