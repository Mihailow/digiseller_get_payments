import hmac

from payment_systems import *
import db


# получить код страны по ip
async def get_country_code(ip: str):
    endpoint = f"https://ipinfo.io/{ip}/json"
    response = requests.get(endpoint, verify=True)
    if response.status_code != 200:
        return "no_country"
    data = response.json()
    if "country" not in data:
        return "no_country"
    return data["country"]


# по данных из json создает в базе запись и возвращает url
async def create_invoice_url(data: dict):
    print('data', data)
    if not {'invoice_id', 'amount', 'currency', 'description', 'lang', 'email', 'payment_id', 'owner', 'receipt', 'return_url'}.issubset(data):
        return "error"
    payment_system = await db.get_payment_system(data["payment_id"])
    if not payment_system:
        return "error"
    data["amount"] = float(data["amount"]) + float(payment_system["amount"]) + float(data["amount"])*float(payment_system["percent"])/100
    await db.insert_order(data["invoice_id"], data["amount"], data["currency"], data["description"], data["lang"],
                          data["email"], data["payment_id"], data["owner"], data["receipt"]["receipt"], data["return_url"], payment_system["percent"], payment_system["amount"])
    if payment_system["description"].startswith("Antilopay"):
        if payment_system["description"] == "Antilopay":
            payment_system["description"] = "Antilopay_"
        response = await Antilopay.create_payment(float(data["amount"]), str(data["invoice_id"]), str(data["currency"]), str(data["receipt"]["receipt"][0]["description"]), str(data["email"]), str(data["description"]), str(data["return_url"]), payment_system["description"].replace("Antilopay_", ""))
        try:
            await db.update_order_id_order_payment(data["invoice_id"], response["payment_id"])
            print(response)
            return response["payment_url"]
        except:
            print(response)
            return "error"
    elif payment_system["description"].startswith("Cryptomus"):
        if payment_system["description"] == "Cryptomus":
            payment_system["description"] = "Cryptomus_"
        response = await Cryptomus.create_payment(float(data["amount"]), str(data["invoice_id"]), str(data["currency"]), str(data["return_url"]), payment_system["description"].replace("Cryptomus_", ""))
        try:
            await db.update_order_id_order_payment(data["invoice_id"], response.uuid)
            print(response)
            return response.url
        except:
            print(response)
            return "error"
    elif payment_system["description"] == "BinancePay":
        if str(data["currency"]) == "USD":
            data["currency"] = "USDT"
        response = await BinancePay.create_payment(float(data["amount"]), str(data["invoice_id"]), str(data["currency"]), str(data["return_url"]), str(data["receipt"]["receipt"][0]["id"]), str(data["receipt"]["receipt"][0]["description"]))
        try:
            await db.update_order_id_order_payment(data["invoice_id"], response["data"]["prepayId"])
            print(response)
            return response["data"]["universalUrl"]
        except:
            print(response)
            return "error"
    elif payment_system["description"] == "Wata":
        response = await Wata.create_payment(str(data["invoice_id"]), float(data["amount"]), str(data["description"]), str(data["return_url"]), str(data["currency"]))
        try:
            await db.update_order_id_order_payment(data["invoice_id"], response["transaction_uuid"])
            print(response)
            return response["acquiring_page"]
        except:
            print(response)
            return "error"
    elif payment_system["description"] == "P2p":
        response = await P2p.create_payment(str(data["invoice_id"]), float(data["amount"]), str(data["return_url"]), str(data["currency"]))
        try:
            await db.update_order_id_order_payment(data["invoice_id"], response["id"])
            print(response)
            return response["link"]
        except:
            print(response)
            return "error"
    elif payment_system["description"] == "Gmpays":
        payment_link = await Gmpays.create_payment(str(data["invoice_id"]), float(data["amount"]), str(data["description"]),  str(data["return_url"]), str(data["currency"]))
        try:
            print(payment_link)
            return payment_link
        except:
            print(payment_link)
            return "error"
    elif payment_system["description"] == "B2pay":
        response = await B2pay.create_payment(str(data["invoice_id"]), float(data["amount"]), str(data["currency"]), "", str(data["return_url"]), str(data["email"]))
        try:
            print(response)
            return response["data"]["url"]
        except:
            print(response)
            return "error"
    elif payment_system["description"].startswith("Paypalych"):
        response = await Paypalych.create_payment(str(data["invoice_id"]), float(data["amount"]), str(data["description"]), str(data["return_url"]), str(data["currency"]), str(data["email"]), payment_system["description"].replace("Paypalych_", ""))
        try:
            await db.update_order_id_order_payment(data["invoice_id"], response["bill_id"])
            print(response)
            return response["link_page_url"]
        except:
            print(response)
            return "error"
    else:
        return "error"
    

async def generate_signature(data_dict, secret_key):
    """
    Функция для генерации подписи HMAC по алгоритму RFC 2104 и с учётом правила формирования строки
    data_dict: словарь с данными для формирования строки
    secret_key: секретный ключ
    """
    # Сортируем ключи по алфавиту и формируем строку по правилу "ключ:значение;"
    sorted_data = sorted(data_dict.items())
    data_string = ''.join([f"{key}:{value};" for key, value in sorted_data])

    # Преобразуем секретный ключ и строку данных в байты
    secret_key_bytes = bytes(secret_key, 'utf-8')
    data_string_bytes = data_string.encode()

    # Формируем HMAC с использованием алгоритма SHA256
    hmac_signature = hmac.new(secret_key_bytes, data_string_bytes, hashlib.sha256)

    # Возвращаем результат в формате HEX
    return hmac_signature.hexdigest().upper()