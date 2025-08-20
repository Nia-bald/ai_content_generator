import sqlite3
import logging
import uuid
from typing import Any, List, Tuple, Optional
from utils.units import Task, RedditData, RedditDataList
import pandas as pd

class LocalDatabase:
    def __init__(self, db_path: str = 'database.db'):
        """
        Initialize the database connection.
        :param db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.table_name_to_primary_key = {"opinfo":"OpInfoId", "redditposttable":"PostId", "postproductiontable":"PostProductionTableId"}

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

    def execute_upsert(self, table_name: str, data:List[dict]) -> None:
        """
        Execute an insert query.
        :param table_name: Name of the table to insert into.
        :param data: List of dictionaries containing the data to insert.
        """
        primary_key = self.table_name_to_primary_key.get(table_name.lower())
        for row in data:
            query = f"""
            INSERT INTO {table_name} ({', '.join(row.keys())})
            VALUES ({', '.join(['?' for _ in row.keys()])})
            ON CONFLICT ({primary_key})
            DO UPDATE SET {', '.join([f"{col}=excluded.{col}" for col in row.keys() if col != primary_key])}
            """
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

    def execute_read_df(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> pd.DataFrame:
        """
        Execute a read (SELECT) query and return the results as a pandas DataFrame.
        :param query: SQL query string.
        :param params: Optional tuple of parameters for the query.
        :return: pandas.DataFrame containing the query results.
        """
        if params:
            df = pd.read_sql_query(query, self.conn, params=params)
        else:
            df = pd.read_sql_query(query, self.conn)
        return df
    def close(self):
        """
        Close the database connection.
        """
        self.conn.close()

class DataSaver:
    def __init__(self, db: LocalDatabase, logger: Optional[logging.Logger] = None):
        self.db = db
        self.logger = logger or logging.getLogger(__name__)

    def save_task(self, task: Task) -> Task:
        """
        Persist all Reddit data associated with the task into the database.
        Mirrors the behavior of VideoGenerationPipeline.save_to_db but uses
        modular helper methods for clarity and testability.
        """
        self.logger.info("Starting database save operation (DataSaver)")
        total_posts_saved = 0

        try:
            for subreddit_name, reddit_data in task.reddit_datas.subreddit_to_reddit_data.items():
                total_posts_saved += self._save_single_subreddit(subreddit_name, reddit_data)

            self.logger.info(f"Database save completed successfully. Total posts saved: {total_posts_saved}")
        except Exception as exc:
            self.logger.error(f"Database save failed: {str(exc)}")
            raise

        return task

    def _save_single_subreddit(self, subreddit_name: str, reddit_data: RedditData) -> int:
        """
        Save all rows for a single subreddit's RedditData into the database.
        Returns the number of posts saved for this subreddit.
        """
        self.logger.info(f"Processing data for subreddit: {subreddit_name}")

        pandas_data = reddit_data.to_pandas_dataframe()

        op_rows = self._build_op_info_rows(pandas_data)
        if op_rows:
            self.logger.info(f"Inserting {len(op_rows)} OpInfo records for subreddit {subreddit_name}")
            self.db.execute_upsert('OpInfo', op_rows)

        post_rows = self._build_reddit_post_rows(pandas_data, subreddit_name)
        if post_rows:
            self.logger.info(f"Inserting {len(post_rows)} RedditPostTable records for subreddit {subreddit_name}")
            self.db.execute_upsert('RedditPostTable', post_rows)

        post_prod_rows = self._build_post_prod_rows(pandas_data)

        if post_prod_rows:
            self.logger.info(f"Inserting {len(post_prod_rows)} PostProductionTable records for subreddit {subreddit_name}")
            self.db.execute_upsert('PostProductionTable', post_prod_rows)

        return len(post_rows)
    
    def _build_post_prod_rows(self, pandas_data)-> List[dict]:
        """
        Construct rows for the PostProductionTable from a DataFrame of Reddit posts.
        """
        post_prod_details: List[dict] = []

        for _, row in pandas_data.iterrows():
            post_prod_details.append({
                'PostProductionTableId': str(uuid.uuid4()),
                'PostId': row['id'],
                'ChannelId': None,  # Not available in Reddit data
                'Tags': None,  # Not available in Reddit data
                'Description': None,
                'Credit': None,
                'Title': None,
                'Rank': None,  # Not available in Reddit data
                'RankingAlgorithm': None,  # Not available in Reddit data
                'AudioPath': row.get('synthesized_audio_file_path', None),
                'VideoPath': row.get('video_file_path', None),
                'FinalVideoPath': row.get('final_video_path', None),
                'Narration': row.get('narration', None),
                'DateOfPosting': None,
                'ViewCount': None,
                'Likes': None,
                'YouTubeAnalytics': None  # Not available
            })
        return post_prod_details

    def _build_op_info_rows(self, pandas_data) -> List[dict]:
        """
        Construct rows for the OpInfo table from a DataFrame of Reddit posts.
        """
        op_details: List[dict] = []
        for _, row in pandas_data.iterrows():
            op_details.append({
                'OpInfoId': row['author_fullname'],
                'OpName': row['author'],
                'OpFollowers': None  # TODO: populate from Reddit API when available
            })
        return op_details

    def _build_reddit_post_rows(self, pandas_data, subreddit_name: str) -> List[dict]:
        """
        Construct rows for the RedditPostTable from a DataFrame of Reddit posts.
        """
        content_details: List[dict] = []
        for _, row in pandas_data.iterrows():
            content_details.append({
                'PostId': row['id'],
                'Content': row['selftext'],
                'Type': None,  # TODO: determine from Reddit data
                'MediaPath': None,  # TODO: determine from Reddit data
                'SubredditName': subreddit_name,
                'Rank': None,
                'RankingAlgorithm': None,
                'EngagmentTableId': None,
                'OpInfoId': row['author'],  # Note: mirrors current pipeline behavior
                'PostProductionTableId': None
            })
        return content_details


if __name__ == "__main__":
    db = LocalDatabase('database.db')
    output = db.execute_read_df("SELECT * FROM PostProductionTable")
    output = output.dropna(axis=1)
    print(output)
    db.close()