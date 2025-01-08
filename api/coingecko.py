# -*- coding: utf-8 -

import requests
from requests.models import Response
import time
from infra import log


class Coingecko:
    """Coingecko
    """

    def __init__(self, coingecko_api_key: str) -> None:
            self.coingecko_api_url: str = "https://api.coingecko.com/api/v3"
            self.coingecko_api_key: str = coingecko_api_key

    @log.function_log()
    def auth(self) -> int:
        headers = {
            "accept": "application/json", "x-cg-api-key": self.coingecko_api_key
        }

        response = requests.get(url=f"{self.coingecko_api_url}/ping", headers=headers)

        time.sleep(3)
        
        if response.status_code == 200:
            return response.status_code
        else:
            log.error(f"{response.status_code}, {response.text}")
            return

    @log.function_log()
    def coins_list(self) -> str:
        headers: dict = {
            "accept": "application/json", "x-cg-api-key": self.coingecko_api_key
        }

        response: Response = requests.get(
            url=f"{self.coingecko_api_url}/coins/list", headers=headers
        )

        return response.json()

    def coin_data_by_id(self, coind_id: str) -> dict | None:
        headers: dict = {
            "accept": "application/json", "x-cg-api-key": self.coingecko_api_key
        }

        response: Response = requests.get(
            url=f"{self.coingecko_api_url}/coins/{coind_id}", headers=headers
        )

        if int(str(response.status_code)[0]) == 2:
            return response.json()
        log.error(f"[coin_data_by_id] {response.status_code}: {response.text}")
        return

    def coin_market_data(self, coind_id: str) -> dict | None:
        coin_data = self.coin_data_by_id(coind_id=coind_id.strip().lower())

        if coin_data:
            return coin_data["market_data"]
        return

    @log.function_log()
    def coin_current_price_for_btc_usd_brl(self, coind_id: str) -> None | dict:
        coin_data = self.coin_data_by_id(coind_id=coind_id)

        if not coin_data:
            return
        
        btc: int = coin_data["market_data"]["current_price"]["btc"]
        usd: int = coin_data["market_data"]["current_price"]["usd"]
        brl: int = coin_data["market_data"]["current_price"]["brl"]

        log.info(f"btc: {btc}, usd: {usd}, brl: {brl}")

        return {
            "btc": btc, "usd": usd, "brl": brl
        }

    @log.function_log()
    def get_token_info(self) -> dict:
        token_id: str = ""
        url = f"{self.coingecko_api_url}/simple/token_price/{token_id}"

        headers: dict = {"accept": "application/json"}

        response: Response = requests.get(url, headers=headers)

        return response.json()


if __name__ == "__main__":
    coingecko: object = Coingecko()

    # coingecko.auth()
    # print(coingecko.coins_list())
    # print(coingecko.coin_data_by_id(coind_id="bitcoin"))
    # print(coingecko.coin_market_data(coind_id="bitcoin"))
    # coingecko.coin_current_price_for_btc_usd_brl(coind_id="bitcoin")
