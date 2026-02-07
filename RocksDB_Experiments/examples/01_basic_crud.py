import gc
import shutil
import os
from rocksdict import Rdict, Options, WriteBatch, Snapshot, CompactOptions, WriteOptions, ReadOptions

DB_PATH = "./demo_db"

def clean_db():
    if os.path.exists(DB_PATH):
        try:
            shutil.rmtree(DB_PATH)
            print(f"Cleaned up existing database at {DB_PATH}")
        except Exception as e:
            print(f"Error cleaning up: {e}")

def run_demo():
    print("=== RocksDB Demo with rocksdict ===\n")
    
    clean_db()
    
    # 1. Opening Database
    print("1. Opening Database...")
    # Rdict (RocksDict) handles the DB connection.
    # It automatically creates the DB if it doesn't exist by default.
    db = Rdict(DB_PATH)
    print(f"Database opened at {DB_PATH}\n")

    # 2. Basic CRUD Operations
    print("2. Basic CRUD Operations...")
    
    # Put
    key1 = "user:1001"
    val1 = "Alice"
    print(f"Putting {key1} -> {val1}")
    db[key1] = val1
    
    # Get
    res1 = db[key1]
    print(f"Get {key1} -> {res1}")
    
    # Update
    val1_new = "Alice Smith"
    print(f"Updating {key1} -> {val1_new}")
    db[key1] = val1_new
    print(f"Get {key1} -> {db[key1]}")
    
    # Delete
    print(f"Deleting {key1}")
    del db[key1]
    
    try:
        print(f"Get {key1} -> {db[key1]}")
    except KeyError:
        print(f"Get {key1} -> Not Found (KeyError as expected)")
    print()

    # 3. Batch Operations
    print("3. Batch Operations (WriteBatch)...")
    # Batch writes are atomic and faster for multiple updates
    wb = WriteBatch()
    wb["user:1002"] = "Bob"
    wb["user:1003"] = "Charlie"
    wb["user:1004"] = "David"
    db.write(wb)
    print("Wrote batch of 3 users.")
    
    print(f"Verify user:1002: {db['user:1002']}")
    print(f"Verify user:1004: {db['user:1004']}")
    print()

    # 4. Iteration
    print("4. Iteration...")
    print("Iterating over all keys:")
    for key, value in db.items():
        print(f"  {key} => {value}")
        
    print("\nIterating keys starting with 'user:1003':")
    # rocksdict allows seeking by slicing/iter methods if available or just iterating sorted
    # Note: Rdict keys are bytes or strings. The iteration is sorted.
    iter_db = db.iter()
    iter_db.seek("user:1003")
    while iter_db.valid():
         print(f"  {iter_db.key()} => {iter_db.value()}")
         iter_db.next()
    print()

    # 5. Snapshots
    print("5. Snapshots...")
    # Create a snapshot
    snapshot = db.snapshot()
    print("Created Snapshot.")
    
    # Modify DB after snapshot
    print("Modifying DB: Deleting user:1002, Adding user:1005")
    del db["user:1002"]
    db["user:1005"] = "Eve"
    
    # Read from Snapshot (should see old state)
    print(f"Snapshot Read user:1002 -> {snapshot['user:1002']}")
    try:
         print(f"Snapshot Read user:1005 -> {snapshot['user:1005']}")
    except Exception as e:
         print(f"Snapshot Read user:1005 -> Not Found ({e})")
         
    # Read from Current DB (should see new state)
    try:
        print(f"Current DB Read user:1002 -> {db['user:1002']}")
    except KeyError:
        print("Current DB Read user:1002 -> Not Found (Expected)")
    print(f"Current DB Read user:1005 -> {db['user:1005']}")
    
    del snapshot # Clean up snapshot
    print()

    # 6. Column Families
    print("6. Column Families...")
    # Note: ColumnFamilies usually need to be defined at Open or Created explicitly.
    # rocksdict supports managing column families.
    cf_name = "log_data"
    print(f"Creating Column Family '{cf_name}'")
    
    # In rocksdict, we can create a new CF.
    cf_handle = db.create_column_family(cf_name, Options())
    
    # Accessing the CF
    # We can use the db instance to access CFs if we opened them or created them.
    # Writing to CF
    print(f"Putting 'log:1' -> 'Login event' into '{cf_name}'")
    # Use the returned Rdict instance (cf_handle) directly
    cf_handle["log:1"] = "Login event"
    
    # Reading from CF
    res_cf = cf_handle["log:1"]
    print(f"Get 'log:1' from '{cf_name}' -> {res_cf}")
    
    # Verify key doesn't exist in default CF
    try:
        print(f"Get 'log:1' from default -> {db['log:1']}")
    except KeyError:
        print("Get 'log:1' from default -> Not Found (Expected)")
    print()
    
    # 7. Compaction
    print("7. Manual Compaction...")
    # RocksDB auto-compacts, but we can trigger it manually.
    # range=None compacts the whole range.
    db.compact_range(None, None) 
    print("Compaction triggered.")
    print()

    # Closing
    print("Closing Database...")
    # Explicit close (or let GC handle it)
    db.close()
    print("Done.")

if __name__ == "__main__":
    try:
        run_demo()
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
