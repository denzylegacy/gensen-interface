# -*- coding: utf-8 -*-

from pathlib import Path
from local_io import JSONHandler
from dotenv import load_dotenv
import os

load_dotenv()


BASE_PATH = str(Path(__file__).resolve().parent.parent)

OPTIONS = JSONHandler().read_options_json(r"src/json/options.json")

# API KEYs
COINGECKO_API_KEY: str = os.getenv("COINGECKO_API_KEY", "")
DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
