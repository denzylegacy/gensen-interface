import discord
import traceback
from discord.ui import Modal, TextInput
from utils.utils import Utilities
from local_io import JSONHandler

from infra import log
from api import Foxbit
from firebase import Firebase
from utils.encryptor import Encryptor


textstyle = Utilities().textstyle
data_options = JSONHandler().read_options_json("./../infra/options.json")

class FoxbitApiKeysRegistration(Modal, title="Foxbit API Keys Registration"):

    foxbit_user_id = TextInput(
        label="FOXBIT USER ID",
        placeholder="(Mandatory)",
        required=True,
        max_length=300
    )
    
    foxbit_access_key = TextInput(
        label="FOXBIT ACCESS KEY",
        placeholder="(Mandatory)",
        required=True,
        max_length=300
    )
    
    foxbit_secret_key = TextInput(
        label="FOXBIT SECRET KEY",
        placeholder="(Mandatory)",
        required=True,
        max_length=300
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            firebase = Firebase()
            
            connection = firebase.firebase_connection("root")

            meResponse = Foxbit(
                api_key=self.foxbit_access_key.value,
                api_secret=self.foxbit_secret_key.value
            ).request("GET", "/rest/v3/me", None, None)
            log.info(f"Response: {meResponse}")
            
            if meResponse:  # if not meResponse:
                embed = discord.Embed(
                    title="Watch out!",
                    description="Foxbit API keys are invalid!!!",
                    color=0xffa07a
                )
                embed.add_field(
                    name="", 
                    value="Please check whether the information you entered is correct. If you believe this is a bug, please contact my developers!",
                    inline=False
                )
                
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                log.info("FOXBIT CREDENTIALS ARE VALID!")

                firebase = Firebase()

                connection.child(f"users/{interaction.user.id}/exchanges/foxbit/credentials").set(
                    {
                        "FOXBIT_USER_ID": Encryptor().encrypt_api_key(self.foxbit_user_id.value),
                        "FOXBIT_ACCESS_KEY": Encryptor().encrypt_api_key(self.foxbit_access_key.value),
                        "FOXBIT_SECRET_KEY": Encryptor().encrypt_api_key(self.foxbit_secret_key.value)
                    }
                )

                log.info(f'[REGISTERED CREDENTIALS] {interaction.user.id}')

                embed = discord.Embed(
                    title="Exchange connected successfully!",
                    description="Foxbit API keys are valid!!!",
                    color=0xDBD0F8
                )
                embed.add_field(
                    name="", 
                    value="From now on Gensen'll be able to operate cryptocurrencies contained in this exchange!\nAnd remember, you can **unlink** your exchange account at **any** time you wish!",
                    inline=False
                )

                await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            log.error(f"An error occurred: {str(e)}")
            await interaction.followup.send(
                f"An error occurred while processing your information. Please try again later or contact support.",
                ephemeral=True
            )

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message(
            f"An error occurred while processing your information: {error}", ephemeral=True
        )
        traceback.print_exception(type(error), error, error.__traceback__)
