import sqlite3


class Database():
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def add_value(self, values):
        value = self.get_value(
            '''SELECT * FROM carbery_table 
                WHERE userId=? AND filename=? AND sha256=? AND md5=?''',
            values
        )
        if not value:
            query = 'INSERT INTO carbery_table VALUES (?, ?, ?, ?)'
            try:
                self.cursor.execute(query, values)
                self.conn.commit()
            except Exception as err:
                print(err)
                self.conn.rollback()

    def get_value(self, query, values):
        self.cursor.execute(query, values)
        response = self.cursor.fetchone()
        if response:
            response_keys = response.keys()
            response = tuple(response)
            if len(response) == len(response_keys):
                response = dict(zip(response_keys, response))

            return response
        else:
            return tuple()

    def del_value(self, where_values):
        query = '''DELETE FROM carbery_table 
            WHERE userId=? and (sha256=? or md5=?)'''
        self.cursor.execute(query, where_values)
        self.conn.commit()

        return tuple(self.cursor.fetchall())
