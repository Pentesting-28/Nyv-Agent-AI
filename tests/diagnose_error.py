import asyncio
import os
import sys
import traceback

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.tools.multi_db.db_tools import RunWriteQueryTool

# Set DB to SQLite for this test
os.environ["DB_TYPE"] = "sqlite"
os.environ["DB_PATH"] = "diagnose.sqlite"

async def main():
    try:
        tool = RunWriteQueryTool()
        print("Executing CREATE TABLE...")
        res = await tool.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER)")
        print(f"Result: {res}")
        
        print("Executing INSERT...")
        # This might be where it fails?
        res = await tool.execute("INSERT INTO test (id) VALUES (1)")
        print(f"Result: {res}")

    except Exception:
        traceback.print_exc()
    finally:
        if os.path.exists("diagnose.sqlite"):
            os.remove("diagnose.sqlite")

if __name__ == "__main__":
    asyncio.run(main())
