import openpyxl
import mysql.connector.aio as mysql
from mysql.connector.cursor import MySQLCursor
import mysql.connector as mysql_
import config

conn = None
cursor: MySQLCursor = None


async def init():
    global conn
    global cursor
    #conn = await mysql.connect(user=config.DB_USER, database=config.DB_NAME, password=config.DB_PASSWORD, host=config.DB_HOST)
    conn = await mysql.connect(user=config.DB_USER, database=config.DB_NAME, password=config.DB_PASSWORD, host='localhost',
                                port=32001)
    cursor = await conn.cursor()

async def terminate():
    await conn.close()


async def write(store, date, items, user_id):
    global cursor
    q = """
INSERT IGNORE INTO costs (name, price, quantity, cost, date, store, 
user_id, category_id)
VALUES (%s, %s, %s, %s, %s, 
IFNULL((SELECT synonym FROM shop_synonyms WHERE user_id = %s AND shop = %s), %s),
%s, 
(SELECT category_id FROM regexes WHERE user_id = %s AND LOWER(%s) REGEXP regex)
)
"""
    await cursor.executemany(q, [(item['name'], item['price'], 
                                    item['quantity'], item['price']*item['quantity'], 
                                    date, user_id, store, store, user_id, user_id, item['name']) for item in items])
    await conn.commit()
        

async def new_category(name, user_id):
    global cursor
    await cursor.execute("INSERT IGNORE INTO categories (name, user_id) VALUES (%s, %s)", (name, user_id))
    await conn.commit()

async def new_product(name, regex, user_id):
    global cursor
    q = """
INSERT INTO regexes (category_id, regex, user_id)
VALUES ((SELECT id from categories WHERE user_id=%s AND name=%s), %s, %s)
"""
    await cursor.execute(q, (user_id, name, regex, user_id))
    q = """
UPDATE costs
SET category_id = (SELECT category_id FROM regexes WHERE user_id = %s AND LOWER(name) REGEXP regex)
WHERE
"""
    await cursor.execute(q, (user_id,))
    await conn.commit()

async def ls_categories(user_id):
    global cursor
    q = """
SELECT name, IFNULL(GROUP_CONCAT(regex SEPARATOR ', '), "")
FROM regexes RIGHT JOIN categories ON categories.id = regexes.category_id
WHERE categories.user_id = %s
GROUP BY name
"""
    global cursor
    await cursor.execute(q, (user_id,))
    return await cursor.fetchall()

async def get_user_records(user_id):
    global cursor
    q = """
SELECT date, costs.name, price, quantity, cost, IFNULL(categories.name, "разное"), store
FROM costs LEFT JOIN categories ON category_id = categories.id
WHERE costs.user_id = %s
"""
    await cursor.execute(q, (user_id,))
    return await cursor.fetchall()

async def new_synonym(shop, syn, user_id):
    global cursor
    await cursor.execute("INSERT IGNORE INTO shop_synonyms (shop, synonym, user_id) VALUES (%s, %s, %s)", (shop, syn, user_id))
    await conn.commit()

async def report(rep, user_id, *args):
    global cursor
    q = "SELECT query FROM reports WHERE name = %s AND user_id IN (%s, 0)"
    await cursor.execute(q, (rep, user_id))
    q = (await cursor.fetchall())[0][0]
    await cursor.execute(q, (user_id, *args))
    res = await cursor.fetchall()
    return res, [i[0] for i in cursor.description]

async def ls_reports(user_id):
    global cursor
    q = "SELECT name, help FROM reports WHERE user_id IN (%s, 0)"
    await cursor.execute(q, (user_id,))
    return await cursor.fetchall()

async def new_top_category(name, user_id):
    global cursor
    await cursor.execute("INSERT IGNORE INTO top_categories (name, user_id) VALUES (%s, %s)", (name, user_id))
    await conn.commit()

async def ls_top_categories(user_id):
    global cursor
    q = """
SELECT t.name, IFNULL(GROUP_CONCAT(c.name SEPARATOR ', '), "")
FROM included_categories AS i
INNER JOIN categories AS c ON c.id = i.category_id
RIGHT JOIN top_categories AS t ON t.id = i.top_id
WHERE t.user_id = %s
GROUP BY t.name
"""
    await cursor.execute(q, (user_id,))
    return await cursor.fetchall()

async def include_in_top_category(topcat, cat, user_id):
    global cursor
    q = """
INSERT INTO included_categories (category_id, top_id, user_id)
VALUES (
(SELECT id FROM categories WHERE name = %s AND user_id = %s),
(SELECT id FROM top_categories WHERE name = %s AND user_id = %s),
%s
)
"""
    try:
        await cursor.execute(q, (cat, user_id, topcat, user_id, user_id))
        await conn.commit()
    except mysql_.errors.Error as e:
        return -1

def write_excel(table): #
    #date = date.strftime('%d.%m.%Y %H:%M')
    wb = openpyxl.Workbook()
    page = wb.worksheets[0]
    for i, row in enumerate(table, 1):
        for j, cell in enumerate(row, 1):
            page.cell(i, j, cell)
    wb.save('report.xlsx')


def pretty_print(table, headers=None):
    s = ''
    if headers:
        s += ('  '.join(str(j) for j in headers)) + '\n'
    for i in table:
        s += '  '.join(str(j) for j in i) + '\n'
    return s
