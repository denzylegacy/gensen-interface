# -*- coding: utf-8 -*-

import jwt
from cryptography.hazmat.primitives import serialization
import time
import uuid
import math
import secrets
from json import dumps
from coinbase.rest import RESTClient
from dotenv import load_dotenv, set_key
from infra import log

load_dotenv()


class CoinbaseAuth():
    """CoinbaseAuth
    """
    def __init__(self, api_key: str, api_secret: str) -> None:
        self.request_method: str = "GET"
        self.request_host: str = "api.coinbase.com"
        self.request_path: str = "/api/v3/brokerage/accounts"
        self.api_key: str = api_key
        self.api_secret: str = api_secret

    def build_jwt(self):
            private_key = serialization.load_pem_private_key(
                data=self.api_secret.encode('utf-8'), password=None
            )

            jwt_payload: dict = {
                'sub': self.api_key,
                'iss': "cdp",
                'nbf': int(time.time()),
                'exp': int(time.time()) + 120,
                'uri': f"{self.request_method} {self.request_host}{self.request_path}",
            }

            jwt_token = jwt.encode(
                payload=jwt_payload,
                key=private_key,
                algorithm='ES256',
                headers={'kid': self.api_key, 'nonce': secrets.token_hex()},
            )

            return jwt_token


    def auth(self):
        try:
            jwt_token = self.build_jwt()
            # set_key(".env", "COINBASE_JWT_TOKEN", jwt_token)
            log.info(f"COINBASE JWT TOKEN WAS BEEN CREATED! {jwt_token}")
            return jwt_token
        except:
            return

    
class Coinbase(CoinbaseAuth):
    """Coinbase
    doc: https://docs.cdp.coinbase.com/advanced-trade/docs/sdk-rest-client-trade
    """
    def __init__(self, api_key: str, api_secret: str) -> None:
        super().__init__(api_key=api_key, api_secret=api_secret)
        self.client = RESTClient(api_key=api_key, api_secret=api_secret)

    def client_accounts(self) -> dict:
        accounts = self.client.get_accounts()
        return dumps(accounts, indent=2)

    def account_balance_in_brl(self) -> dict | None:
        accounts = self.client.get_accounts()

        if accounts:
            for account in accounts["accounts"]:
                if account["currency"] == "BRL":
                    return account
        return None

    def asset_data(self, currency: str) -> dict | None:
        accounts = self.client.get_accounts()

        if accounts:
            for account in accounts["accounts"]:
                if account["currency"] == currency.upper():
                    return account
        return None

    def placing_market_order(
            self, base_currency: str = "BTC", quote_currency: str = "BRL",
            quote_size: int = 1,
        ) -> dict:
        order = self.client.market_order_buy(
            client_order_id=str(uuid.uuid4())[:8],
            product_id=f"{base_currency}-{quote_currency}",
            quote_size=str(quote_size)
        )

        fills = self.client.get_fills(order_id=order["order_id"])
        return dumps(fills, indent=2)

    def placing_limit_buy_order(
            self, base_currency: str = "BTC", quote_currency: str = "BRL",
    ) -> str:
        product = self.client.get_product(f"{base_currency}-{quote_currency}")

        btc_usd_price = float(product["price"])

        adjusted_btc_usd_price = str(math.floor(btc_usd_price - (btc_usd_price * 0.05)))

        return adjusted_btc_usd_price
    
    def placing_order_5_percent_below_price(
            self, base_currency: str = "BTC", quote_currency: str = "BRL",
            quote_size: str = "0.0002",
    ):
        adjusted_btc_usd_price = self.placing_limit_buy_order(
            base_currency=base_currency, quote_currency=quote_currency
        )

        limit_order = self.client.limit_order_gtc_buy(
            client_order_id=str(uuid.uuid4())[:8],
            product_id=f"{base_currency}-{quote_currency}",
            base_size=quote_size,
            limit_price=adjusted_btc_usd_price
        )

        return limit_order["order_id"]

    def cancelling_the_order(self, limit_order_id):
        return self.client.cancel_orders(order_ids=[limit_order_id])


if __name__ == "__main__":
    coinbase = Coinbase()

    print(coinbase.auth())
    # print(coinbase.client_accounts())
    # print(coinbase.account_balance_in_brl())
    # print(coinbase.asset_data(asset="NEAR"))
