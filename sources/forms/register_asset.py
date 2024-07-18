import discord
import traceback
from discord.ui import Modal, TextInput
from utils.utils import Utilities
from local_io import JSONHandler
from firebase import Firebase
from infra import log
from api.coingecko import Coingecko
from gensen import ゲンセン

textstyle = Utilities().textstyle
data_options = JSONHandler().read_options_json("./../infra/options.json")


class AssetRegistration(Modal, title="Asset registration"):

	asset = TextInput(
		label="Asset Name",
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
		
		asset_data = Coingecko().coin_market_data(coind_id=self.asset.value)

		if not asset_data:
			embed = discord.Embed(
				title="Watch out!",
				description=f"The **{self.asset.value}** asset is **not** listed on Coingecko!!",
				color=0xffa07a
			)
			embed.add_field(
				name="", 
				value="Please check whether the information you entered is correct. If you believe this is a bug, please contact my developer!",
				inline=False
			)
			await interaction.followup.send(embed=embed, ephemeral=True)
		else:
			firebase = Firebase()
			
			connection = firebase.firebase_connection("users")

			user_assets = connection.child(
				f"{interaction.user.id}/assets"
			).get()

			if not self.asset.value in user_assets.keys():
				client_asset_data: dict = ゲンセン().user_asset_validator(asset=self.asset.value)
				
				asset_available_value_brl: float = ゲンセン().convert_asset_to_brl(
					asset=self.asset.value,
					brl_asset=client_asset_data["brl"],
					available_balance=client_asset_data["available_balance"]
				)
				
				connection.child(f"{interaction.user.id}/assets/{self.asset.value}").update(
					{
						"name": self.asset.value,
						"available_balance_brl": client_asset_data["available_balance"],
						f"available_balance_{self.asset.value.lower()}": asset_available_value_brl,
						"base_balance": self.base_balance.value,
						"brl": client_asset_data["brl"],
						"usd": client_asset_data["usd"],
					}
				)
				log.info(f"+ {self.asset.value.upper()} -> {interaction.user.name} ({interaction.user.id})")

				resp = (
					f"Asset: {self.asset.value.upper()}\n"
					f"Your Available Balance (BRL): {client_asset_data["available_balance"]}\n"
					f"Your Available Balance ({self.asset.value}): {asset_available_value_brl}\n"
					f"Base Balance (BRL): {self.base_balance.value}\n"
					f"Fixed Profit (BRL): {self.fixed_profit_brl.value}"
				)

				embed = discord.Embed(title="Successfully registered!", description=resp, color=0x6AA84F)
				embed.add_field(name="", value=f"Your asset has been registered successfully!", inline=False)

				await interaction.followup.send(embed=embed, ephemeral=True)
			else:
				embed = discord.Embed(
					title="Watch out!",
					description=f"The **{self.asset.value}** asset **is** already linked to your account!!",
					color=0xffa07a
				)
				embed.add_field(
					name="", 
					value="Please check whether the information you entered is correct. If you believe this is a bug, please contact my developer!",
					inline=False
				)
				await interaction.followup.send(embed=embed, ephemeral=True)
	
	async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
		await interaction.response.send_message(
			f"An error occurred while processing your information: {error}", ephemeral=True
		)
		traceback.print_exception(type(error), error, error.__traceback__)
