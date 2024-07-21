import discord
from local_io import JSONHandler
import asyncio
from pathlib import Path
import traceback

# from sources.dropdowns.dropdown import DropdownView


class DropdownExchange(discord.ui.Select):
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
            await interaction.response.defer(ephemeral=True)

            assert self.view is not None
            
            view = self.view

            view.value = self.labels.index(self.values[0])
            view.interaction = interaction

            if int(view.value) == 0:
                from sources.buttons.exchange_button import ExchangeManagementButtons
                from sources.embeds import CustomEmbed

                embed = (
                    CustomEmbed(
                        "Foxbit Settings",
                        "Connect Gensen to your Foxbit account by adding the API keys which can be obtained from the [official website](https://app.foxbit.com.br/profile/api-key);\n\n"
                        "Link a new crypto asset to your portfolio;\n\n"
                        "Completely remove the data from your exchange account in Gensen's database by clicking disconnect."
                    ) # https://cdn.pfps.gg/banners/9031-toney.gif
                	.set_image("https://cdn.pfps.gg/banners/1785-chainsaw-man-cinema.gif")
                	.create_embed()
                )

                await interaction.followup.send(embed=embed, view=ExchangeManagementButtons(), ephemeral=True)
            elif int(view.value) == 1:
                await interaction.followup.send(
                    f"Esta funcionalidade ainda não foi desenvolvida.", ephemeral=True
                )
        except Exception as e:
            print(f"An error occurred: {e}")
            tb = traceback.format_exc()
            print(tb)
