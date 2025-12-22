import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.infrastructure.database.connectors import SQLiteConnector

try:
    print("Initializing Connector...")
    # Explicitly use a file path
    db_path = "debug_db.sqlite"
    conn = SQLiteConnector(db_path)
    
    print("Connecting...")
    conn.connect()
    
    print("Creating table...")
    conn.execute_query("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, val TEXT)")
    
    print("Inserting...")
    conn.execute_query("INSERT INTO test (val) VALUES ('hello')")
    
    print("Fetching...")
    data = conn.fetch_data("SELECT * FROM test")
    print(f"Data: {data}")
    
    print("Disconnecting...")
    conn.disconnect()
    
    if os.path.exists(db_path):
        os.remove(db_path)
        
    print("Success!")
except Exception as e:
    import traceback
    traceback.print_exc()
