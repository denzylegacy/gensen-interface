import discord
import traceback
from infra import log


class AuthButton(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)

	@discord.ui.button(label="Authenticate", style=discord.ButtonStyle.green, custom_id="authenticate:button")
	async def Authenticate(self,  interaction: discord.Interaction, button: discord.ui.Button):
		try:
			from ..forms.authentication import Authenticate
			await interaction.response.send_modal(Authenticate())
		except:
			log.error(traceback.format_exc())
