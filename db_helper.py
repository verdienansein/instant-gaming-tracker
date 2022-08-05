import sqlite3
import psycopg2

class DBHelper:
    def __init__(self, dbname="instantgamingtracker.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS targets (url, target_price, chat_id, PRIMARY KEY(url, chat_id))"
        self.conn.execute(stmt)
        self.conn.commit()

    def add_target(self, url, target_price, chat_id):
        try:
            stmt = "INSERT INTO targets (url, target_price, chat_id) VALUES (?, ?, ?)"
            args = (url, target_price, chat_id, )
            self.conn.execute(stmt, args)
            self.conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError

    def delete_target(self, url, chat_id):
        stmt = "DELETE FROM targets WHERE url = (?) AND chat_id = (?)"
        args = (url, chat_id, )
        self.conn.execute(stmt, args)
        self.conn.commit()

    def update_target_price(self, url, target_price, chat_id):
        stmt = "UPDATE targets set target_price = (?) WHERE url = (?) AND chat_id = (?)"
        args = (target_price, url, chat_id, )
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_targets(self, chat_id):
        stmt = "SELECT url, target_price FROM targets WHERE chat_id = (?)"
        args = (chat_id, )
        return [x for x in self.conn.execute(stmt, args)]

    def get_all_targets(self):
        stmt = "SELECT url, target_price, chat_id FROM targets"
        return [x for x in self.conn.execute(stmt)]

class PostgreDBHelper:
    def __init__(self, conn_string):
        self.conn_string = conn_string
        self.conn = psycopg2.connect(self.conn_string)
        self.conn.autocommit = True

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS targets (url VARCHAR (300), target_price DECIMAL, chat_id INTEGER, PRIMARY KEY(url, chat_id))"
        # stmt= "DROP TABLE targets"
        self.cursor = self.conn.cursor()
        self.cursor.execute(stmt)
        self.conn.commit()

    def add_target(self, url, target_price, chat_id):
        try:
            stmt = "INSERT INTO targets (url, target_price, chat_id) VALUES (%s, %s, %s)"
            args = (url, target_price, chat_id, )
            self.cursor = self.conn.cursor()
            self.cursor.execute(stmt, args)
            self.conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError

    def delete_target(self, url, chat_id):
        stmt = "DELETE FROM targets WHERE url = (%s) AND chat_id = (%s)"
        args = (url, chat_id, )
        self.cursor = self.conn.cursor()
        self.cursor.execute(stmt, args)
        self.conn.commit()

    def update_target_price(self, url, target_price, chat_id):
        stmt = "UPDATE targets set target_price = (%s) WHERE url = (%s) AND chat_id = (%s)"
        args = (target_price, url, chat_id, )
        self.cursor = self.conn.cursor()
        self.cursor.execute(stmt, args)
        self.conn.commit()

    def get_targets(self, chat_id):
        stmt = "SELECT url, target_price FROM targets WHERE chat_id = (%s)"
        args = (chat_id, )
        self.cursor = self.conn.cursor()
        self.cursor.execute(stmt, args)
        result = self.cursor.fetchall()
        return result

    def get_all_targets(self):
        stmt = "SELECT url, target_price, chat_id FROM targets"
        self.cursor = self.conn.cursor()
        self.cursor.execute(stmt)
        result = self.cursor.fetchall()
        return result
