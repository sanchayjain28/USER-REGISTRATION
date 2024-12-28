import psycopg2
from psycopg2.extras import RealDictCursor
from settings import settings
import os

class Database:
    _instance = None

    def __new__(cls, db_url):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.db_url = os.getenv('DATABASE_URL')
            cls._instance.connection = None
        return cls._instance

    def connect(self):
        """Establish a database connection."""
        if self.connection is None:
            self.connection = psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
            self.create_tables()

    def create_tables(self):
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        with self.connection.cursor() as cursor:
            cursor.execute(create_users_table)
        self.connection.commit()

    def execute_query(self, query: str, params: tuple = None):
        """Execute a query."""
        if self.connection is None:
            raise RuntimeError("Database connection is not initialized. Call connect() first.")

        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            if query.strip().lower().startswith("select"):
                return cursor.fetchall()  # Fetch all rows for SELECT queries
            self.connection.commit()  # Commit changes for non-SELECT queries

    def disconnect(self):
        """Close the database connection."""
        if self.connection is not None:
            self.connection.close()
            self.connection = None


db = Database(f"postgresql://{settings['USER']}:{settings['PASSWORD']}@localhost:{settings['DB_PORT']}/{settings['DATABASE']}")
