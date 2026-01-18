from datetime import datetime
import sqlite3

class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cur = self.conn.cursor()
        self.cur.execute('PRAGMA journal_mode=WAL;')

    def create_user(self, chat_id):
        self.cur.execute("""INSERT INTO user(chat_id) VALUES (?) """, (chat_id,))
        self.conn.commit()

    def update_user_data(self, chat_id, key, value):
        self.cur.execute(f"UPDATE USER SET {key} = ? WHERE chat_id = ?", (value, chat_id))
        self.conn.commit()

    def get_user_by_chat_id(self, chat_id):
        self.cur.execute(f" SELECT * FROM user WHERE chat_id = ?", (chat_id,))
        user = dict_fetchone(self.cur)
        return user

    # lesson 2
    def get_categories_by_parent(self, parent_id=None):
        if parent_id:
            self.cur.execute("""select * from category where parent_id = ?""", (parent_id, ))
        else:
            self.cur.execute("""select * from category where parent_id is NULL""")

        categories = dict_fetchall(self.cur)
        return categories

    def get_category_parent(self, category_id):
        self.cur.execute("""select parent_id from category where id = ?""", (category_id, ))
        category = dict_fetchone(self.cur)
        return category

    # New 3
    def get_products_by_category(self, category_id):
        self.cur.execute("""select * from product where category_id = ?""", (category_id,))
        products = dict_fetchall(self.cur)
        return products

    def get_product_by_id(self, product_id):
        self.cur.execute("SELECT * FROM product WHERE id = ?", (product_id,))
        product = dict_fetchone(self.cur)
        return product

    # Lesson 4
    def get_product_for_cart(self, product_id):
        self.cur.execute("""
        SELECT product.*, category.name_uz as cat_name_uz, category.name_ru as cat_name_ru
        FROM product INNER JOIN category ON product.category_id  WHERE product.id = ?
        """, (product_id,))

        product = dict_fetchone(self.cur)
        return product

    def create_order(self, user_id, products, payment_type, location):
        self.cur.execute("""
        INSERT INTO "order"(user_id, status, payment_type, longitude, latitude, created_at) VALUES (?, ?, ?, ?, ?, ?)"""
                         , (user_id, 1, payment_type, location.longitude, location.latitude, datetime.now())
                         )
        self.conn.commit()
        self.cur.execute("""
        SELECT max(id) as last_order FROM "order" WHERE user_id = ? """, (user_id,))

        last_order = dict_fetchone(self.cur)['last_order']
        for key, val in products.items():
            self.cur.execute("""
            INSERT INTO "order_product"(product_id, order_id, amount, created_at) VALUES (?, ?, ?, ?)""",
                             (int(key), last_order, int(val), datetime.now())
                             )
        self.conn.commit()

    def get_user_orders(self, user_id):
        self.cur.execute("""
        SELECT * FROM "order" WHERE user_id = ? AND status = 1""", (user_id,))
        orders = dict_fetchall(self.cur)
        return orders

    def get_order_products(self, order_id):
        self.cur.execute("""
        SELECT order_product.*, product.name_uz as product_name_uz, product.name_ru as product_name_ru,
        product.price as product_price FROM order_product INNER JOIN product ON order_product.product_id = product.id
        WHERE order_id = ?""", (order_id,))

        products = dict_fetchall(self.cur)
        return products



def dict_fetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def dict_fetchone(cursor):
    row = cursor.fetchone()
    if row is None:
        return False
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))