from db.engine import database

class BaseRepo:
    def __init__(self, table_name, pk_column):
        self.table = table_name
        self.pk = pk_column

    def create(self, data: dict):
        columns = ", ".join(data.keys())
        placeholder = ", ".join(["%s"]*len(data))
        query = f"INSERT INTO {self.table} ({columns}) VALUES {placeholder}"
        with database.get_cursor() as cursor:
            cursor.execute(query, tuple(data.values()))
            return cursor.lastrowid

    def find_by_id(self, pk_value):
        query = f"SELECT * FROM {self.table} WHERE {self.pk} = %s"
        with database.get_cursor(dictionary=True) as cursor:
            cursor.execute(query, (pk_value,))
            return cursor.fetchone()

    def find_all(self, limit=20):
        query = f"SELECT * FROM {self.table} LIMIT = %s"
        with database.get_cursor(dictionary=True) as cursor:
            cursor.execute(query, (limit,))
            return cursor.fetchall()

    def update(self, pk_value, data: dict):
        set_clause = ", ".join(f"{k} = %s" for k in data)
        values = tuple(data.values()) + (pk_value,)
        query = f"UPDATE {self.table} SET {set_clause} WHERE {self.pk} = %s"
        with database.get_cursor() as cursor:
            cursor.execute(query, values)
            return cursor.rowcount

    def delete(self, pk_value):
        query = f"DELETE FROM {self.table} WHERE {self.pk} = %s"
        with database.get_cursor() as cursor:
            cursor.execute(query, (pk_value,))
            return cursor.rowcount > 0