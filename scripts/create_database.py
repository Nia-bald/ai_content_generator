import sqlite3


class DataBaseBuilder:
    def __init__(self, database_name: str):
        self.database_name = database_name
        self.conn = sqlite3.connect(database_name)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name: str, columns: list[str]):
        with open('schemas/database_schema.sql', 'r') as f:
            sql_script = f.read()
        # Split the script into individual statements and execute each
        for statement in sql_script.split(';'):
            stmt = statement.strip()
            if stmt:
                self.cursor.execute(stmt)
            self.conn.commit()

    def close(self):
        self.conn.close()


if __name__ == "__main__":
    db_builder = DataBaseBuilder('database.db')
    db_builder.create_table('users', ['id INTEGER PRIMARY KEY', 'name TEXT'])
    db_builder.close()



