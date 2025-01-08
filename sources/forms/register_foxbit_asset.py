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

    standby_balance = TextInput(
        label="Standby Balance (BRL)",
        placeholder="100 (Enter digits only!)",
        required=True,
        max_length=4
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        if not self.standby_balance.value.isdigit():
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

        _standby_balance = connection.child(
            f"users/{interaction.user.id}/exchanges/foxbit/cryptocurrencies/{currency['symbol'].lower()}/standby_balance"
        ).get()

        _base_balance = connection.child(
            f"users/{interaction.user.id}/exchanges/foxbit/cryptocurrencies/{currency['symbol'].lower()}/base_balance"
        ).get()

        _initial_profit = connection.child(
            f"users/{interaction.user.id}/exchanges/foxbit/cryptocurrencies/{currency['symbol'].lower()}/initial_profit"
        ).get()

        new_standby_balance = (
            float(self.standby_balance.value) + float(_standby_balance) 
            if _standby_balance else float(self.standby_balance.value)
        )
        
        if not _initial_profit and _base_balance:
            new_standby_balance += float(_base_balance)
        
        timestamp = datetime.datetime.now(
            pytz.timezone("America/Sao_Paulo")
        ).strftime("%Y-%m-%d %H:%M:%S")

        connection.child(
            f"users/{interaction.user.id}/exchanges/foxbit/cryptocurrencies/{currency['symbol'].lower()}"
        ).update(
            {
                "name": currency["name"],
                "standby_balance": new_standby_balance,
                "update_timestamp_america_sp": timestamp
            }
        )
        log.info(f"[LINKED] {currency_name.upper()} -> {interaction.user.name} ({interaction.user.id})")

        resp = (
            f"Asset: {currency_name.upper()}\n"
            f"Standby Balance (BRL): {self.standby_balance.value}"
        )

        embed = discord.Embed(title="Successfully registered!", description=resp, color=0x6AA84F)
        embed.add_field(name="", value="Your asset has been registered successfully!", inline=False)

        await interaction.followup.send(embed=embed, ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message(
            f"An error occurred while processing your information: {error}", ephemeral=True
        )
        traceback.print_exception(type(error), error, error.__traceback__)
