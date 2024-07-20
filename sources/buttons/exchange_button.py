import discord
import traceback

from infra import log
from firebase import Firebase


class ExchangeManagementButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Add API Keys", style=discord.ButtonStyle.green, custom_id="add_api:button")
    async def AddAPIKeys(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            from ..forms.register_foxbit_api_keys import FoxbitApiKeysRegistration
            await interaction.response.send_modal(FoxbitApiKeysRegistration())
        except:
            log.error(traceback.format_exc())
    
    @discord.ui.button(label="Link crypto", style=discord.ButtonStyle.green, custom_id="link_crypto:button")
    async def LinkCrypto(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            from ..forms.register_foxbit_asset import FoxbitAssetRegistration
            await interaction.response.send_modal(FoxbitAssetRegistration())
        except:
            log.error(traceback.format_exc())

    @discord.ui.button(label="Disconnect", style=discord.ButtonStyle.red, custom_id="disconnect:button")
    async def DisconnectExchange(self, interaction: discord.Interaction, button: discord.ui.Button):
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