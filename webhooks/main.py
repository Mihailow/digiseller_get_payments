import asyncio

from flask import Flask, request, redirect
from flask_cors import CORS

from payment_systems import *
from functions import *
import db

app = Flask(__name__)
CORS(app)


@app.route('/api/change_status', methods=['POST'])
def change_status():
    data = request.json
    if "order_id" in data and "status" in data:
        asyncio.run(db.update_order_status(data['order_id'], data['status']))
    return "HTTP 200 ОК"


@app.route('/antilopay/webhook', methods=['GET', 'POST'])
def antilopay_webhook():
    data = request.json
    asyncio.run(db.insert_request(data, request.url))
    print('data\n', data, "\n")
    if "order_id" not in data:
        return "HTTP 200 ОК"
    order = asyncio.run(db.get_order(data["order_id"]))
    if order:
        resp = asyncio.run(Antilopay.check_payment(order_id=data["order_id"]))
        print('resp\n', resp, "\n")
        if "status" in resp and resp["status"] == "SUCCESS":
            asyncio.run(db.update_order_status(data["order_id"], "paid"))
            print('paid\n\n')
            order["status"] = "paid"
            asyncio.run(send_order_status(order["id_order"], resp["amount"], resp["currency"], order["status"]))
        else:
            asyncio.run(db.update_order_status(data["order_id"], "canceled"))
            print('canceled\n\n')
            order["status"] = "canceled"
            asyncio.run(send_order_status(data["order_id"], order["amount"], order["currency"], order["status"]))
    return "HTTP 200 ОК"


@app.route('/cryptomus/webhook', methods=['GET', 'POST'])
def cryptomus_webhook():
    data = request.json
    asyncio.run(db.insert_request(data, request.url))
    print('data\n', data, "\n")
    order = asyncio.run(db.get_order(data["order_id"]))
    if order:
        resp = asyncio.run(Cryptomus.check_payment(uuid=order["id_order_payment"], order_id=data["order_id"]))
        print('resp\n', resp, "\n")
        if resp.status in ["paid", "paid_over"]:
            asyncio.run(db.update_order_status(data["order_id"], "paid"))
            print('paid\n\n')
            order["status"] = "paid"
            if resp.currency == "USDT":
                resp.currency = "USD"
            asyncio.run(send_order_status(order["id_order"], resp.amount, resp.currency, order["status"]))
        else:
            asyncio.run(db.update_order_status(data["order_id"], "canceled"))
            print('canceled\n\n')
            order["status"] = "canceled"
            asyncio.run(send_order_status(order["id_order"], order["amount"], order["currency"], order["status"]))
    return "HTTP 200 ОК"


@app.route('/binancepay/webhook', methods=['GET', 'POST'])
def binancepay_webhook():
    data = request.json
    asyncio.run(db.insert_request(data, request.url))
    print('data\n', data, "\n")
    order = asyncio.run(db.get_order_by_id_payment_system(str(data["bizIdStr"])))
    if order:
        resp = asyncio.run(BinancePay.check_payment(order_id=order["id_order"]))
        print('resp\n', resp, "\n")
        if "status" in resp and resp["status"] == "SUCCESS" and "data" in resp and "status" in resp["data"] and resp["data"]["status"] == "PAID":
            asyncio.run(db.update_order_status(order["id_order"], "paid"))
            print('paid\n\n')
            order["status"] = "paid"
            asyncio.run(send_order_status(order["id_order"], resp["data"]["orderAmount"], resp["data"]["currency"], order["status"]))
        else:
            asyncio.run(db.update_order_status(order["id_order"], "canceled"))
            print('canceled\n\n')
            order["status"] = "canceled"
            asyncio.run(send_order_status(order["id_order"], order["amount"], order["currency"], order["status"]))
    return {"returnCode": "SUCCESS", "returnMessage": None}


@app.route('/wata/webhook', methods=['GET', 'POST'])
def waka_webhook():
    data = request.json
    asyncio.run(db.insert_request(data, request.url))
    print('data\n', data, "\n")
    order = asyncio.run(db.get_order(data["order_id"]))
    if order:
        resp = asyncio.run(Wata.check_payment(order_id=order["id_order_payment"]))
        print('resp\n', resp, "\n")
        if "status" in resp and resp["status"] == "Paid":
            asyncio.run(db.update_order_status(data["order_id"], "paid"))
            print('paid\n\n')
            order["status"] = "paid"
            asyncio.run(send_order_status(order["id_order"], resp["amount"], order["currency"], order["status"]))
        else:
            asyncio.run(db.update_order_status(data["order_id"], "canceled"))
            print('canceled\n\n')
            order["status"] = "canceled"
            asyncio.run(send_order_status(order["id_order"], order["amount"], order["currency"], order["status"]))
    return "HTTP 200 ОК"


@app.route('/p2p/webhook', methods=['GET', 'POST'])
def p2p_webhook():
    data = json.loads(request.data)
    asyncio.run(db.insert_request(data, request.url))
    print('data\n', data, "\n")
    order = asyncio.run(db.get_order(data["order_id"]))
    if order:
        if asyncio.run(P2p.check_payment(data)):
            asyncio.run(db.update_order_status(data["order_id"], "paid"))
            print('paid\n\n')
            order["status"] = "paid"
            asyncio.run(send_order_status(order["id_order"], data["amount"], data["currency"], order["status"]))
        else:
            print('canceled\n\n')
            order["status"] = "canceled"
            asyncio.run(send_order_status(order["id_order"], order["amount"], order["currency"], order["status"]))
    return "Оплата успешно обработана", 200


@app.route('/gmpays/webhook', methods=['GET', 'POST'])
def gmpays_webhook():
    data = request.form.to_dict()
    asyncio.run(db.insert_request(data, request.url))
    print('data\n', data, "\n")
    order = asyncio.run(db.get_order(data["project_invoice"]))
    if order:
        resp = asyncio.run(Gmpays.check_payment(order_id=data["project_invoice"]))
        print('resp\n', resp, "\n")
        if "status" in resp and resp["status"] == "Paid":
            asyncio.run(db.update_order_status(data["project_invoice"], "paid"))
            print('paid\n\n')
            order["status"] = "paid"
            asyncio.run(send_order_status(order["id_order"], resp["amount"], resp["currency_project"], order["status"]))
        else:
            asyncio.run(db.update_order_status(data["project_invoice"], "canceled"))
            print('canceled\n\n')
            order["status"] = "canceled"
            asyncio.run(send_order_status(order["id_order"], order["amount"], order["currency"], order["status"]))
    return {"success": "true"}


@app.route('/b2pay/webhook', methods=['GET', 'POST'])
def b2pay_webhook():
    data = request.json
    asyncio.run(db.insert_request(data, request.url))
    print('data\n', data, "\n")
    order = asyncio.run(db.get_order(data["orderNumber"]))
    sign = data["sign"]
    if order:
        signature = asyncio.run(B2pay.sign(data))
        print('signature\n', signature, "\n")
        if signature == sign and data["status"] == "approved":
            asyncio.run(db.update_order_status(data["orderNumber"], "paid"))
            print('paid\n\n')
            order["status"] = "paid"
            asyncio.run(send_order_status(order["id_order"], data["amount"], data["currency"], order["status"]))
        else:
            asyncio.run(db.update_order_status(data["orderNumber"], "canceled"))
            print('canceled\n\n')
            order["status"] = "canceled"
            asyncio.run(send_order_status(order["id_order"], order["amount"], order["currency"], order["status"]))
    return "HTTP 200 ОК"


@app.route('/paypalych/webhook', methods=['GET', 'POST'])
def paypalych_webhook():
    data = request.form.to_dict()
    asyncio.run(db.insert_request(data, request.url))
    print('data\n', data, "\n")
    order = asyncio.run(db.get_order(data["InvId"]))
    if order:
        resp = asyncio.run(Paypalych.check_payment(order_id=data["TrsId"]))
        print('resp\n', resp, "\n")
        if "status" in resp and resp["status"] in ["SUCCESS", "OVERPAID"]:
            asyncio.run(db.update_order_status(order["id_order"], "paid"))
            print('paid\n\n')
            order["status"] = "paid"
            asyncio.run(send_order_status(order["id_order"], resp["amount"], resp["currency_in"], order["status"]))
        else:
            asyncio.run(db.update_order_status(order["id_order"], "canceled"))
            print('canceled\n\n')
            order["status"] = "canceled"
            asyncio.run(send_order_status(order["id_order"], order["amount"], order["currency"], order["status"]))
    return "HTTP 200 ОК"


@app.route('/paypalych/success', methods=['GET', 'POST'])
def paypalych_success():
    data = request.form.to_dict()
    asyncio.run(db.insert_request(data, request.url))
    print('data\n', data, "\n")
    order = asyncio.run(db.get_order(data["InvId"]))
    if order:
       return redirect(order["return_url"])
    return "HTTP 200 ОК"


@app.route('/paypalych/fail', methods=['GET', 'POST'])
def paypalych_fail():
    data = request.form.to_dict()
    asyncio.run(db.insert_request(data, request.url))
    print('data\n', data, "\n")
    order = asyncio.run(db.get_order(data["InvId"]))
    if order:
       return redirect(order["return_url"])
    return "HTTP 200 ОК"


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)
