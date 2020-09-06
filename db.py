import sqlite3


class Database():
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def add_value(self, table_name, values):
        value = self.get_value(
            select='*',
            table_name=table_name,
            where="userId='{}' and filename='{}' and sha256='{}' and md5='{}'".format(
                values.get('userId'),
                values.get('filename'),
                values.get('sha256'),
                values.get('md5')
            )
        )
        if not value:
            values = tuple(values.values())
            query = 'INSERT INTO {} VALUES {}'.format(
                table_name, values
            )
            try:
                self.cursor.execute(query)
                self.conn.commit()
            except Exception as err:
                print(err)
                self.conn.rollback()

    def get_value(self, select, table_name, where=None):
        query = 'SELECT {} FROM {}'.format(
            str(select), table_name
        )
        if where:
            query = '{} WHERE {}'.format(query, where)
        self.cursor.execute(query)
        response = self.cursor.fetchone()
        if response:
            response_keys = response.keys()
            response = tuple(response)
            if len(response) == len(response_keys):
                response = dict(zip(response_keys, response))

            return response
        else:
            return tuple()

    def del_value(self, table_name, where):
        query = 'DELETE FROM {} WHERE {}'.format(
            table_name, where
        )
        self.cursor.execute(query)
        self.conn.commit()

        return tuple(self.cursor.fetchall())
