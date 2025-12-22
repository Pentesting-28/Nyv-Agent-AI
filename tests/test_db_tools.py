import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 1. Setup SQLite for testing - MUST BE DONE BEFORE IMPORTING tools.multi_db.db_tools
# This ensures the Singleton Manager initializes with these values instead of .env
os.environ["DB_TYPE"] = "sqlite"
os.environ["DB_PATH"] = "test_db_v2.sqlite"

from src.tools.multi_db.db_tools import ListTablesTool, RunReadQueryTool, RunWriteQueryTool

async def main():
    print("Beginning Database Tool Verification...")
    
    # Clean up previous test
    if os.path.exists("test_db_v2.sqlite"):
        try:
            os.remove("test_db_v2.sqlite")
        except:
            pass

    try:
        # Initialize tools
        # Note: In the real app, these are imported from db_tools which instantiates them.
        # Here we instantiate them again, sharing the same Singleton Manager.
        list_tool = ListTablesTool()
        write_tool = RunWriteQueryTool()
        read_tool = RunReadQueryTool()

        # 2. Test Write (Create Table)
        print("\n--- Testing Write (Create Table) ---")
        create_table_query = "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)"
        result = await write_tool.execute(create_table_query)
        print(result)

        # 3. Test Write (Insert Data)
        print("\n--- Testing Write (Insert Data) ---")
        insert_query = "INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com'), ('Bob', 'bob@example.com')"
        result = await write_tool.execute(insert_query)
        print(result)

        # 4. Test List Tables
        print("\n--- Testing List Tables ---")
        tables = await list_tool.execute()
        print(tables)

        # 5. Test Read (Select)
        print("\n--- Testing Read (Select) ---")
        select_query = "SELECT * FROM users"
        data = await read_tool.execute(select_query)
        print(data)

    finally:
        # Cleanup
        if os.path.exists("test_db.sqlite"):
            os.remove("test_db.sqlite")
        print("\nVerification Complete.")

if __name__ == "__main__":
    asyncio.run(main())
