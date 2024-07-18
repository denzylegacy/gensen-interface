import discord
from sources.dropdowns.uiSelectsDropdowns import DropdownAssets


class DropdownView(discord.ui.View):
	def __init__(self, args, **kwargs):
		super().__init__(timeout=None) #response = kwargs.get('response')
		placeholder = kwargs.get("placeholder") or "You didn't type the placeholder"
		min_values = kwargs.get("min_values") or 1
		max_values = kwargs.get("max_values") or 1
		self.dropdown_name = kwargs.get("dropdown_name")
		
		self.custom_id_dropdown = kwargs.get("custom_id_dropdown")
		self.custom_id_button = kwargs.get("custom_id_button")

		# Adiciona o SelectMenu/ Dropdown ao nosso objeto view.
		if self.dropdown_name == "DropdownAssets":
			self.add_item(
				DropdownAssets(
					args, 
					placeholder=placeholder, 
					min_values=min_values, 
					max_values=max_values, 
					custom_id_dropdown=self.custom_id_dropdown, 
					custom_id_button=self.custom_id_button
				)
			)
