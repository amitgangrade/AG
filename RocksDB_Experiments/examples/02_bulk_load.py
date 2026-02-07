import json
import os
import shutil
import time
import random
from faker import Faker
from rocksdict import Rdict, Options, WriteBatch, ReadOptions

DB_PATH = "./employee_db"
TOTAL_RECORDS = 50000
BATCH_SIZE = 5000

fake = Faker()

def clean_db():
    if os.path.exists(DB_PATH):
        try:
            shutil.rmtree(DB_PATH)
            print(f"Cleaned up existing database at {DB_PATH}")
        except Exception as e:
            print(f"Error cleaning up: {e}")

def setup_db():
    print("Initializing Database and Column Families...")
    cf_names = ["employees", "idx_dept", "idx_manager", "idx_name"]
    db = Rdict(DB_PATH)
    existing_cfs = db.columns()
    for cf in cf_names:
        if cf not in existing_cfs:
            db.create_column_family(cf, Options())
    return db

def generate_bulk_data(db):
    print(f"Starting bulk load of {TOTAL_RECORDS} records...")
    start_time = time.time()
    
    # Get handles once
    emp_cf_h = db.get_column_family_handle("employees")
    dept_idx_h = db.get_column_family_handle("idx_dept")
    mgr_idx_h = db.get_column_family_handle("idx_manager")
    name_idx_h = db.get_column_family_handle("idx_name")
    
    departments = ["Engineering", "Sales", "Marketing", "HR", "Finance", "Legal", "Operations", "Product"]
    designations = ["Junior", "Senior", "Lead", "Staff", "Manager", "Director", "VP"]
    
    wb = WriteBatch()
    count = 0
    
    for i in range(1, TOTAL_RECORDS + 1):
        emp_id = f"E{i:05d}"
        name = fake.name()
        dept = random.choice(departments)
        manager = fake.name()
        
        data = {
            "ID": emp_id,
            "Employee Name": name,
            "City": fake.city(),
            "Address": fake.address().replace("\n", ", "),
            "Manager Name": manager,
            "Designation": f"{random.choice(designations)} {dept}",
            "Department": dept,
            "Joining Date": str(fake.date_between(start_date='-5y', end_date='today')),
            "Active": random.choice([0, 1]),
            "Last Date": str(fake.date_between(start_date='today', end_date='+2y')) if random.random() < 0.1 else None
        }
        
        # Prepare Batch
        main_key = f"emp:{emp_id}"
        dept_key = f"dept:{dept}:{emp_id}"
        mgr_key = f"mgr:{manager}:{emp_id}"
        name_key = f"name:{name}:{emp_id}"
        
        wb.put(main_key, json.dumps(data), emp_cf_h)
        wb.put(dept_key, "", dept_idx_h)
        wb.put(mgr_key, "", mgr_idx_h)
        wb.put(name_key, "", name_idx_h)
        
        count += 1
        
        # Commit batch
        if count % BATCH_SIZE == 0:
            db.write(wb)
            wb = WriteBatch() 
            print(f"  Loaded {count}/{TOTAL_RECORDS} records...")
            
    # Final write for any remaining items
    if not wb.is_empty():
        db.write(wb)
        
    end_time = time.time()
    print(f"\nBulk load completed in {end_time - start_time:.2f} seconds.")

def verify_load(db):
    print("\nVerifying Data Load...")
    emp_cf = db.get_column_family("employees")
    idx_dept = db.get_column_family("idx_dept")
    
    # 1. Check total count (estimate)
    est_keys = emp_cf.property_value("rocksdb.estimate-num-keys")
    print(f"Estimated keys in employees CF: {est_keys}")
    
    # 2. Random Point Lookup
    random_id = f"E{random.randint(1, TOTAL_RECORDS):05d}"
    print(f"Point Lookup for {random_id}:")
    try:
        val = emp_cf[f"emp:{random_id}"]
        print(f"  {val[:100]}...") # Show first 100 chars
    except KeyError:
        print(f"  Error: {random_id} not found!")

    # 3. Department Search
    test_dept = "Engineering"
    print(f"Counting employees in {test_dept} via index...")
    it = idx_dept.iter()
    it.seek(f"dept:{test_dept}:")
    dept_count = 0
    while it.valid() and it.key().startswith(f"dept:{test_dept}:"):
        dept_count += 1
        it.next()
    print(f"  Found {dept_count} employees in {test_dept}.")

if __name__ == "__main__":
    clean_db() # Ensure fresh start
    db = setup_db()
    generate_bulk_data(db)
    verify_load(db)
    db.close()
