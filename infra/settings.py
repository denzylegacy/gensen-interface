# -*- coding: utf-8 -*-

from typing import Any
from pathlib import Path
from local_io import JSONHandler
from dotenv import load_dotenv
import os

load_dotenv()


BASE_PATH = str(Path(__file__).resolve().parent.parent)

OPTIONS = JSONHandler().read_options_json(r"src/json/options.json")

### API KEYs
DISCORD_TOKEN: Any = os.getenv("DISCORD_TOKEN", "")

COINGECKO_API_KEY: Any = os.getenv("COINGECKO_API_KEY", "")

COINBASE_VIEW_API_KEY_NAME: Any = os.getenv("COINBASE_VIEW_API_KEY_NAME", "")

COINBASE_VIEW_API_KEY_PRIVATE_KEY: Any = os.getenv("COINBASE_VIEW_API_KEY_PRIVATE_KEY", "").replace("||", "\n")

### ENCRYPTATION_KEY
ENCRYPTATION_KEY: Any = os.getenv("ENCRYPTATION_KEY", "")

### FIREBASE
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY", "")
