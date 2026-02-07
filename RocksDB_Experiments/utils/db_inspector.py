from rocksdict import Rdict, Options, ReadOptions
import os

DB_PATH = "./employee_db"

def inspect_db():
    print(f"=== RocksDB Inspection: {DB_PATH} ===\n")
    
    if not os.path.exists(DB_PATH):
        print(f"Error: Path {DB_PATH} does not exist.")
        return

    # 1. List all Column Families
    print("1. Listing Column Families...")
    try:
        cfs = Rdict.list_cf(DB_PATH)
        print(f"Found Column Families: {cfs}\n")
    except Exception as e:
        print(f"Error listing CFs: {e}")
        return

    # 2. Open DB with all CFs and inspect properties
    print("2. Inspecting Properties for each CF...")
    # Rdict can be opened with specific options if needed, 
    # but for inspection we just need access.
    try:
        # Opening with all discovered CFs
        db = Rdict(DB_PATH) 
        
        # Note: In rocksdict, 'db' itself acts on the default or manages all.
        # We can iterate through cf names and get a handle for each.
        for cf_name in cfs:
            print(f"--- CF: {cf_name} ---")
            
            # Get the handle for this CF
            # If it's the default CF, we can just use 'db' or get it explicitly
            cf_handle = db.get_column_family(cf_name)
            
            # Common RocksDB properties
            properties = [
                "rocksdb.estimate-num-keys",
                "rocksdb.num-immutable-mem-table",
                "rocksdb.mem-table-flush-pending",
                "rocksdb.cur-size-active-mem-table",
                "rocksdb.stats", # This gives a large text output of RDB internals
            ]
            
            for prop in properties:
                val = cf_handle.property_value(prop)
                if prop == "rocksdb.stats":
                    print(f"\n[{prop}]:")
                    # stats can be very long, just show the first few lines or highlights
                    if val:
                        lines = val.split('\n')
                        for line in lines[:10]: # First 10 lines of stats
                            print(f"  {line}")
                        print("  ...")
                else:
                    print(f"{prop}: {val}")
            print()
            
        db.close()
    except Exception as e:
        print(f"Error during inspection: {e}")

if __name__ == "__main__":
    inspect_db()
