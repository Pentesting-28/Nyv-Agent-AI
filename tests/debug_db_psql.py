import sys
import os
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models.db_connectors import PostgresConnector

try:
    print("Initializing Connector...")
    conn = PostgresConnector(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=os.getenv("DB_PORT")
    )
    
    print("Connecting...")
    conn.connect()
    
    # print("Creating table...")
    # conn.execute_query("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, val TEXT)")
    
    # print("Inserting...")
    # conn.execute_query("INSERT INTO test (val) VALUES ('hello')")
    
    print("Fetching...")
    data = conn.fetch_data("SELECT * FROM information_schema.tables")
    print(f"Data: {data}")
    
    print("Disconnecting...")
    conn.disconnect()
    
    print("Success!")
except Exception as e:
    import traceback
    traceback.print_exc()
