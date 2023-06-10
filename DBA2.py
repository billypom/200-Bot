import secretly2
import mysql.connector

class DBAccess:
    def __init__(self):
        self._conn = mysql.connector.connect(
            host = secretly2.HOST,
            user = secretly2.USER,
            passwd = secretly2.PASS,
            database = secretly2.DTB
        )
        self._cursor = self._conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def connection(self):
        return self._conn

    @property
    def cursor(self):
        return self._cursor

    def commit(self):
        self.connection.commit()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.connection.close()

    def execute(self, sql, params):
        self.cursor.execute(sql, params or ())

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def query(self, sql, params):
        self.cursor.execute(sql, params or ())
        return self.fetchall()