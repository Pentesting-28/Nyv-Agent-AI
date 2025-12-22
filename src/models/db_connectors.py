from typing import Any, List, Dict, Optional, Union
import pandas as pd
from sqlalchemy import create_engine, text, Engine
from sqlalchemy.exc import SQLAlchemyError
from .base_connector import BaseConnector

class DatabaseConnector(BaseConnector):
    """
    Base implementation for SQLAlchemy-based database connectors.
    """
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.engine: Optional[Engine] = None

    def connect(self) -> None:
        if not self.engine:
            self.engine = create_engine(self.connection_string)
            # Test connection
            try:
                with self.engine.connect() as conn:
                    pass
            except Exception as e:
                self.engine = None
                raise ConnectionError(f"Failed to connect to database: {str(e)}")

    def disconnect(self) -> None:
        if self.engine:
            self.engine.dispose()
            self.engine = None

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        if not self.engine:
            self.connect()
        
        try:
            with self.engine.connect() as conn:
                # SQLAlchemy text() handles parameter binding safely
                result = conn.execute(text(query), params or {})
                if result.returns_rows:
                    return [dict(row._mapping) for row in result]
                else:
                    conn.commit()
                    return {"status": "success", "rows_affected": result.rowcount}
        except SQLAlchemyError as e:
            raise Exception(f"Database error executing query: {str(e)}")

    def fetch_data(self, query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        if not self.engine:
            self.connect()
        
        try:
            return pd.read_sql(query, self.engine, params=params)
        except Exception as e:
            raise Exception(f"Error fetching data: {str(e)}")

    def get_schema_info(self) -> Dict[str, Any]:
        if not self.engine:
            self.connect()
            
        from sqlalchemy import inspect
        insp = inspect(self.engine)
        
        schema_info = {}
        table_names = insp.get_table_names()
        
        for table in table_names:
            columns = []
            for col in insp.get_columns(table):
                columns.append({
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col["nullable"]
                })
            schema_info[table] = columns
            
        return schema_info

class MySQLConnector(DatabaseConnector):
    def __init__(self, host, user, password, database, port=3306):
        # mysql+pymysql://user:password@host:port/dbname
        conn_str = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
        super().__init__(conn_str)

class PostgresConnector(DatabaseConnector):
    def __init__(self, host, user, password, database, port=5432):
        # postgresql+psycopg2://user:password@host:port/dbname
        conn_str = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
        super().__init__(conn_str)

class SQLiteConnector(DatabaseConnector):
    def __init__(self, db_path):
        # sqlite:///path/to/db
        conn_str = f"sqlite:///{db_path}"
        super().__init__(conn_str)
