import requests
import json

BASE_URL = 'http://127.0.0.1:8001/api/v1'

def print_json(data):
    print(json.dumps(data, indent=2))

def run():
    print("=== ISSUE 1 & 2: Variants & Images ===")
    res = requests.get(f"{BASE_URL}/products/")
    products = res.json().get('results', [])
    if products:
        print("Variants for first product:")
        print_json(products[0].get('variants', []))
        print("\nImages for first product:")
        print_json(products[0].get('images', []))
    else:
        print("No products found.")

    print("\n=== ISSUE 3: Hero Image ===")
    res2 = requests.get(f"{BASE_URL}/homepage/banners/")
    print("Banners response:")
    print_json(res2.json())

if __name__ == "__main__":
    run()
