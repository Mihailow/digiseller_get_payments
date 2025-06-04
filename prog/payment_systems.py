import asyncio
import json
import hashlib
import math

import requests
import base64
from Crypto.Hash import SHA256, HMAC
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from CryptomusAPI import Cryptomus as Cryptomus_api
from binance.pay.merchant import Merchant as Client

from config import *


class Antilopay:
    async def create_signature(str_payload: dict):
        str_payload = json.dumps(str_payload)
        rsa_key = RSA.importKey(base64.b64decode(ANTILIOPAY_SECRET))
        payload = bytes(str_payload, 'UTF-8')
        hash = SHA256.new(payload)
        signature = base64.b64encode(pkcs1_15.new(rsa_key).sign(hash))
        return signature, payload

    async def check_signature(signature: bytes, payload: bytes):
        url = "https://lk.antilopay.com/api/v1/signature/check"
        headers = {"X-Apay-Secret-Id": ANTILIOPAY_SECRET_ID, "X-Apay-Sign": signature}
        resp = requests.post(url, data=payload, headers=headers)
        resp = resp.json()
        if "status" in resp and resp["status"] == "ok":
            return True
        return False

    @staticmethod
    async def create_payment(amount: float, order_id: str, currency: str, product_name: str, email: str, description: str, success_url: str, prefer_methods: str):
        if prefer_methods == "":
            prefer_methods = ["CARD_RU", "SBER_PAY", "SBP"]
        else:
            prefer_methods = [prefer_methods]
        url = "https://lk.antilopay.com/api/v1/payment/create"
        str_payload = {
            "project_identificator": ANTILIOPAY_PROJECT_IDENTIFICATOR,  # Идентификатор проекта мерчанта
            "amount": amount,  # Сумма платежа
            "order_id": order_id,  # Идентификатор платежа на стороне мерчанта. Должен быть уникальным
            "currency": currency,  # Валюта. Только "RUB"
            "product_name": description,  # Название товара/услуги
            "product_type": "goods",  # Принимает значения: "goods", "services"
            # "vat": 10,  # Необязательно. Ставка ндс, возможные значения: 10, 20. Поле обязательное, если сно - ОСНО
            "description": description,  # Описание платежа
            "success_url": success_url,  # Необязательно. URL переадресации покупателя после успешной оплаты
            "customer": {  # Данные покупателя
                "email": email},  # Электронная почта покупателя. Если указан phone, то можно пропустить
            "prefer_methods": prefer_methods
        }
        signature, payload = await Antilopay.create_signature(str_payload)
        if not await Antilopay.check_signature(signature, payload):
            return {"error": "error in check_signature"}
        headers = {"X-Apay-Secret-Id": ANTILIOPAY_SECRET_ID, "X-Apay-Sign": signature}
        resp = requests.post(url, data=payload, headers=headers)
        return resp.json()

    @staticmethod
    async def check_payment(order_id: str):
        url = "https://lk.antilopay.com/api/v1/payment/check"
        str_payload = {
            "project_identificator": ANTILIOPAY_PROJECT_IDENTIFICATOR,  # Идентификатор проекта мерчанта
            "order_id": order_id  # Идентификатор платежа на стороне мерчанта. Должен быть уникальным
        }
        signature, payload = await Antilopay.create_signature(str_payload)
        if not await Antilopay.check_signature(signature, payload):
            return {"error": "error in check_signature"}
        headers = {"X-Apay-Secret-Id": ANTILIOPAY_SECRET_ID, "X-Apay-Sign": signature}
        resp = requests.post(url, data=payload, headers=headers)
        return resp.json()


class Cryptomus:
    @staticmethod
    async def create_payment(summ, order_id, currency, url_success, network):
        if network == "":
            invoice = await Cryptomus_api(CRYPTOMUS_MERCHANT_ID, CRYPTOMUS_API_KEY).payments.create_invoice(
                amount=summ,
                order_id=order_id,  # This parameter must not contain spaces.
                currency=currency,  # or crypto currency like TON
                url_success=url_success,  # перенапрваляет пользователя после оплаты
                url_callback="https://payments.playhaslimits.store/cryptomus/webhook"  # сюда приходит уведомление после оплаты или ошибки
            )
        else:
            invoice = await Cryptomus_api(CRYPTOMUS_MERCHANT_ID, CRYPTOMUS_API_KEY).payments.create_invoice(
                amount=summ,
                order_id=order_id,  # This parameter must not contain spaces.
                currency="USDT",  # or crypto currency like TON
                url_success=url_success,  # перенапрваляет пользователя после оплаты
                url_callback="https://payments.playhaslimits.store/cryptomus/webhook",  # сюда приходит уведомление после оплаты или ошибки
                network=network
            )
        return invoice.result

    @staticmethod
    async def check_payment(uuid, order_id):
        invoice = await Cryptomus_api(CRYPTOMUS_MERCHANT_ID, CRYPTOMUS_API_KEY).payments.info(
            uuid=uuid,
            order_id=order_id
        )
        return invoice.result


class BinancePay:
    @staticmethod
    async def create_payment(summ: float, order_id: str, currency: str, returnUrl: str, goods_id: str, goods_name: str):
        parameters = {
            "env": {
                "terminalType": "WEB"
            },
            "merchantTradeNo": order_id,
            "orderAmount": summ,
            "currency": currency,
            "goods": {
                "goodsType": "02",
                "goodsCategory": "Z000",
                "referenceGoodsId": goods_id,
                "goodsName": goods_name
            },
            "returnUrl": returnUrl,
            "webhookUrl": "https://payments.playhaslimits.store/binancepay/webhook"
        }

        response = Client(BINANCE_PAY_KEY, BINANCE_PAY_SECRET).new_order(parameters)
        return response

    @staticmethod
    async def check_payment(order_id):
        response = Client(BINANCE_PAY_KEY, BINANCE_PAY_SECRET).get_order(merchantTradeNo=order_id)
        return response


class Wata:
    # Создание платежа
    @staticmethod
    async def create_payment(merchant_order_id: str, amount: float, description: str, success_url: str, currency: str):
        url = "https://acquiring.foreignpay.ru/webhook/partner_sbp/transaction"
        headers = {
            'Authorization': f"Bearer {WATA_TOKEN}",
            'Content-Type': 'application/json'
        }
        if success_url is None:
            success_url = "https://pay.playhaslimits.store/order_success"
        data = {
            # Сумма
            "amount": amount,
            # Описание
            "description": description,
            # можно удалить
            "success_url": success_url,
            # валюта (USD, EUR, GBP), можно удалить
            "currency": currency,
            # номер заказа в нашей системе, можно удалить
            "merchant_order_id": merchant_order_id
        }
        response = requests.post(url, headers=headers, json=data)
        return response.json()

    @staticmethod
    async def check_payment(order_id):
        url = "https://acquiring.foreignpay.ru/webhook/check_transaction"
        headers = {
            'Authorization': f"Bearer {WATA_TOKEN}",
            'Content-Type': 'application/json'
        }
        data = {
            # номер транзакции в платежной системе
            "transaction_uuid": order_id
        }
        response = requests.post(url, headers=headers, json=data)
        return response.json()


class P2p:
    @staticmethod
    async def create_payment(order_id: str, amount: float, success_url: str, currency: str):
        project_id = 65  # ID проекта
        order_id = order_id
        amount = amount
        method = 'sbp'  # Метод оплаты (Банковская карта (card) или СБП QR-код (sbp))
        currency = currency  # Валюта платежа (RUB или USD)
        api_code = P2P_API  # api
        success_url = success_url  # Редирект на страницу успеха (в случае прохождения оплаты)
        failed_url = success_url  # Редирект на страницу неуспеха (в случае непрохождения оплаты)
        callback_url = 'https://payments.playhaslimits.store/p2p/webhook'  # Коллбек

        data = {
            'project_id': project_id,
            'order_id': order_id,
            'amount': amount,
            'currency': currency,
            'method': method,
            'success_url': success_url,
            'failed_url': failed_url,
            'callback_url': callback_url,
        }

        jsonData = json.dumps(data)

        join_string = f'{api_code}{order_id}{project_id}{amount:.2f}{currency}'
        auth_token = hashlib.sha512(join_string.encode('utf-8')).hexdigest()

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {auth_token}'
        }

        response = requests.post('https://p2pkassa.live/api/v1/acquiring', headers=headers, data=jsonData)
        return response.json()

    @staticmethod
    async def check_payment(data):
        project_id = 65
        join_string = f"{P2P_API}{data['id']}{data['order_id']}{project_id}{data['amount']:.2f}{data['currency']}"
        check_sign = hashlib.sha256(join_string.encode('utf-8')).hexdigest()

        if check_sign == data.get('sign'):
            return True
        else:
            return False


class Gmpays:
    @staticmethod
    async def sign(data_set):
        data_set.pop('signature', None)
        sorted_data = dict(sorted(data_set.items()))
        data_str = ""
        for data in sorted_data:
            data_str += data + ":" + sorted_data[data]+";"

        hash_func = HMAC.new(GMPAYS_HMAC_KEY.encode('utf-8'), digestmod=SHA256)
        hash_func.update(data_str.encode('utf-8'))

        return hash_func.hexdigest()

    @staticmethod
    async def create_payment(order_id: str, amount: float, description: str, success_url: str, currency: str):
        url = "https://pay.gmpays.com/api/terminal/create"
        # url = "https://paygate.gamemoney.com/invoice"
        data = {
            "project": GMPAYS_PROJECT_ID,
            "user": order_id,
            "amount": str(amount),
            "comment": description,
            "success_url": success_url,
            "fail_url": success_url,
            "project_invoice": order_id,
            "currency": currency
        }
        data["signature"] = await Gmpays.sign(data)

        resp = requests.post(url, data=data)
        payment_url = resp.url
        return payment_url

    @staticmethod
    async def check_payment(order_id):
        url = "https://paygate.gamemoney.com/invoice/status"
        data = {
            "project": GMPAYS_PROJECT_ID,
            "project_invoice": order_id
        }
        data["signature"] = await Gmpays.sign(data)

        resp = requests.post(url, data=data)
        return resp.json()


class B2pay:
    @staticmethod
    async def sign(data_set):
        data_set.pop('sign', None)
        sorted_data = dict(sorted(data_set.items()))
        values = list(sorted_data.values())
        values.append(B2PAY_ENCRYPTION_PASSWORD)
        sign_string = ':'.join(map(str, values))
        hash_func = hashlib.md5()
        hash_func.update(sign_string.encode('utf-8'))
        sign_string = hash_func.digest()
        return base64.b64encode(sign_string).decode('utf-8')

    @staticmethod
    async def encrypt(string):
        pw = hashlib.sha256(B2PAY_ENCRYPTION_PASSWORD.encode()).hexdigest()[:32].encode()
        iv = hashlib.sha256(B2PAY_ENCRYPTION_IV.encode()).hexdigest()[:16].encode()

        pad = lambda s: s + chr(16 - len(s) % 16) * (16 - len(s) % 16)
        cipher = AES.new(pw, AES.MODE_CBC, iv)

        encrypted = base64.b64encode(cipher.encrypt(pad(string).encode())).decode()
        output = base64.b64encode(encrypted.encode()).decode()

        return output

    @staticmethod
    async def create_payment(order_number: str, amount: float, currency: str, description: str, success_url: str, email: str):
        amount = math.ceil(amount*100)/100
        url = "https://api.b2pay.io/merchantpayments.php"
        payment_json = {
            "amount": amount,
            "currency": currency,
            "description": description,
            "order_number": order_number,
            "type_payment": "merchant",
            "usr": "new",
            "custom_field": "",
            "callback_url": base64.b64encode(b"https://payments.playhaslimits.store/b2pay/webhook").decode(),
            "customer_email": email,
            "success_url": base64.b64encode(success_url.encode()).decode()
        }

        payment_json["signature"] = await B2pay.sign(payment_json)
        payment_str = json.dumps(payment_json, ensure_ascii=False, separators=(',', ':'))

        payment_encrypt = await B2pay.encrypt(payment_str)

        data = {"payment": payment_encrypt, "id": 1173}
        resp = requests.post(url, data=data)

        return resp.json()


class Paypalych:
    @staticmethod
    async def create_payment(order_id: str, amount: float, description: str, success_url: str, currency: str, email: str, payment_method: str):
        url = 'https://palych.io/api/v1/bill/create'
        params = {
            'amount': amount,
            'order_id': order_id,
            'description': description,
            'shop_id': PAYPALYCH_SHOP_ID,
            "currency_in": currency,
            "payer_email": email,
            "success_url": success_url,
            "payment_method": payment_method
        }
        headers = {'Authorization': f'Bearer {PAYPALYCH_TOKEN}'}
        resp = requests.post(url, json=params, headers=headers)
        return resp.json()

    @staticmethod
    async def check_payment(order_id: str):
        url = 'https://palych.io/api/v1/payment/status'
        params = {'id': order_id}
        headers = {'Authorization': f'Bearer {PAYPALYCH_TOKEN}'}
        resp = requests.post(url, json=params, headers=headers)
        return resp.json()