from config import DTB, HOST, USER, PASS
import mysql.connector

class DBAccess:
    def __init__(self, db_name = DTB):
        self._conn = mysql.connector.connect(
            host = HOST,
            user = USER,
            passwd = PASS,
            database = db_name
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
        
    def executemany(self, sql, seq_of_params):
        self.cursor.executemany(sql, seq_of_params)

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def query(self, sql, params):
        self.cursor.execute(sql, params or ())
        return self.fetchall()