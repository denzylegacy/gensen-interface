# -*- coding: utf-8 -*-

import jwt
from cryptography.hazmat.primitives import serialization
import time
import secrets
from coinbase.rest import RESTClient
from json import dumps

from dotenv import load_dotenv, set_key
from infra import log, COINBASE_VIEW_API_KEY_NAME, COINBASE_VIEW_API_KEY_PRIVATE_KEY

load_dotenv()


class CoinbaseAuth():
    """CoinbaseAuth
    """

    def __init__(self) -> None:
        self.request_method: str = "GET"
        self.request_host: str = "api.coinbase.com"
        self.request_path: str = "/api/v3/brokerage/accounts"

    def build_jwt(self):
            private_key = serialization.load_pem_private_key(
                data=COINBASE_VIEW_API_KEY_PRIVATE_KEY.encode('utf-8'), password=None
            )

            jwt_payload: dict = {
                'sub': COINBASE_VIEW_API_KEY_NAME,
                'iss': "cdp",
                'nbf': int(time.time()),
                'exp': int(time.time()) + 120,
                'uri': f"{self.request_method} {self.request_host}{self.request_path}",
            }

            jwt_token = jwt.encode(
                payload=jwt_payload,
                key=private_key,
                algorithm='ES256',
                headers={'kid': COINBASE_VIEW_API_KEY_NAME, 'nonce': secrets.token_hex()},
            )

            return jwt_token


    def auth(self) -> None:
        jwt_token = self.build_jwt()
        set_key(".env", "COINBASE_JWT_TOKEN", jwt_token)
        log.info("JWT TOKEN WAS BEEN CREATED!")

    
class Coinbase():
    """Coinbase
    """
    def __init__(self) -> None:
        self.auth = CoinbaseAuth().auth()
        self.client = RESTClient(
            api_key=COINBASE_VIEW_API_KEY_NAME,
            api_secret=COINBASE_VIEW_API_KEY_PRIVATE_KEY
        )

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


if __name__ == "__main__":
    coinbase = Coinbase()
    # print(coinbase.client_accounts())
    print(coinbase.account_balance_in_brl())
