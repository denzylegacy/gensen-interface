import discord
from discord.ext import commands, tasks
import datetime
import pytz
import asyncio
from pathlib import Path

from infra import log
from infra.settings import BASE_PATH, ENVIRONMENT
from crud import JsonDB
from firebase import Firebase
from api.foxbit import Foxbit
from utils.encryptor import Encryptor


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
            user_credentials = connection.child(
                f"users/{user}/exchanges/foxbit/credentials"
            ).get()
            
            if not user_credentials:
                return
        
            for exchange in users[user]["exchanges"].keys():
                for cryptocurrencie in users[user]["exchanges"][exchange]["cryptocurrencies"].keys():
                    asset = users[user]["exchanges"][exchange]["cryptocurrencies"][cryptocurrencie]

                    foxbit = Foxbit(
                        api_key=Encryptor().decrypt_api_key(user_credentials["FOXBIT_ACCESS_KEY"]),
                        api_secret=Encryptor().decrypt_api_key(user_credentials["FOXBIT_SECRET_KEY"])
                    )

                    accounts = foxbit.request("GET", "/rest/v3/accounts", None, None)

                    for account in accounts["data"]:
                        if account["currency_symbol"] == cryptocurrencie:
                            params = {
                                "side": "buy",
                                "base_currency": cryptocurrencie,
                                "quote_currency": "brl",
                                "amount": "1"
                            }
                            
                            quote_sell = foxbit.request(
                                "GET", "/rest/v3/markets/quotes", params=params, body=None
                            )

                            asset_available_value_brl = foxbit.convert_asset_to_brl(
                                brl_asset=float(account["balance_available"]),
                                available_balance_brl=float(quote_sell["price"])
                            )

                            difference_check: float = round(
                                float(asset_available_value_brl) - 
                                float(asset["base_balance"]), 3
                            )
                            
                            log.info(f"{difference_check}: {cryptocurrencie} -> {user}")

                            if (
                                float(asset_available_value_brl) >= 
                                float(asset["base_balance"]) + 
                                (float(asset["fixed_profit_brl"]) + 0.3)
                                ):

                                if ENVIRONMENT == "SERVER":
                                    order = {
                                        "market_symbol": f"{cryptocurrencie}brl",
                                        "side": "SELL",
                                        "type": "INSTANT",
                                        "amount": "5.00"
                                    }
                                    
                                    orderResponse = foxbit.request("POST", "/rest/v3/orders", None, body=order)
                                    
                                    timestamp = datetime.datetime.now(
                                        pytz.timezone("America/Sao_Paulo")
                                    ).strftime("%Y-%m-%d %H:%M:%S")
                                                    
                                    log.info(f"[{timestamp}] ORDER RESPONSE: {orderResponse}")
                                
                                    ### DM NOTIFICATION ###

                                    log.info(f"[INSTANT ORDER NOTIFICATION] {cryptocurrencie} -> {user}")
                                    
                                    embed = discord.Embed(
                                        title=f'Short-term profit of {cryptocurrencie.upper()} (+**{difference_check}**)!',
                                        description=f'At that very moment I made a sale of R$**{difference_check}** worth of {asset["name"]}!!',
                                        color=0xffa07a
                                    )

                                    embed.add_field(
                                        name="", 
                                        value="Remember, make your sales with caution. If you believe this is a mistake, please contact my developer!",
                                        inline=False
                                    )

                                    await self.bot.get_user(int(user)).send(embed=embed)
                                    await asyncio.sleep(1)

    @tasks.loop(seconds=30)
    async def background_tasks(self):
        await self.market_conditions_evaluator()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BackgroundTasks(bot))
