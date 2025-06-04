import psycopg2
import psycopg2.extras
import json

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


async def postgres_select_one(query: str, params: object) -> object:
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


async def postgres_select_all(query: str, params: object) -> object:
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


# изменить status в заказе
async def update_order_status(id_order: str, status: str):
    await postgres_do_query("UPDATE digiseller_orders SET status = %s WHERE id_order = %s;",
                            (status, id_order,))


# получить заказ
async def get_order(id_order: str):
    order = await postgres_select_one("SELECT * FROM digiseller_orders WHERE id_order = %s;",
                                      (id_order,))
    return order


# получить заказ по id платежной системы
async def get_order_by_id_payment_system(id_order_payment: str):
    order = await postgres_select_one("SELECT * FROM digiseller_orders WHERE id_order_payment = %s;",
                                      (id_order_payment,))
    return order


async def insert_request(request: dict, url):
    await postgres_do_query("INSERT INTO requests (request, type, url) VALUES (%s, %s, %s);",
                            (json.dumps(request, ensure_ascii=True), "webhook", url))