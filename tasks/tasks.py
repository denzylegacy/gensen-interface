import discord
from discord.ext import commands, tasks
import datetime
import pytz
import asyncio
from pathlib import Path

from infra import log
from infra.settings import BASE_PATH
from crud import JsonDB
from firebase import Firebase
from gensen import ゲンセン


class BackgroundTasks(commands.Cog):
    """BackgroundTasks
    """

    def __init__(self, bot):
        self.bot = bot
        self.current_dir = Path(__file__).resolve().parent
        self.json_db = JsonDB(BASE_PATH + "/instance/db.json")

    @commands.Cog.listener()
    async def on_ready(self):
        await self.background_tasks.start()

    async def market_conditions_evaluator(self):
        log.info(f"[background_tasks] market_conditions_evaluator: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        firebase = Firebase()
        
        connection = firebase.firebase_connection("root")

        users = connection.child("users").get()

        if not users:
            return

        for user in users.keys():
            user_credentials: dict = ゲンセン(user=user).get_user_credentials()
            
            if not user_credentials:
                return
        
            for asset in users[user]["assets"].keys():
                client_asset_data: dict = ゲンセン(user=user).user_asset_validator(
                    asset=users[user]["assets"][asset]["name"]
                )

                if client_asset_data:
                    asset_available_value_brl: float = ゲンセン(user=user).convert_asset_to_brl(
                        asset=users[user]["assets"][asset]["name"],
                        brl_asset=client_asset_data["brl"],
                        available_balance_brl=client_asset_data["available_balance"]
                    )

                    difference_check: float = round(
                        float(asset_available_value_brl) - 
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
                                f'available_balance_{users[user]["assets"][asset]["name"].lower()}': float(client_asset_data["available_balance"]),
                                "available_balance_brl": asset_available_value_brl,
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
                await asyncio.sleep(1)

    @tasks.loop(seconds=300)
    async def background_tasks(self):
        await self.market_conditions_evaluator()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BackgroundTasks(bot))
