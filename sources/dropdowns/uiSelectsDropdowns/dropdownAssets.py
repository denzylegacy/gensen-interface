import discord
from local_io import JSONHandler
import asyncio
from pathlib import Path
import traceback

# from sources.dropdowns.dropdown import DropdownView


class DropdownAssets(discord.ui.Select):
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
                from sources.buttons.register_button import AssetRegistrationButton
                from sources.embeds import CustomEmbed

                embed = (
                    CustomEmbed(
                        "Gensen Asset Inclusion",
                        "You must enter the name of the asset you want to register in your username, the base value and the value related to the fixed profit for it after clicking continue."
                    )
                	.set_image("https://cdn.pfps.gg/banners/9031-toney.gif")
                	# https://i.imgur.com/wlLmdW9.gif
                	# https://i.imgur.com/9df8CxP.gif
                	# https://i.imgur.com/oDIA7hz.gif
                	# https://i.imgur.com/isuZQ31.gif
                	# https://i.imgur.com/Pj2dF4w.gif
                	# https://i.imgur.com/8Kop1Lt.gif
                	# https://i.imgur.com/dbSES5Z.gif
                	# https://i.imgur.com/tKrQjIA.gif
                	# https://i.imgur.com/fvQcI5h.mp4
                	# https://i.imgur.com/WmqMqNG.png
                	.create_embed()
                )

                await interaction.followup.send(embed=embed, view=AssetRegistrationButton(), ephemeral=True)
            elif int(view.value) == 1:
                await interaction.followup.send(
                    f"Esta funcionalidade ainda não foi desenvolvida.", ephemeral=True
                )
        except Exception as e:
            print(f"An error occurred: {e}")
            tb = traceback.format_exc()
            print(tb)
