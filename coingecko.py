# -*- coding: utf-8 -

import requests
from requests.models import Response
from infra import log, COINGECKO_API_KEY


class Coingecko:
    """Coingecko
    """

    def __init__(self) -> None:
            self.coingecko_api_url: str = "https://api.coingecko.com/api/v3"
            self.coingecko_api_key: str = COINGECKO_API_KEY

    def auth(self) -> int:
        headers = {
            "accept": "application/json", "x-cg-api-key": self.coingecko_api_key
        }

        response = requests.get(url=f"{self.coingecko_api_url}/ping", headers=headers)

        if response.status_code == 200:
            log.info(response.json())
            return response.status_code
        else:
            log.error(f"{response.status_code}, {response.text}")
            return response.status_code

    def coins_list(self) -> str:
        headers: dict = {
            "accept": "application/json", "x-cg-api-key": self.coingecko_api_key
        }

        response: Response = requests.get(
            url=f"{self.coingecko_api_url}/coins/list", headers=headers
        )

        return response.json()

    def coin_data_by_id(self, coind_id: str) -> dict:
        headers: dict = {
            "accept": "application/json", "x-cg-api-key": self.coingecko_api_key
        }

        response: Response = requests.get(
            url=f"{self.coingecko_api_url}/coins/{coind_id}", headers=headers
        )

        return response.json()

    def coin_market_data(self, coind_id: str):
        coin_data: dict = self.coin_data_by_id(coind_id=coind_id)
        return coin_data["market_data"]

    def coin_current_price_for_btc_usd_brl(self, coind_id: str) -> dict:
        coin_data = self.coin_data_by_id(coind_id=coind_id)

        btc: int = coin_data["market_data"]["current_price"]["btc"]
        usd: int = coin_data["market_data"]["current_price"]["usd"]
        brl: int = coin_data["market_data"]["current_price"]["brl"]

        log.info(f"btc: {btc}, usd: {usd}, brl: {brl}")

        return {
            "btc": btc, "usd": usd, "brl": brl
        }

    def get_token_info(self) -> dict:
        token_id: str = ""
        url = f"{self.coingecko_api_url}/simple/token_price/{token_id}"

        headers: dict = {"accept": "application/json"}

        response: Response = requests.get(url, headers=headers)

        return response.json()


if __name__ == "__main__":
    coingecko: object = Coingecko()

    # coingecko.auth()
    print(len(coingecko.coins_list()))
    # pprint(coingecko.coin_data_by_id(coind_id="bitcoin"))
    # coingecko.coin_market_data(coind_id="bitcoin")
    # coingecko.coin_current_price_for_btc_usd_brl(coind_id="bitcoin")
