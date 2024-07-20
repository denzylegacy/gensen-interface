from typing import Any
import os
import json
import requests
import time
import hmac
import hashlib
from urllib.parse import urlencode

from infra import log


class Foxbit:

    def __init__(
        self, api_key: str, api_secret: str
        ) -> None:
        self.base_url: str = "https://api.foxbit.com.br"
        self.api_key = api_key
        self.api_secret = api_secret

    def sign(self, method, path, params, body) -> Any:
        queryString: str = ""
        if params:
            queryString = urlencode(params)

        rawBody: str = ""
        if body:
            rawBody = json.dumps(body)

        timestamp = str(int(time.time() * 1000))

        preHash = f"{timestamp}{method.upper()}{path}{queryString}{rawBody}"
        log.info(f"PreHash: {preHash}")

        signature = hmac.new(self.api_secret.encode(), preHash.encode(), hashlib.sha256).hexdigest()
        log.info(f"Signature: {preHash}")

        return signature, timestamp

    def request(self, method: str, path: str, params: Any, body: Any) -> Any:
        time.sleep(1)
        log.info("--------------------------------------------------")
        log.info(f"Requesting: ({method}) {path}")

        signature, timestamp = self.sign(method, path, params, body)

        url = self.base_url + path

        headers = {
            "X-FB-ACCESS-KEY": self.api_key,
            "X-FB-ACCESS-TIMESTAMP": timestamp,
            "X-FB-ACCESS-SIGNATURE": signature,
            "Content-Type": "application/json",
        }

        try:
            response = requests.request(method, url, params=params, json=body, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as http_err:
            log.error(
                f"HTTP Status Code: {http_err.response.status_code}, Error Response Body: {http_err.response.json()}",
            )
            return False
        except Exception as err:
            log.error(f"An error occurred: {err}")
            raise

    def check_currency(self, currency: str) -> bool | dict:
        currencies = self.request("GET", "/rest/v3/currencies", None, None)

        if not currencies:
            return False
        
        currency = currency.strip().lower()

        for asset in currencies["data"]:
            if asset["name"].lower() == currency or asset["symbol"].lower() == currency:
                return asset

    def convert_asset_to_brl(
            self, brl_asset: float = None, available_balance_brl: float = None
        ) -> float:
        _available_balance_brl = float(available_balance_brl) * float(brl_asset)
        return round(_available_balance_brl, 3)


if __name__ == "__main__":

    foxbit = Foxbit(
        api_key=os.getenv("FOXBIT_ACCESS_KEY"),
        api_secret=os.getenv("FOXBIT_SECRET_KEY")
    )

    print("FOXBIT_USER_ID", os.getenv("FOXBIT_USER_ID"))

    # Get user info
    # meResponse = foxbit.request("GET", "/rest/v3/me", None, None)
    # print("Response:")
    # pprint(meResponse)

    # List currencies
    # currencies = foxbit.request("GET", "/rest/v3/currencies", None, None)
    # print("Response:")
    # pprint(currencies)

    # print(currencies["data"])

    # User accounts
    # accounts = foxbit.request("GET", "/rest/v3/accounts", None, None)

    # currency = "near"

    # for account in accounts["data"]:
    #     if account["currency_symbol"] == currency:

    #         print(account)

    #         # Exemplo de cotação de venda
    #         params = {
    #             "side": "buy",
    #             "base_currency": currency,
    #             "quote_currency": "brl",
    #             "amount": "1"
    #         }
            
    #         quote_sell = foxbit.request("GET", "/rest/v3/markets/quotes", params=params, body=None)
    #         print("Cotação de venda:", quote_sell)

    #         print(foxbit.convert_asset_to_brl(
    #             brl_asset=float(account["balance_available"]), 
    #             available_balance_brl=float(quote_sell["price"])))
    #         break

    # ### ORDERKAMER ###
    # currency = "sol"
    
    # order = {
    #         "market_symbol": f"{currency}brl",
    #         "side": "SELL",
    #         "type": "INSTANT",
    #         "amount": "5.00"
    #     }
    
    # orderResponse = foxbit.request("POST", "/rest/v3/orders", None, body=order)
    # print('Response:', orderResponse)

    # currency = "btc"

    # for account in accounts["data"]:
    #     if account["currency_symbol"] == currency:
    #         print(account["balance_available"])

    # order = {
    #     'market_symbol': 'btcbrl',
    #     'side': 'BUY',
    #     'type': 'LIMIT',
    #     # 'price': '3.0',
    #     'quantity': '0.00001',
    # }
    # order = {
    #     "side": "BUY",
    #     "type": "INSTANT",
    #     "market_symbol": "btcbrl",
    #     "client_order_id": os.getenv("FOXBIT_USER_ID"),
    #     "remark": "A remarkable note for the order.",
    #     "amount": "0.00001"
    # }
    
    # orderResponse = foxbit.request('POST', '/rest/v3/orders', None, order)
    # print('Response:', orderResponse)
