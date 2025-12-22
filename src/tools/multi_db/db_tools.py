from typing import List, Dict, Any, Optional
from src.models.function_model import BaseTool, tool_registry
from .manager import DatabaseConnectionManager

class BaseDatabaseTool(BaseTool):
    def __init__(self, name: str, description: str, parameters: Dict[str, Any]):
        super().__init__(name, description, parameters)
        self.manager = DatabaseConnectionManager()

class ListTablesTool(BaseDatabaseTool):
    def __init__(self):
        super().__init__(
            name="db_list_tables",
            description="List all tables in the database.",
            parameters={
                "type": "object",
                "properties": {
                    "connection_name": {
                        "type": "string",
                        "description": "Name of the connection to use (default: 'primary')",
                        "default": "primary"
                    }
                },
                "required": []
            }
        )

    async def execute(self, connection_name: str = "primary") -> str:
        try:
            conn = self.manager.get_connection(connection_name)
            schema_info = conn.get_schema_info()
            tables = list(schema_info.keys())
            return f"Tables in database '{connection_name}':\n" + "\n".join([f"- {t}" for t in tables])
        except Exception as e:
            return f"Error listing tables: {str(e)}"

class GetSchemaTool(BaseDatabaseTool):
    def __init__(self):
        super().__init__(
            name="db_get_schema",
            description="Get the schema (columns) of a specific table.",
            parameters={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table"
                    },
                    "connection_name": {
                        "type": "string",
                        "description": "Connection name",
                        "default": "primary"
                    }
                },
                "required": ["table_name"]
            }
        )

    async def execute(self, table_name: str, connection_name: str = "primary") -> str:
        try:
            conn = self.manager.get_connection(connection_name)
            schema_info = conn.get_schema_info()
            
            if table_name not in schema_info:
                return f"Error: Table '{table_name}' not found."
                
            columns = schema_info[table_name]
            output = [f"Schema for table '{table_name}':"]
            for col in columns:
                output.append(f"- {col['name']} ({col['type']}) {'[Nullable]' if col['nullable'] else ''}")
                
            return "\n".join(output)
        except Exception as e:
            return f"Error getting schema: {str(e)}"

class RunReadQueryTool(BaseDatabaseTool):
    def __init__(self):
        super().__init__(
            name="db_run_read_query",
            description="Execute a SELECT query against the database.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The SQL SELECT query to execute"
                    },
                    "connection_name": {
                        "type": "string",
                        "description": "Connection name",
                        "default": "primary"
                    }
                },
                "required": ["query"]
            }
        )

    async def execute(self, query: str, connection_name: str = "primary") -> str:
        if not query.strip().lower().startswith("select"):
             return "Error: This tool only supports SELECT queries. Use 'db_run_write_query' for modifications."

        try:
            conn = self.manager.get_connection(connection_name)
            df = conn.fetch_data(query)
            if df.empty:
                return "Query returned no results."
            return df.to_string(index=False)
        except Exception as e:
            return f"Error executing query: {str(e)}"

class RunWriteQueryTool(BaseDatabaseTool):
    def __init__(self):
        super().__init__(
            name="db_run_write_query",
            description="Execute an INSERT, UPDATE, or DELETE query.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The SQL query to execute"
                    },
                    "connection_name": {
                        "type": "string",
                        "description": "Connection name",
                        "default": "primary"
                    }
                },
                "required": ["query"]
            }
        )

    async def execute(self, query: str, connection_name: str = "primary") -> str:
        # Basic safety check
        forbidden = ["drop table", "truncate table", "drop database"]
        if any(f in query.lower() for f in forbidden):
            return "Error: Destructive operations (DROP, TRUNCATE) are blocked for safety."

        try:
            conn = self.manager.get_connection(connection_name)
            result = conn.execute_query(query)
            return f"Query executed successfully. Result: {result}"
        except Exception as e:
            return f"Error executing query: {str(e)}"

# Register tools
list_tables_tool = ListTablesTool()
tool_registry.register(list_tables_tool)

get_schema_tool = GetSchemaTool()
tool_registry.register(get_schema_tool)

run_read_tool = RunReadQueryTool()
tool_registry.register(run_read_tool)

run_write_tool = RunWriteQueryTool()
tool_registry.register(run_write_tool)
