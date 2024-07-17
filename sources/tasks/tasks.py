import discord
from discord.ext import commands, tasks
import asyncio
import datetime
import pytz
from pathlib import Path

from coingecko import Coingecko
from gensen import ゲンセン
from crud import JsonDB
from infra.settings import BASE_PATH


class Monitoring(commands.Cog):
    """Works with Monitoring"""

    def __init__(self, bot):
        self.bot = bot
        self.current_dir = Path(__file__).resolve().parent
        self.gensen: object = ゲンセン()
        self.coingecko: object = Coingecko()
        self.json_db = JsonDB(BASE_PATH + "/instance/db.json")

    @commands.Cog.listener()
    async def on_ready(self):
        await self.background_tasks.start()

    async def background(self, forced_execution: bool = False):
        date_time = datetime.datetime.now(
            pytz.timezone("America/Sao_Paulo")
        ).strftime("%d-%m-%Y às %H:%M:%S")

        print(date_time)

        price_for_btc_usd_brl: dict = self.coingecko.coin_current_price_for_btc_usd_brl(
            coind_id="bitcoin"
        )

        users = self.json_db.read(collection="users")

        if users:
            for user in users.keys():
                user_data = self.json_db.read(collection="users", doc=str(user))

                value_difference, sell = self.gensen.engine(
                    base_asset_value=user_data["bitcoin"]["base"], 
                    previous_asset_value=user_data["bitcoin"]["brl"],
                    current_asset_value=price_for_btc_usd_brl["brl"]
                )

                print("difference:", value_difference)

                if sell:
                    print("Vender!")
        await asyncio.sleep(3)
    

    @tasks.loop(seconds=30)
    async def background_tasks(self, forced_execution: bool = False):

        def day_of_the_week():
            week_days = [
                "monday", "tuesday", "wednesday",
                "thursday", "friday", "saturday", "sunday"
            ]
            return str(week_days[datetime.datetime.now().weekday()])

        # today = day_of_the_week()
        # if today != "saturday" and today != "sunday" or forced_execution:
        await self.background(forced_execution=forced_execution)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Monitoring(bot))
