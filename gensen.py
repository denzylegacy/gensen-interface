import requests
from pprint import pprint
from infra import log, COINGECKO_API_KEY


class ゲンセン:
    """
    Gensen -Fonte de Ouro-
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

    def coins_list(self):
        headers = {
            "accept": "application/json", "x-cg-api-key": self.coingecko_api_key
        }

        response = requests.get(url=f"{self.coingecko_api_url}/coins/list", headers=headers)
        
        log.info(response.text)

        return response.text
    
    def coin_data_by_id(self, coind_id: str) -> dict:
        headers = {
            "accept": "application/json", "x-cg-api-key": self.coingecko_api_key
        }

        response = requests.get(url=f"{self.coingecko_api_url}/coins/{coind_id}", headers=headers)

        return response.json()

    def coin_market_data(self, coind_id: str):
        coin_data = self.coin_data_by_id(coind_id=coind_id)
        return coin_data["market_data"]

    def coin_current_price_for_btc_usd_brl(self, coind_id: str):
        coin_data = self.coin_data_by_id(coind_id=coind_id)
        
        btc: int = coin_data["market_data"]["current_price"]["btc"]
        usd: int = coin_data["market_data"]["current_price"]["usd"]
        brl: int = coin_data["market_data"]["current_price"]["brl"]

        log.info(f"btc: {btc}, usd: {usd}, brl: {brl}")
        return

    def get_token_info(self):
        token_id: str = ""
        url = f"{self.coingecko_api_url}/simple/token_price/{token_id}"

        headers = {"accept": "application/json"}

        response = requests.get(url, headers=headers)

        print(response.text)
        return


if __name__ == "__main__":
    gensen = ゲンセン()
    # gensen.auth()
    # gensen.coins_list()
    # pprint(gensen.coin_data_by_id(coind_id="bitcoin"))
    # gensen.coin_market_data(coind_id="bitcoin")
    gensen.coin_current_price_for_btc_usd_brl(coind_id="bitcoin")
    