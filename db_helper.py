import sqlite3

class DBHelper:
    def __init__(self, dbname="instantgamingtracker.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS targets (url, target_price, chat_id)"
        self.conn.execute(stmt)
        self.conn.commit()

    def add_target(self, url, target_price, chat_id):
        stmt = "INSERT INTO targets (url, target_price, chat_id) VALUES (?, ?, ?)"
        args = (url, target_price, chat_id, )
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_target(self, url, chat_id):
        stmt = "DELETE FROM targets WHERE url = (?) AND chat_id = (?)"
        args = (url, chat_id, )
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_targets(self, chat_id):
        stmt = "SELECT url, target_price FROM targets WHERE chat_id = (?)"
        args = (chat_id, )
        return [x for x in self.conn.execute(stmt, args)]

    def get_all_targets(self):
        stmt = "SELECT url, target_price, chat_id FROM targets"
        return [x for x in self.conn.execute(stmt)]
