import json
import shutil
import os
from rocksdict import Rdict, Options, WriteBatch, ReadOptions

DB_PATH = "./employee_db"

def clean_db():
    if os.path.exists(DB_PATH):
        try:
            shutil.rmtree(DB_PATH)
            print(f"Cleaned up existing database at {DB_PATH}")
        except Exception as e:
            print(f"Error cleaning up: {e}")

def setup_db():
    # 1. Define Column Families
    cf_names = ["employees", "idx_dept", "idx_manager", "idx_name"]
    
    # Rdict automatically opens the default CF
    db = Rdict(DB_PATH)
    
    # Check what CFs already exist in the opened DB
    existing_cfs = db.columns()
    
    for cf in cf_names:
        if cf not in existing_cfs:
            db.create_column_family(cf, Options())
    return db

def add_employee(db, emp_id, data):
    """
    Schema Design:
    - employees CF: Key='emp:<id>', Value=JSON Blob
    - idx_dept CF: Key='dept:<dept_name>:<id>', Value=''
    - idx_manager CF: Key='mgr:<mgr_name>:<id>', Value=''
    - idx_name CF: Key='name:<full_name>:<id>', Value=''
    """
    
    # Handles for Column Families (raw handles for WriteBatch)
    emp_cf_h = db.get_column_family_handle("employees")
    dept_idx_h = db.get_column_family_handle("idx_dept")
    mgr_idx_h = db.get_column_family_handle("idx_manager")
    name_idx_h = db.get_column_family_handle("idx_name")
    
    # 1. Main Key
    main_key = f"emp:{emp_id}"
    main_val = json.dumps(data)
    
    # 2. Index Keys
    dept_key = f"dept:{data['Department']}:{emp_id}"
    mgr_key = f"mgr:{data['Manager Name']}:{emp_id}"
    name_key = f"name:{data['Employee Name']}:{emp_id}"
    
    # Atomic Write using WriteBatch
    wb = WriteBatch()
    wb.put(main_key, main_val, emp_cf_h)
    wb.put(dept_key, "", dept_idx_h)
    wb.put(mgr_key, "", mgr_idx_h)
    wb.put(name_key, "", name_idx_h)
    
    db.write(wb)
    print(f"Added employee {emp_id}: {data['Employee Name']}")

def get_by_id(db, emp_id):
    # We can use the Rdict instance for lookups
    emp_cf = db.get_column_family("employees")
    try:
        val = emp_cf[f"emp:{emp_id}"]
        return json.loads(val)
    except KeyError:
        return None

def search_by_department(db, dept_name):
    print(f"\n--- Searching for employees in Department: {dept_name} ---")
    
    # Get Rdict instance for iteration
    dept_idx = db.get_column_family("idx_dept")
    emp_cf = db.get_column_family("employees")
    
    # Seek to the first entry for this department
    it = dept_idx.iter()
    it.seek(f"dept:{dept_name}:")
    
    found = []
    while it.valid():
        key = it.key()
        # Ensure we are still in the same department (prefix check)
        if not key.startswith(f"dept:{dept_name}:"):
            break
            
        # Extract EmpID from the index key
        emp_id = key.split(":")[-1]
        
        # Fetch full record from main CF
        emp_data = json.loads(emp_cf[f"emp:{emp_id}"])
        found.append(emp_data)
        it.next()
    
    return found

def run_demo():
    clean_db()
    db = setup_db()
    
    # Sample Employees
    employees = [
        {
            "ID": "E101",
            "Employee Name": "Alice Johnson",
            "City": "New York",
            "Address": "123 Wall St",
            "Manager Name": "Bob Smith",
            "Designation": "Senior Engineer",
            "Department": "Engineering",
            "Joining Date": "2022-01-15",
            "Active": 1,
            "Last Date": None
        },
        {
            "ID": "E102",
            "Employee Name": "Charlie Brown",
            "City": "San Francisco",
            "Address": "456 Market St",
            "Manager Name": "Bob Smith",
            "Designation": "QA Lead",
            "Department": "Engineering",
            "Joining Date": "2023-05-10",
            "Active": 1,
            "Last Date": None
        },
        {
            "ID": "E201",
            "Employee Name": "David Wilson",
            "City": "London",
            "Address": "789 Canary Wharf",
            "Manager Name": "Alice Johnson",
            "Designation": "Sales Rep",
            "Department": "Sales",
            "Joining Date": "2021-11-20",
            "Active": 0,
            "Last Date": "2024-01-01"
        }
    ]
    
    print("Populating Database...")
    for emp in employees:
        add_employee(db, emp['ID'], emp)
        
    # Test Lookups
    print("\nIndividual Lookup (E101):")
    print(get_by_id(db, "E101"))
    
    # Test Index Search
    results = search_by_department(db, "Engineering")
    for r in results:
        print(f"  - {r['Employee Name']} ({r['Designation']})")

    db.close()

if __name__ == "__main__":
    run_demo()
