import discord
from discord.ext import commands, tasks
import asyncio
import datetime
import pytz
from pathlib import Path

from infra.settings import BASE_PATH
from api.coingecko import Coingecko
from crud import JsonDB
from firebase import Firebase
from gensen import ゲンセン


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

    async def market_conditions_evaluator(self, forced_execution: bool = False):
        date_time = datetime.datetime.now(
            pytz.timezone("America/Sao_Paulo")
        ).strftime("%Y-%m-%d %H:%M:%S")


        # print(date_time)

        # firebase = Firebase()
        
        # connection = firebase.firebase_connection("users")
        
        await asyncio.sleep(3)
    

    @tasks.loop(seconds=30)
    async def background_tasks(self, forced_execution: bool = False):
        await self.market_conditions_evaluator(forced_execution=forced_execution)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Monitoring(bot))
