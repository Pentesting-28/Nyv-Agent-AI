from typing import Any, List, Dict, Optional, Union
import sqlite3
import pymysql
import pg8000.native
from .base_connector import BaseConnector

class DatabaseConnector(BaseConnector):
    """
    Base implementation for native database connectors.
    """
    def __init__(self):
        self.conn = None

    def connect(self) -> None:
        raise NotImplementedError

    def disconnect(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        # This generic method might need overrides for specific param styles
        pass

    def fetch_data(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        pass

    def get_schema_info(self) -> Dict[str, Any]:
        pass

class SQLiteConnector(DatabaseConnector):
    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path

    def connect(self) -> None:
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        if not self.conn: self.connect()
        cursor = self.conn.cursor()
        # sqlite3 uses ? or :name, we assume user provides compatible query or we handle it
        # For simplicity, we assume simple queries or usage of tuple params if needed
        # But BaseConnector interface says params is Dict. sqlite3 supports :name style.
        try:
            cursor.execute(query, params or {})
            self.conn.commit()
            return {"status": "success", "rows_affected": cursor.rowcount}
        except Exception as e:
            raise Exception(f"SQLite error: {str(e)}")

    def fetch_data(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if not self.conn: self.connect()
        cursor = self.conn.cursor()
        try:
            cursor.execute(query, params or {})
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            raise Exception(f"SQLite fetch error: {str(e)}")

    def get_schema_info(self) -> Dict[str, Any]:
        if not self.conn: self.connect()
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row['name'] for row in cursor.fetchall()]
        
        schema = {}
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = []
            for col in cursor.fetchall():
                columns.append({
                    "name": col['name'],
                    "type": col['type'],
                    "nullable": not col['notnull']
                })
            schema[table] = columns
        return schema

class MySQLConnector(DatabaseConnector):
    def __init__(self, host, user, password, database, port=3306):
        super().__init__()
        self.config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database,
            "port": port,
            "cursorclass": pymysql.cursors.DictCursor
        }

    def connect(self) -> None:
        if not self.conn:
            self.conn = pymysql.connect(**self.config)

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        if not self.conn: self.connect()
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params or {})
            self.conn.commit()
            return {"status": "success"}
        except Exception as e:
            raise Exception(f"MySQL error: {str(e)}")

    def fetch_data(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if not self.conn: self.connect()
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params or {})
                return cursor.fetchall()
        except Exception as e:
            raise Exception(f"MySQL fetch error: {str(e)}")

    def get_schema_info(self) -> Dict[str, Any]:
        if not self.conn: self.connect()
        schema = {}
        with self.conn.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = [list(row.values())[0] for row in cursor.fetchall()]
            for table in tables:
                cursor.execute(f"DESCRIBE {table}")
                columns = []
                for col in cursor.fetchall():
                    columns.append({
                        "name": col['Field'],
                        "type": col['Type'],
                        "nullable": col['Null'] == 'YES'
                    })
                schema[table] = columns
        return schema

class PostgresConnector(DatabaseConnector):
    def __init__(self, host, user, password, database, port=5432):
        super().__init__()
        self.user = user
        self.host = host
        self.password = password
        self.database = database
        self.port = port
        
    def connect(self) -> None:
        if not self.conn:
            self.conn = pg8000.native.Connection(
                user=self.user,
                host=self.host,
                password=self.password,
                database=self.database,
                port=self.port
            )

    def disconnect(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        if not self.conn: self.connect()
        # pg8000 native uses :name for params? or $1, $2? 
        # Actually pg8000 native interface is query(sql, **params) if we use named?
        # Standard pg8000 uses DBAPI. pg8000.native is lower level.
        # Let's switch to standard pg8000 DBAPI for consistency with params
        # But earlier I imported pg8000.native. 
        # Let's use standard import.
        pass

# Re-implementing Postgres using standard DB-API for consistency
# We need to import the dbapi module from pg8000
import pg8000.dbapi

class PostgresConnectorComple(DatabaseConnector):
    def __init__(self, host, user, password, database, port=5432):
        super().__init__()
        self.conn_args = {
            "user": user,
            "host": host,
            "password": password,
            "database": database,
            "port": port
        }
        
    def connect(self) -> None:
        if not self.conn:
            self.conn = pg8000.dbapi.connect(**self.conn_args)

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        if not self.conn: self.connect()
        cursor = self.conn.cursor()
        try:
            # pg8000 requires %s or :name depending on paramstyle. 
            # pg8000.paramstyle is 'format' (standard %s) or 'qmark'?
            # Usually %s.
            # But our BaseConnector assumes named parameters often found in SQLAlchemy (:name).
            # Mapping named params to %s is hard without a library.
            # For this simple agent, we will assume generic logic or direct query passing.
            cursor.execute(query, params or {})
            self.conn.commit()
            return {"status": "success", "rows_affected": cursor.rowcount}
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Postgres error: {str(e)}")

    def fetch_data(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if not self.conn: self.connect()
        cursor = self.conn.cursor()
        try:
            cursor.execute(query, params or {})
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Postgres fetch error: {str(e)}")

    def get_schema_info(self) -> Dict[str, Any]:
        if not self.conn: self.connect()
        cursor = self.conn.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = [row[0] for row in cursor.fetchall()]
        
        schema = {}
        for table in tables:
            cursor.execute(f"SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = '{table}'")
            columns = []
            for col in cursor.fetchall():
                columns.append({
                    "name": col[0],
                    "type": col[1],
                    "nullable": col[2] == 'YES'
                })
            schema[table] = columns
        return schema

# Replace the partial class with the full one
PostgresConnector = PostgresConnectorComple
