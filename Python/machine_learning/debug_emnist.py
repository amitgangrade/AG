from sklearn.datasets import fetch_openml
import numpy as np

def check_dataset(name_or_id):
    print(f"\nChecking {name_or_id}...")
    try:
        data = fetch_openml(name_or_id, as_frame=False, parser='liac-arff')
        print(f"SUCCESS: Found {data.details.get('name')} (ID: {data.details.get('id')})")
        print(f"Shape: {data.data.shape}")
        print(f"Target classes: {np.unique(data.target)}")
        return data
    except Exception as e:
        print(f"FAILED: {e}")
        return None

# 1. Inspect the weird ID 44071
check_dataset(44071)

# 2. Try EMNIST_Balanced (ID 40996 is Fashion, let's look for Balanced)
# Common EMNIST Balanced ID is 40996? No that was Fashion.
# Try by name
check_dataset('EMNIST_Balanced')
check_dataset('emnist_balanced')

# 3. Try EMNIST (generic)
check_dataset('EMNIST')
