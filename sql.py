import sqlite3

class SQLighter:
    def __init__(self, database_file):
        # подключение к бд
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()
    def output(self, query):
        with self.connection:
            return self.cursor.execute(query).fetchall()
