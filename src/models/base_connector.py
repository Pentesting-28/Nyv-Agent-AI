from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional, Union
import pandas as pd

class BaseConnector(ABC):
    """
    Abstract base class for all database connectors.
    """

    @abstractmethod
    def connect(self) -> None:
        """Establishes the connection to the database."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Closes the connection."""
        pass

    @abstractmethod
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Executes a raw query against the database.
        Returns the raw result (cursor, list of dicts, etc. depending on implementation).
        """
        pass

    @abstractmethod
    def fetch_data(self, query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Executes a query and returns the results as a Pandas DataFrame.
        """
        pass

    @abstractmethod
    def get_schema_info(self) -> Dict[str, Any]:
        """
        Returns information about the database schema (tables, collections, etc.).
        """
        pass
