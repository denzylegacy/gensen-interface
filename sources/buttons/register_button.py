import discord
import traceback
from infra import log


class AssetRegistrationButton(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)

	@discord.ui.button(label="Continue", style=discord.ButtonStyle.green, custom_id="continue:button")
	async def Continue(self,  interaction: discord.Interaction, button: discord.ui.Button):
		try:
			from ..forms.register_asset import AssetRegistration
			await interaction.response.send_modal(AssetRegistration())
		except:
			log.error(traceback.format_exc())
