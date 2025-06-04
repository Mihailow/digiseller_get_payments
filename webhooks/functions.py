import hmac

from payment_systems import *


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


async def send_order_status(invoice_id, amount, currency, status):
    url = "https://digiseller.market/callback/api"
    data = {
        "invoice_id": invoice_id,
        "amount": amount,
        "currency": currency,
        "status": status
    }
    sign = await generate_signature(data, SECRET)
    response = {
        "invoice_id": invoice_id,
        "amount": amount,
        "currency": currency,
        "status": status,
        "signature": sign,
        "error": ""
    }
    requests.get(url=url, params=response)
    print('send\n')
