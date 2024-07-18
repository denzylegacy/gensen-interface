from pprint import pprint

from infra import log
from api import Coingecko
from api import Coinbase
from firebase import Firebase
from utils.encryptor import Encryptor


class ゲンセン:
    """Gensen -Golden Fountain-

    - Sell for every R$5.00 of profit (This value may be changed after future analysis.)
    - Supply:
      - Think about what the issue of gas depletion will be like (As with each sale the value of the crypto will be reduced)
    - Perform automatic analysis for low supply suggestion per token
    - Cover the initial cost invested
    - Obtain at least half of the capital invested apart from covering the same amount

    Considerations:
    * It must be necessary to input the assets and values for the assets
    for each sale, the machine must request confirmation of the sale, as long as the Coinbase API is not implemented
    This is to avoid problems (I'm in a hurry and I'm not going to explain them now...)
    
    * The user must be notified when to make the sale and purchase, and which assets
    * Create a watch list, so as soon as an asset falls below a certain percentage,
    a purchase notification is made
    """

    def __init__(self, user: str) -> tuple | None:
        self.user: str = user
    
    def get_user_credentials(self):
        firebase = Firebase()

        connection = firebase.firebase_connection("root")

        user_credentials = connection.child("users").get()

        if not user_credentials or not str(self.user) in user_credentials.keys():
            return
        
        return connection.child(
            f"users/{self.user}/credentials"
        ).get()

    def engine(
            self, base_asset_value: int, previous_asset_value: int, current_asset_value: int
        ) -> tuple:
        value_difference: int = (previous_asset_value * base_asset_value) / current_asset_value

        if value_difference >= self.profit:
            return value_difference, True
        else:
            return value_difference, False

    def convert_asset_to_brl(
            self, asset: str = None, brl_asset: int = None, available_balance_brl: float = None
        ) -> float:
        if not brl_asset:
            asset_data = Coingecko(
                coingecko_api_key=Encryptor().decrypt_api_key(self.user_credentials["coingecko_api_key"])
            ).coin_data_by_id(coind_id=asset)

            if not asset_data:
                return
          
            brl_asset: int = asset_data["market_data"]["current_price"]["brl"]

        _available_balance_brl = float(available_balance_brl) * int(brl_asset)

        return round(_available_balance_brl, 3)

    def user_asset_validator(self, asset: str) -> dict:

        user_credentials: dict = ゲンセン(user=self.user).get_user_credentials()

        asset_data = Coingecko(
            coingecko_api_key=Encryptor().decrypt_api_key(user_credentials["coingecko_api_key"])
        ).coin_data_by_id(coind_id=asset)

        if not asset_data:
            return
        
        usd: int = asset_data["market_data"]["current_price"]["usd"]
        brl: int = asset_data["market_data"]["current_price"]["brl"]

        client_asset_data: dict = Coinbase(
            api_key=Encryptor().decrypt_api_key(user_credentials["coinbase_api_key_name"]),
            api_secret=Encryptor().decrypt_api_key(user_credentials["coinbase_api_private_key"])
        ).asset_data(currency=asset_data["symbol"])

        asset_available_balance = client_asset_data["available_balance"]["value"]

        return {
            "available_balance": asset_available_balance, "brl": brl, "usd": usd,
        }

if __name__ == "__main__":
    gensen: object = ゲンセン()

    # print(gensen.user_asset_validator(asset="bitcoin"))

    print(
        gensen.convert_asset_to_brl(
            # asset="bitcoin", brl_asset=354449, available_balance=0.00139909
            asset="bitcoin", brl_asset=353241, available_balance=0.00139909
        )
    )