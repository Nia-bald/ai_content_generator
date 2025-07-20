import sqlite3
from typing import Any, List, Tuple, Optional

class LocalDatabase:
    def __init__(self, db_path: str = 'local_database.db'):
        """
        Initialize the database connection.
        :param db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def execute_write(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> None:
        """
        Execute a write (INSERT, UPDATE, DELETE) query.
        :param query: SQL query string.
        :param params: Optional tuple of parameters for the query.
        """
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        self.conn.commit()

    def execute_insert(self, table_name: str, data:List[dict]) -> None:
        """
        Execute an insert query.
        :param table_name: Name of the table to insert into.
        :param data: List of dictionaries containing the data to insert.
        """
        for row in data:
            query = f"INSERT INTO {table_name} ({', '.join(row.keys())}) VALUES ({', '.join(['?' for _ in row.keys()])})"
            self.execute_write(query, tuple(row.values()))
    
    def execute_read(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> List[Tuple[Any, ...]]:
        """
        Execute a read (SELECT) query and return the results.
        :param query: SQL query string.
        :param params: Optional tuple of parameters for the query.
        :return: List of tuples containing the query results.
        """
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        return self.cursor.fetchall()

    def close(self):
        """
        Close the database connection.
        """
        self.conn.close()

if __name__ == "__main__":
    db = LocalDatabase('database.db')
    # data = [
    #     {'VideoId': 12, 'UpvoteCount': 100, 'DownvoteCount': 5, 'DateOfPosting': '2024-06-01', 'ViewCount': 1000, 'Comments': 'Great video!', 'Type': 'mp4', 'VideoPath': '/videos/video1.mp4', 'MediaPath': '/media/media1.mp4'},
    #     {'VideoId': 13, 'UpvoteCount': 100, 'DownvoteCount': 5, 'DateOfPosting': '2024-06-01', 'ViewCount': 1000, 'Comments': 'Great video!', 'Type': 'mp4', 'VideoPath': '/videos/video1.mp4', 'MediaPath': '/media/media1.mp4'}
    # ]
    # db.execute_insert('VideoTable', data)
    output = db.execute_read("SELECT * FROM RedditPostTable")
    print(output)
    db.close()