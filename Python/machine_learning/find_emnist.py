from sklearn.datasets import fetch_openml

def try_fetch(name_or_id):
    print(f"Trying to fetch: {name_or_id}")
    try:
        kwargs = {'as_frame': False, 'parser': 'liac-arff'}
        if isinstance(name_or_id, int):
            data = fetch_openml(data_id=name_or_id, **kwargs)
        else:
            data = fetch_openml(name=name_or_id, **kwargs)
        print(f"SUCCESS: Found {data.details['name']} (ID: {data.details['id']})")
        print(f"Shape: {data.data.shape}")
        print(f"Target example: {data.target[:5]}")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

# Try common EMNIST IDs/names
# 20072 is often EMNIST Letters
# 'emnist_letters'
# 'EMNIST_Letters'
candidates = [
    'emnist_letters',
    'EMNIST_Letters',
    20072, # EMNIST Letters
    40996  # Fashion MNIST usually, but checking
]

for cand in candidates:
    if try_fetch(cand):
        break
