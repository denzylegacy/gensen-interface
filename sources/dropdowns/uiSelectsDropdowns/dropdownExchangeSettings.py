import discord
from local_io import JSONHandler
from pathlib import Path
import traceback
from infra import log
from firebase import Firebase
from sources.forms.register_foxbit_api_keys import FoxbitApiKeysRegistration
from sources.forms.register_foxbit_asset import FoxbitAssetRegistration

data_options = JSONHandler(file_path="./infra/options.json").read_json()


class DropdownExchangeSettings(discord.ui.Select):
    def __init__(self, args, **kwargs):
        placeholder = kwargs.get("placeholder") or "You didn't type the placeholder"
        min_values = kwargs.get("min_values") or 1
        max_values = kwargs.get("max_values") or 1

        self.custom_id_dropdown = kwargs.get("custom_id_dropdown") or None
        self.custom_id_button = kwargs.get("custom_id_button") or None
        self.data_options = JSONHandler().read_options_json("./infra/options.json")

        options = [
            discord.SelectOption(label=x, description=y, emoji=z) for (x, y, z) in args
        ]

        self.labels = [x for (x, y, z) in args]

        self.current_dir = Path(__file__).resolve().parent

        super().__init__(
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            options=options,
            custom_id=self.custom_id_dropdown
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            assert self.view is not None
            
            view = self.view

            view.value = self.labels.index(self.values[0])
            view.interaction = interaction

            if int(view.value) == 0:  # API KEYs
                try:
                    await interaction.response.send_modal(FoxbitApiKeysRegistration())
                except:
                    log.error(traceback.format_exc())
            elif int(view.value) == 1:  # VIEW CRYPTOS
                try:
                    await interaction.response.defer(ephemeral=True)
                    await interaction.followup.send(
                        "This functionality has not yet been developed.", ephemeral=True
                    )
                except:
                    log.error(traceback.format_exc())
            elif int(view.value) == 2:  # ADD/UPDATE CRYPTO
                try:
                    await interaction.response.send_modal(FoxbitAssetRegistration())
                except:
                    log.error(traceback.format_exc())
            elif int(view.value) == 3:  # DISCONNECT CRYPTO
                try:
                    await interaction.response.defer(ephemeral=True)
                    await interaction.followup.send(
                        "This functionality has not yet been developed.", ephemeral=True
                    )
                except:
                    log.error(traceback.format_exc())
            elif int(view.value) == 4:  # DISCONNECT EXCHANGE
                await interaction.response.defer(ephemeral=True)
                
                try:
                    firebase = Firebase()
                    connection = firebase.firebase_connection("root")
                    foxbit = connection.child(f"users/{interaction.user.id}/exchanges/foxbit")

                    if foxbit.get():
                        foxbit.delete()
                        log.info(f'[FOXBIT ACCOUNT HAS BEEN DISCONNECTED] {interaction.user.id}')

                        embed = discord.Embed(
                            title="Exchange disconnected successfully!",
                            description="All data associated with this exchange has been permanently removed from our services. This includes credentials, asset information, and any other data collected for operational purposes. We have ensured complete deletion of all relevant information from our systems.",
                            color=0xDBD0F8
                        )
                        embed.add_field(
                            name="", 
                            value="Remember, you can connect this exchange again whenever you want!",
                            inline=False
                        )
                    else:
                        embed = discord.Embed(
                            title="No account found",
                            description="There is currently **no** Foxbit account associated with **your** user!!!",
                            color=0xffa07a
                        )

                    await interaction.followup.send(embed=embed, ephemeral=True)
                except Exception as e:
                        log.error(f"Error in DisconnectExchange: {str(e)}")
                        log.error(traceback.format_exc())
                        
                        try:
                            await interaction.followup.send("An error occurred while disconnecting the exchange. Please try again later or contact support.", ephemeral=True)
                        except Exception as follow_up_error:
                            log.error(f"Failed to send error message: {str(follow_up_error)}")
        except Exception as e:
            print(f"An error occurred: {e}")
            tb = traceback.format_exc()
            print(tb)
