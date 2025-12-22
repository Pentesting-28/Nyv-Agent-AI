import os
from typing import Dict, Optional
from dotenv import load_dotenv
from src.infrastructure.database.connectors import (
    MySQLConnector,
    PostgresConnector,
    SQLiteConnector,
    BaseConnector
)

# Load environment variables
load_dotenv()

class DatabaseConnectionManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnectionManager, cls).__new__(cls)
            cls._instance.connections: Dict[str, BaseConnector] = {}
            cls._instance._initialize_connections()
        return cls._instance

    def _initialize_connections(self):
        """
        Initializes connections based on environment variables.
        Looks for DB_CONNECTION_{NAME}_TYPE patterns.
        """
        # Default Primary Connection
        db_type = os.getenv("DB_TYPE", "").lower()
        if db_type:
            try:
                connector = self._create_connector(db_type)
                if connector:
                    self.connections["primary"] = connector
            except Exception as e:
                print(f"Failed to initialize primary database: {e}")

    def _create_connector(self, db_type: str, prefix: str = "") -> Optional[BaseConnector]:
        """
        Helper to create a connector based on prefix (e.g., 'DB_' or 'DB_SECONDARY_').
        """
        if not prefix:
            # Use 'DB_' as default prefix for standard env vars
            host = os.getenv("DB_HOST", "localhost")
            user = os.getenv("DB_USER", "root")
            password = os.getenv("DB_PASSWORD", "")
            dbname = os.getenv("DB_NAME", "test")
            port = int(os.getenv("DB_PORT", 3306))
            path = os.getenv("DB_PATH", "database.sqlite") # For SQLite
        else:
            # Not fully implemented for multi-db env vars yet, but extensible
            pass

        if db_type == "mysql":
            return MySQLConnector(host, user, password, dbname, port)
        elif db_type == "postgres" or db_type == "postgresql":
            # Postgres usually defaults to 5432
            if port == 3306: port = 5432 
            return PostgresConnector(host, user, password, dbname, port)
        elif db_type == "sqlite":
            return SQLiteConnector(path)
        else:
            return None

    def get_connection(self, name: str = "primary") -> BaseConnector:
        """
        Retrieves a connection by name.
        """
        connector = self.connections.get(name)
        if not connector:
            raise ValueError(f"Connection '{name}' not found. Available: {list(self.connections.keys())}")
        return connector

    def list_connections(self) -> list:
        return list(self.connections.keys())
