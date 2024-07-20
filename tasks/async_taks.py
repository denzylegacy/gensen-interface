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
from api.foxbit import Foxbit
from utils.encryptor import Encryptor


class BackgroundTasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_dir = Path(__file__).resolve().parent
        self.json_db = JsonDB(BASE_PATH + "/instance/db.json")

    @commands.Cog.listener()
    async def on_ready(self):
        self.background_tasks.start()

    @tasks.loop(seconds=30)
    async def background_tasks(self):
        await self.market_conditions_evaluator()

    async def market_conditions_evaluator(self):
        log.info(f"[background_tasks] market_conditions_evaluator: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        firebase = Firebase()
        connection = firebase.firebase_connection("root")
        users = connection.child("users").get()

        if not users:
            return

        tasks = []
        for user in users.keys():
            tasks.append(self.process_user(user, users[user], connection))
        
        await asyncio.gather(*tasks)

    async def process_user(self, user, user_data, connection):
        user_credentials = connection.child(f"users/{user}/exchanges/foxbit/credentials").get()
        if not user_credentials:
            return

        for exchange in user_data["exchanges"].keys():
            for cryptocurrencie in user_data["exchanges"][exchange]["cryptocurrencies"].keys():
                await self.process_cryptocurrency(user, user_credentials, exchange, cryptocurrencie, user_data["exchanges"][exchange]["cryptocurrencies"][cryptocurrencie])

    async def process_cryptocurrency(self, user, user_credentials, exchange, cryptocurrencie, asset):
        foxbit = Foxbit(
            api_key=Encryptor().decrypt_api_key(user_credentials["FOXBIT_ACCESS_KEY"]),
            api_secret=Encryptor().decrypt_api_key(user_credentials["FOXBIT_SECRET_KEY"])
        )

        accounts = await self.run_in_executor(foxbit.request("GET", "/rest/v3/accounts", None, None))

        for account in accounts["data"]:
            if account["currency_symbol"] == cryptocurrencie:
                params = {
                    "side": "buy",
                    "base_currency": cryptocurrencie,
                    "quote_currency": "brl",
                    "amount": "1"
                }
                
                quote_sell = await self.run_in_executor(foxbit.request("GET", "/rest/v3/markets/quotes", params=params, body=None))

                asset_available_value_brl = foxbit.convert_asset_to_brl(
                    brl_asset=float(account["balance_available"]),
                    available_balance_brl=float(quote_sell["price"])
                )

                difference_check = round(float(asset_available_value_brl) - float(asset["base_balance"]), 3)
                
                log.info(f"{difference_check}: {cryptocurrencie} -> {user}")

                if float(asset_available_value_brl) >= float(asset["base_balance"]) + (float(asset["fixed_profit_brl"]) + 0.3):
                    await self.send_notification(user, cryptocurrencie, difference_check, asset["name"])

    async def send_notification(self, user, cryptocurrencie, difference_check, asset_name):
        log.info(f'[NOTIFICATION] {cryptocurrencie} -> {user}')
        
        embed = discord.Embed(
            title=f'Short-term profit of {cryptocurrencie.upper()} (+**{difference_check}**)!',
            description=f'Right now it is recommended to **sell** R$**{difference_check}** worth of {asset_name}!!',
            color=0xffa07a
        )
        embed.add_field(
            name="", 
            value="Remember, make your sales with caution. If you believe this is a mistake, please contact my developer!",
            inline=False
        )

        discord_user = self.bot.get_user(int(user))
        if discord_user:
            await discord_user.send(embed=embed)

    async def run_in_executor(self, func, *args):
        return await self.bot.loop.run_in_executor(None, func, *args)

# async def setup(bot: commands.Bot) -> None:
#     await bot.add_cog(BackgroundTasks(bot))
