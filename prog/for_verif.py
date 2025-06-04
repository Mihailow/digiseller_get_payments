from flask import Flask, render_template, abort, jsonify, request
import hashlib
import hmac
app = Flask(__name__)

SECRET_KEY = ''


def generate_signature(data_dict, secret_key):
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


@app.route('/pay', methods=['POST'])
def payment_info():
    data = request.form.to_dict()
    print(f"{data=}")
    print('Received data:')
    for key, value in data.items():
        print(f'{key}: {value}')
    return jsonify(success=True)


@app.route('/payment', methods=['GET'])
def payment_info2():
    invoice_id = request.args.get('invoice_id')
    seller_id = request.args.get('seller_id')
    amount = request.args.get('amount')
    currency = request.args.get('currency')
    signature = request.args.get('signature')
 
    data_dict = {
        "invoice_id": invoice_id,
        "amount": amount,
        "currency": currency,
        "seller_id": seller_id,
    }
    
    # Проверяем подпись
    generated_signature = generate_signature(data_dict, SECRET_KEY)
    if generated_signature == signature:
        # Если подпись верна, возвращаем информацию о платеже

        data_new = {
            "invoice_id": invoice_id,
            "amount": amount,
            "currency": currency,
            "status": "paid"
        }

        new_sign = generate_signature(data_new, SECRET_KEY)
        response = {
            "invoice_id": invoice_id,
            "amount": amount,
            "currency": currency,
            "status": "paid",  # Предположим, что статус всегда "paid" для примера
            "signature": new_sign,
            "error": ""  # Если нет ошибок
        }
        return jsonify(response), 200
    else:
        # Если подпись неверна, возвращаем ошибку
        return jsonify({'error': 'Invalid signature'}), 400


if __name__ == '__main__':
    app.run(debug=True, port=8080, host="0.0.0.0")
