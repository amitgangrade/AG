from rocksdict import Rdict

DB_PATH = "./employee_db"

def list_sst_mapping():
    db = Rdict(DB_PATH)
    files = db.live_files()
    
    print(f"{'SST File':<20} | {'Column Family':<15} | {'Size (Bytes)':<15}")
    print("-" * 55)
    
    # live_files() returns a list of dicts with file metadata
    for f in files:
        if f["name"].endswith(".sst"):
            print(f"{f['name']:<20} | {f['column_family_name']:<15} | {f['size']:<15}")
    
    db.close()

if __name__ == "__main__":
    list_sst_mapping()
