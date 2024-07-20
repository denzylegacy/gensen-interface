import discord
import traceback
import datetime
import pytz
from discord.ui import Modal, TextInput
from utils.utils import Utilities
from local_io import JSONHandler
from firebase import Firebase
from infra import log
from api.foxbit import Foxbit
import asyncio
from utils.encryptor import Encryptor

textstyle = Utilities().textstyle
data_options = JSONHandler().read_options_json("./../infra/options.json")


class FoxbitAssetRegistration(Modal, title="Asset registration"):

    asset = TextInput(
        label="Asset Name",
        placeholder="(Mandatory)",
        required=True,
        max_length=30
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
        await interaction.response.defer(ephemeral=True)

        if not self.base_balance.value.isdigit() or not self.fixed_profit_brl.value.isdigit():
            embed = discord.Embed(
                title="Watch out!",
                description="The **Base Balance (BRL)** and **Fixed Profit (BRL)** fields must **only** be filled in with numbers!!",
                color=0xffa07a
            )
            embed.add_field(
                name="", 
                value="Please check whether the information you entered is correct. If you believe this is a bug, please contact my developer!",
                inline=False
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        currency_name = self.asset.value.strip().lower()
        
        firebase = Firebase()

        connection = firebase.firebase_connection("root")

        user_credentials = connection.child(
            f"users/{interaction.user.id}/exchanges/foxbit/credentials"
        ).get()
        
        foxbit = Foxbit(
            api_key=Encryptor().decrypt_api_key(user_credentials["FOXBIT_ACCESS_KEY"]),
            api_secret=Encryptor().decrypt_api_key(user_credentials["FOXBIT_SECRET_KEY"])
        )

        currency = foxbit.check_currency(currency=currency_name)
        
        if not currency:
            await interaction.followup.send(
                "The cryptocurrency you are looking for is not registered with Foxbit! Please try again later or contact my developers.",
                ephemeral=True
            )
            return
        
        user_assets = connection.child(
            f"users/{interaction.user.id}/exchanges/foxbit/cryptocurrencies"
        ).get()

        asset_names = [user_assets[y]["name"].lower() for y in user_assets] + list(user_assets.keys())
        
        if not user_assets or currency_name not in asset_names:
            timestamp = datetime.datetime.now(
                pytz.timezone("America/Sao_Paulo")
            ).strftime("%Y-%m-%d %H:%M:%S")
            
            connection.child(
                f"users/{interaction.user.id}/exchanges/foxbit/cryptocurrencies/{currency['symbol'].lower()}"
            ).update(
                {
                    "name": currency["name"],
                    "base_balance": float(self.base_balance.value),
                    "fixed_profit_brl": float(self.fixed_profit_brl.value),
                    "update_timestamp_america_sp": timestamp
                }
            )
            log.info(f"[LINKED] {currency_name.upper()} -> {interaction.user.name} ({interaction.user.id})")
            
            resp = (
                f"Asset: {currency_name.upper()}\n"
                f"Base Balance (BRL): {self.base_balance.value}\n"
                f"Fixed Profit (BRL): {self.fixed_profit_brl.value}"
            )
            
            embed = discord.Embed(title="Successfully registered!", description=resp, color=0x6AA84F)
            embed.add_field(name="", value="Your asset has been registered successfully!", inline=False)
            
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
