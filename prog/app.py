from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.responses import JSONResponse
import uvicorn
import urllib.parse

from functions import *
import db


app = FastAPI()


# URL платежа
@app.get("/payment")
async def receive_item(invoice_id: str, seller_id: str, amount: str, currency: str, signature: str):
    data_dict = {
        "invoice_id": invoice_id,
        "amount": amount,
        "currency": currency,
        "seller_id": seller_id,
    }
    # Проверяем подпись
    generated_signature = await generate_signature(data_dict, SECRET)
    if generated_signature == signature:
        # Если подпись верна, возвращаем информацию о платеже
        status = await db.get_order_status(str(invoice_id))
        data_new = {
            "invoice_id": invoice_id,
            "amount": amount,
            "currency": currency,
            "status": status      
        }

        new_sign = await generate_signature(data_new, SECRET)
        response = {
            "invoice_id": invoice_id,
            "amount": amount,
            "currency": currency,
            "status": status,  # Предположим, что статус всегда "paid" для примера
            "signature": new_sign,
            "error": ""  # Если нет ошибок
        }
        return JSONResponse(content=response)
    else:
        # Если подпись неверна, возвращаем ошибку
        return JSONResponse(content={'error': 'Invalid signature'}, status_code=400)


# URL оплаты
@app.post("/pay")
async def receive_item2(request: Request):
    body_bytes = await request.body()
    form_data = urllib.parse.parse_qs(body_bytes.decode('utf-8'))
    form_data = {k: v[0] for k, v in form_data.items()}
    return_url = urllib.parse.unquote(form_data['return_url'])
    receipt = urllib.parse.unquote(form_data['receipt'])
    receipt_str_fixed = receipt.replace('+', ' ')
    receipt = json.loads(receipt_str_fixed)
    url = await create_invoice_url({
        "invoice_id": form_data['invoice_id'],
        "amount": form_data['amount'],
        "currency": form_data['currency'],
        "description": form_data['description'],
        "lang": form_data['lang'],
        "email": form_data['email'],
        "payment_id": form_data['payment_id'],
        "owner": form_data['owner'],
        "receipt": receipt,
        "return_url": return_url})
    await db.update_order_ip(str(form_data['invoice_id']), str(request.client.host), str(await get_country_code(str(request.client.host))))

    return RedirectResponse(url=url, status_code=303)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
