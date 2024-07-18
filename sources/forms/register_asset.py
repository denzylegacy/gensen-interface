import discord
import traceback
import datetime
import pytz
from discord.ui import Modal, TextInput
from utils.utils import Utilities
from local_io import JSONHandler
from firebase import Firebase
from infra import log
from api.coingecko import Coingecko
from gensen import ゲンセン
from utils.encryptor import Encryptor

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
		placeholder="100 (Enter digits only!)",
		required=True,
		max_length=4
	)

	fixed_profit_brl = TextInput(
		label="Fixed Profit (BRL)",
		placeholder="5 (Enter digits only!)",
		required=True,
		max_length=4
	)

	async def on_submit(self, interaction: discord.Interaction):
		await interaction.response.defer()

		firebase = Firebase()

		if (
			not self.base_balance.value.isdigit() or
			not self.fixed_profit_brl.value.isdigit()
		):
			embed = discord.Embed(
				title="Watch out!",
				description=f"The **Base Balance (BRL)** and **Fixed Profit (BRL)** fields must **only** be filled in with numbers!!",
				color=0xffa07a
			)
			embed.add_field(
				name="", 
				value="Please check whether the information you entered is correct. If you believe this is a bug, please contact my developer!",
				inline=False
			)
			await interaction.followup.send(embed=embed, ephemeral=True)
			return
		
		user_credentials: dict = ゲンセン(user=interaction.user.id).get_user_credentials()

		asset_data = Coingecko(
                coingecko_api_key=Encryptor().decrypt_api_key(user_credentials["coingecko_api_key"])
            ).coin_market_data(coind_id=self.asset.value)

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
			connection = firebase.firebase_connection("root")

			user_assets = connection.child(
				f"users/{interaction.user.id}/assets"
			).get()

			if not user_assets or not self.asset.value in user_assets.keys():
				client_asset_data: dict = ゲンセン(
					user=interaction.user.id
				).user_asset_validator(asset=self.asset.value)
				
				asset_available_value_brl: float = ゲンセン(
					user=interaction.user.id
				).convert_asset_to_brl(
					asset=self.asset.value,
					brl_asset=client_asset_data["brl"],
					available_balance_brl=client_asset_data["available_balance"]
				)

				timestamp = datetime.datetime.now(
					pytz.timezone("America/Sao_Paulo")
				).strftime("%Y-%m-%d %H:%M:%S")
				
				connection.child(f"users/{interaction.user.id}/assets/{self.asset.value}").update(
					{
						"name": self.asset.value,
						f"available_balance_{self.asset.value.lower()}": float(client_asset_data["available_balance"]),
						"available_balance_brl": asset_available_value_brl,
						"base_balance": float(self.base_balance.value),
						"fixed_profit_brl": float(self.fixed_profit_brl.value),
						"brl": client_asset_data["brl"],
						"usd": client_asset_data["usd"],
						"update_timestamp_america_sp": timestamp
					}
				)
				log.info(f"[LINKED] {self.asset.value.upper()} -> {interaction.user.name} ({interaction.user.id})")

				resp = (
					f"Asset: {self.asset.value.upper()}\n"
					f"Your Available Balance: {client_asset_data["available_balance"]}\n"
					f"Your Available Balance (BRL)({self.asset.value}): {asset_available_value_brl}\n"
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
