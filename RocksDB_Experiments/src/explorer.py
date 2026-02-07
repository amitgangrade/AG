import streamlit as st
import json
import pandas as pd
import os
import rocksdict
from rocksdict import Rdict, Options, AccessType

st.set_page_config(page_title="RocksDB Employee Explorer", layout="wide")

# Handle relative paths regardless of where streamlit is run from
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# DB is in the parent directory relative to src/
DB_PATH = os.path.join(os.path.dirname(SCRIPT_DIR), "employee_db")

def get_db():
    if not os.path.exists(DB_PATH):
        st.error(f"Database directory not found at: {os.path.abspath(DB_PATH)}")
        return None
    try:
        # Open in read-only mode to avoid locking issues with other processes
        # and to ensure we don't accidentally modify the 50k dataset.
        return Rdict(DB_PATH, Options(), access_type=AccessType.read_only())
    except Exception as e:
        st.error(f"Error opening database: {e}")
        return None

def main():
    st.title("🪨 RocksDB Employee Explorer")
    st.markdown("---")

    # We use a context manager if possible, but Rdict in rocksdict might not support it 
    # as a standard 'with' block for DB. We'll handle close manually.
    db = get_db()
    if not db:
        st.warning("Please ensure the database exists and is not locked by another process.")
        return

    # Sidebar
    st.sidebar.header("Navigation")
    
    # Discovery: Rdict.list_cf is a reliable way to find existing CFs on disk
    try:
        all_cfs = Rdict.list_cf(DB_PATH)
    except:
        all_cfs = db.columns()
    
    if not all_cfs:
        st.error("No Column Families found in this database.")
        db.close()
        return

    selected_cf_name = st.sidebar.selectbox("Select Column Family", all_cfs)
    
    # Row Limit option
    st.sidebar.markdown("---")
    st.sidebar.header("Display Options")
    row_limit = st.sidebar.slider("Number of rows to display", min_value=10, max_value=1000, value=100, step=10)

    # Secondary Search Feature
    st.sidebar.markdown("---")
    st.sidebar.header("Secondary Search")
    search_type = st.sidebar.radio("Search By", ["Employee ID", "Department", "Manager"])
    search_query = st.sidebar.text_input(f"Enter {search_type}")

    col1, col2 = st.columns([1, 1])

    with col1:
        if selected_cf_name:
            st.subheader(f"CF View: {selected_cf_name}")
            try:
                cf_handle = db.get_column_family(selected_cf_name)
                
                # Show entries based on row_limit
                data = []
                it = cf_handle.iter()
                it.seek_to_first()
                
                count = 0
                while it.valid() and count < row_limit:
                    data.append({"Key": it.key(), "Value (Raw)": it.value()})
                    it.next()
                    count += 1
                
                if data:
                    df = pd.DataFrame(data)
                    st.table(df)
                    if count == row_limit:
                        st.info(f"Showing first {row_limit} records only.")
                else:
                    st.info("Column Family is empty.")
            except Exception as e:
                st.error(f"Error reading CF {selected_cf_name}: {e}")
        else:
            st.warning("Please select a Column Family from the sidebar.")

    with col2:
        st.subheader("Details / Search Results")
        
        if search_query:
            try:
                if search_type == "Employee ID":
                    emp_cf = db.get_column_family("employees")
                    val = emp_cf[f"emp:{search_query}"]
                    st.json(json.loads(val))
                
                elif search_type == "Department":
                    idx_dept = db.get_column_family("idx_dept")
                    emp_cf = db.get_column_family("employees")
                    
                    it = idx_dept.iter()
                    it.seek(f"dept:{search_query}:")
                    
                    results = []
                    while it.valid() and it.key().startswith(f"dept:{search_query}:"):
                        emp_id = it.key().split(":")[-1]
                        try:
                            emp_data = json.loads(emp_cf[f"emp:{emp_id}"])
                            results.append(emp_data)
                        except:
                            pass
                        it.next()
                        if len(results) > 50: # Limit UI display
                            break
                    
                    if results:
                        st.success(f"Found {len(results)} matches (showing top 50)")
                        st.write(pd.DataFrame(results))
                    else:
                        st.error("No employees found in this department.")

                elif search_type == "Manager":
                    idx_mgr = db.get_column_family("idx_manager")
                    emp_cf = db.get_column_family("employees")
                    
                    it = idx_mgr.iter()
                    it.seek(f"mgr:{search_query}:")
                    
                    results = []
                    while it.valid() and it.key().startswith(f"mgr:{search_query}:"):
                        emp_id = it.key().split(":")[-1]
                        try:
                            emp_data = json.loads(emp_cf[f"emp:{emp_id}"])
                            results.append(emp_data)
                        except:
                            pass
                        it.next()
                        if len(results) > 50: break
                    
                    if results:
                        st.success(f"Found {len(results)} matches")
                        st.write(pd.DataFrame(results))
                    else:
                        st.error("No employees found for this manager.")
            except KeyError:
                st.error(f"Record not found for query: {search_query}")
            except Exception as e:
                st.error(f"Search error: {e}")
        else:
            st.info("Select a search type and enter a query in the sidebar.")

    db.close()

if __name__ == "__main__":
    main()
