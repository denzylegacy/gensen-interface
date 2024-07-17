from pprint import pprint

from infra import log
from coingecko import Coingecko


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
    This is to avoid problems (I'm sorry and I'm not going to explain them now...)

    * The user must be notified when to make the sale and purchase, and which assets
    * Create a watch list, so as soon as an asset falls below a certain percentage,
    a purchase notification is made
    """

    def __init__(self) -> tuple | None:
        self.profit: int = 5
    
    def engine(
            self, base_asset_value: int, previous_asset_value: int, current_asset_value: int
        ) -> tuple:
        value_difference: int = (previous_asset_value * base_asset_value) / current_asset_value

        if value_difference >= self.profit:
          return value_difference, True
        else:
            return value_difference, False


if __name__ == "__main__":
    gensen: object = ゲンセン()
