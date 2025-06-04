import json

import psycopg2
import psycopg2.extras

DB_HOST = "109.172.89.152"
DB_NAME = "digiseller"
DB_USER = "playhaslimits"
DB_PASS = "kjdsghfkjsf83457943.fsh=2342safaskfasjf"


async def postgres_do_query(query: str, params: object) -> object:
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(query, params)
    try:
        results = cursor.fetchall()
    except:
        results = None
    conn.commit()
    cursor.close()
    conn.close()
    return results


async def postgres_select_one(query, params):
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(query, params)
    result = cursor.fetchone()
    if result:
        result = dict(result)
    conn.commit()
    cursor.close()
    conn.close()

    return result


async def postgres_select_all(query, params):
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(query, params)
    results = cursor.fetchall()
    if results:
        res = []
        for r in results:
            res.append(dict(r))
        results = res
    conn.commit()
    cursor.close()
    conn.close()
    return results


# добавить новый заказ
async def insert_order(id_order: str, amount: (int, float, str), currency: str, description: str, lang: str, email: str, payment_id: str, owner: str, products_info: dict, return_url: str, add_percent: float, add_amount: float):
    await postgres_do_query("INSERT INTO digiseller_orders (id_order, amount, currency, description, lang, email, payment_id, owner, products_info, return_url, time, status, add_percent, add_amount) "
                            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                            (id_order, amount, currency, description, lang, email, payment_id, owner, json.dumps(products_info, ensure_ascii=True), return_url, "NOW()", "wait", add_percent, add_amount,))


# изменить status в заказе
async def update_order_status(id_order: str, status: str):
    await postgres_do_query("UPDATE digiseller_orders SET status = %s WHERE id_order = %s;",
                            (status, id_order,))


# изменить ip, country_code в заказе
async def update_order_ip(id_order: str, ip: str, country_code: str):
    await postgres_do_query("UPDATE digiseller_orders SET ip = %s, country_code = %s WHERE id_order = %s;",
                            (ip, country_code, id_order,))


# изменить id_order_payment в заказе
async def update_order_id_order_payment(id_order: str, id_order_payment: str):
    await postgres_do_query("UPDATE digiseller_orders SET id_order_payment = %s WHERE id_order = %s;",
                            (id_order_payment, id_order,))


# получить статус заказа
async def get_order_status(id_order: str):
    order = await postgres_select_one("SELECT * FROM digiseller_orders WHERE id_order = %s;",
                                      (id_order,))
    if order:
        return order["status"]
    return 'wait'


# получить все заказы
async def get_orders():
    orders = await postgres_select_all("SELECT * FROM digiseller_orders ORDER BY time DESC;",
                                       None)
    return orders


# получить заказ
async def get_order(id_order: str):
    order = await postgres_select_one("SELECT * FROM digiseller_orders WHERE id_order = %s;",
                                      (id_order,))
    return order


# добавить новую платежную систему
async def insert_payment_system(payment_id: str, percent: (float, int), amount: (float, int), description: str):
    await postgres_do_query("INSERT INTO payment_systems (payment_id, percent, amount, description) "
                            "VALUES (%s, %s, %s, %s);",
                            (payment_id, percent, amount, description,))


# изменить платежную систему
async def update_payment_system(payment_id: str, percent: (float, int), amount: (float, int), description: str):
    await postgres_do_query("UPDATE payment_systems SET percent = %s, amount = %s, description = %s "
                            "WHERE payment_id = %s;",
                            (percent, amount, description, payment_id,))


# удалить платежную систему
async def delete_payment_system(payment_id: str):
    await postgres_do_query("DELETE FROM payment_systems WHERE payment_id = %s;",
                            (payment_id,))


# получить все платежные системы
async def get_payment_systems():
    payment_systems = await postgres_select_all("SELECT * FROM payment_systems ORDER BY description;",
                                                None)
    print(payment_systems)
    print(payment_systems[0]['amount'])
    print(payment_systems[0]['amount']+1)
    return payment_systems


# получить платежную систему
async def get_payment_system(payment_id):
    payment_system = await postgres_select_one("SELECT * FROM payment_systems WHERE payment_id = %s;", (payment_id,))
    return payment_system

