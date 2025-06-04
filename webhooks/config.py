from dotenv import load_dotenv
import os

load_dotenv()

ANTILIOPAY_SECRET = os.environ.get("ANTILIOPAY_SECRET")
ANTILIOPAY_SECRET_ID = os.environ.get("ANTILIOPAY_SECRET_ID")
ANTILIOPAY_PROJECT_IDENTIFICATOR = os.environ.get("ANTILIOPAY_PROJECT_IDENTIFICATOR")

CRYPTOMUS_MERCHANT_ID = os.environ.get("CRYPTOMUS_MERCHANT_ID")
CRYPTOMUS_API_KEY = os.environ.get("CRYPTOMUS_API_KEY")

BINANCE_PAY_KEY = os.environ.get("BINANCE_PAY_KEY")
BINANCE_PAY_SECRET = os.environ.get("BINANCE_PAY_SECRET")

WATA_TOKEN = os.environ.get("WATA_TOKEN")

P2P_API = os.environ.get("P2P_API")

GMPAYS_HMAC_KEY = os.environ.get("GMPAYS_HMAC_KEY")
GMPAYS_PROJECT_ID = os.environ.get("GMPAYS_PROJECT_ID")

B2PAY_ENCRYPTION_IV = os.environ.get("B2PAY_ENCRYPTION_IV")
B2PAY_ENCRYPTION_PASSWORD = os.environ.get("B2PAY_ENCRYPTION_PASSWORD")

PAYPALYCH_SHOP_ID = os.environ.get("PAYPALYCH_SHOP_ID")
PAYPALYCH_TOKEN = os.environ.get("PAYPALYCH_TOKEN")

SECRET = os.environ.get("SECRET")
