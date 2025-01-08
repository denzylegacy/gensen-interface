import discord
import traceback
import datetime
import pytz
from discord.ui import Modal, TextInput
from utils.utils import Utilities
from local_io import JSONHandler
from firebase import Firebase
from infra import log

textstyle = Utilities().textstyle
data_options = JSONHandler().read_options_json("./../infra/options.json")


class BitcoinAddressRegistration(Modal, title="Bitcoin Address registration"):

    bitcoin_address = TextInput(
        label="Bitcoin Address",
        placeholder="(Mandatory)",
        required=True,
        max_length=256
    )

    async def on_submit(self, interaction: discord.Interaction):
        firebase = Firebase()

        connection = firebase.firebase_connection("root")
        
        timestamp = datetime.datetime.now(
            pytz.timezone("America/Sao_Paulo")
        ).strftime("%Y-%m-%d %H:%M:%S")

        connection.child(
            f"users/{interaction.user.id}/bitcoin"
        ).update(
            {
                "address": self.bitcoin_address.value,
                "update_timestamp_america_sp": timestamp
            }
        )

        log.info(f"[REGISTERED] {self.bitcoin_address} -> {interaction.user.name} ({interaction.user.id})")

        resp = (
            f"Address: `{self.bitcoin_address}`"
        )

        embed = discord.Embed(title="Successfully registered!", description=resp, color=0x6AA84F)
        embed.add_field(name="", value="Your address has been registered successfully!", inline=False)

        await interaction.followup.send(embed=embed, ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message(
            f"An error occurred while processing your information: {error}", ephemeral=True
        )
        traceback.print_exception(type(error), error, error.__traceback__)
