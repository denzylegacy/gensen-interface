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


class MarketConditionsEvaluator:
    def __init__(self):
        self.current_dir = Path(__file__).resolve().parent
        self.json_db = JsonDB(BASE_PATH + "/instance/db.json")

    async def evaluate_market_conditions(self):
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
                continue
        
            for exchange in users[user]["exchanges"].keys():
                for cryptocurrency in users[user]["exchanges"][exchange]["cryptocurrencies"].keys():
                    asset = users[user]["exchanges"][exchange]["cryptocurrencies"][cryptocurrency]

                    foxbit = Foxbit(
                        api_key=Encryptor().decrypt_api_key(user_credentials["FOXBIT_ACCESS_KEY"]),
                        api_secret=Encryptor().decrypt_api_key(user_credentials["FOXBIT_SECRET_KEY"])
                    )

                    accounts = foxbit.request("GET", "/rest/v3/accounts", None, None)

                    for account in accounts["data"]:
                        if account["currency_symbol"] == cryptocurrency:
                            params = {
                                "side": "buy",
                                "base_currency": cryptocurrency,
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
                            
                            log.info(f"{difference_check}: {cryptocurrency} -> {user}")

                            if (
                                float(asset_available_value_brl) >= 
                                float(asset["base_balance"]) + 
                                (float(asset["fixed_profit_brl"]) + 0.3)
                            ):
                                if ENVIRONMENT == "SERVER":
                                    order = {
                                        "market_symbol": f"{cryptocurrency}brl",
                                        "side": "SELL",
                                        "type": "INSTANT",
                                        "amount": "5.00"
                                    }
                                    
                                    order_response = foxbit.request("POST", "/rest/v3/orders", None, body=order)
                                    
                                    timestamp = datetime.datetime.now(
                                        pytz.timezone("America/Sao_Paulo")
                                    ).strftime("%Y-%m-%d %H:%M:%S")
                                                    
                                    log.info(f"[{timestamp}] ORDER RESPONSE: {order_response}")
                                
                                    log.info(f"[INSTANT ORDER NOTIFICATION] {cryptocurrency} -> {user}")
                                    
                                    await asyncio.sleep(1)

async def main():
    evaluator = MarketConditionsEvaluator()
    while True:
        await evaluator.evaluate_market_conditions()
        await asyncio.sleep(30)


if __name__ == "__main__":
    asyncio.run(main())
