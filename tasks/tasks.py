import discord
from discord.ext import commands, tasks
import datetime
import pytz
from pathlib import Path

from infra import log
from infra.settings import BASE_PATH
from api.coingecko import Coingecko
from crud import JsonDB
from firebase import Firebase
from gensen import ゲンセン


class BackgroundTasks(commands.Cog):
    """BackgroundTasks
    """

    def __init__(self, bot):
        self.bot = bot
        self.current_dir = Path(__file__).resolve().parent
        self.gensen: object = ゲンセン()
        self.coingecko: object = Coingecko()
        self.json_db = JsonDB(BASE_PATH + "/instance/db.json")

    @commands.Cog.listener()
    async def on_ready(self):
        await self.background_tasks.start()

    async def market_conditions_evaluator(self):
        firebase = Firebase()
        
        connection = firebase.firebase_connection("root")

        users = connection.child("users").get()

        if not users:
            return

        for user in users.keys():
            for asset in users[user]["assets"].keys():
                client_asset_data: dict = ゲンセン().user_asset_validator(
                    asset=users[user]["assets"][asset]["name"]
                )
                
                asset_available_value_brl: float = ゲンセン().convert_asset_to_brl(
                    asset=users[user]["assets"][asset]["name"],
                    brl_asset=client_asset_data["brl"],
                    available_balance=client_asset_data["available_balance"]
                )

                difference_check: float = round(
                    float(asset_available_value_brl)- 
                    float(users[user]["assets"][asset]["base_balance"]), 3
                )

                if (
                    float(asset_available_value_brl) >= 
                    float(users[user]["assets"][asset]["base_balance"]) + 
                    (float(users[user]["assets"][asset]["fixed_profit_brl"]) + 0.3)
                    ):
                    print(f"Tá na hora de vender, pai! +{difference_check} na conta!")

                    timestamp = datetime.datetime.now(
                        pytz.timezone("America/Sao_Paulo")
                    ).strftime("%Y-%m-%d %H:%M:%S")
                    
                    connection.child(f'users/{user}/assets/{users[user]["assets"][asset]["name"]}').update(
                        {
                            "available_balance_brl": float(client_asset_data["available_balance"]),
                            f'available_balance_{users[user]["assets"][asset]["name"].lower()}': asset_available_value_brl,
                            "brl": client_asset_data["brl"],
                            "usd": client_asset_data["usd"],
                            "update_timestamp_america_sp": timestamp
                        }
                    )
                    log.info(f'[UPDATE ASSET VALUES] {users[user]["assets"][asset]["name"]} -> {user}')
                    
                    ### DM NOTIFICATION ###

                    embed = discord.Embed(
                        title=f'Short-term profit of {users[user]["assets"][asset]["name"]} (+**{difference_check}**)!',
                        description=f'Right now it is recommended to **sell** R$**{difference_check}** worth of {users[user]["assets"][asset]["name"]}!!',
                        color=0xffa07a
                    )
                    embed.add_field(
                        name="", 
                        value="Remember, make your sales with caution. If you believe this is a mistake, please contact my developer!",
                        inline=False
                    )

                    await self.bot.get_user(int(user)).send(embed=embed)

    @tasks.loop(seconds=30)
    async def background_tasks(self):
        await self.market_conditions_evaluator()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BackgroundTasks(bot))
