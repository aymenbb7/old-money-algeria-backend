import requests
import json
import os

BASE_URL = 'http://127.0.0.1:8001/api/v1'

def login():
    res = requests.post(f"{BASE_URL}/auth/login/", json={
        "email": "admin3@example.com",
        "password": "admin3"
    })
    return res.json().get("access")

def run():
    token = login()
    headers = {"Authorization": f"Bearer {token}"}
    
    with open("dummy.jpg", "wb") as f:
        f.write(b"dummy")

    # Upload Hero Image
    print("Uploading Hero Image...")
    with open("dummy.jpg", "rb") as f:
        res = requests.patch(f"{BASE_URL}/homepage-content/1/", files={"hero_image": f}, headers=headers)
        print("Hero PATCH Status:", res.status_code)
        
    print("\nHero Image Response:")
    res2 = requests.get(f"{BASE_URL}/homepage/banners/")
    print(json.dumps(res2.json(), indent=2))

    # Create Product with Variants and Image
    print("\nCreating Product...")
    data = {
        "name": "Debug Product",
        "slug": "debug-product",
        "description": "Test",
        "price": "199.00",
        "status": "PUBLISHED",
        # Simulating how the frontend sends variants:
        "variants": '[{"size":"M","colors":["Noir","Vert"],"stock":10}, {"size":"S","colors":["Red"],"stock":10}]'
    }
    with open("dummy.jpg", "rb") as f:
        files = {
            "images": ("dummy.jpg", f, "image/jpeg")
        }
        res3 = requests.post(f"{BASE_URL}/products/", data=data, files=files, headers=headers)
        print("Product POST Status:", res3.status_code)
        print("Product POST Response:", res3.text)

    # Get Product
    res4 = requests.get(f"{BASE_URL}/products/")
    products = res4.json().get('results', [])
    if products:
        p = [x for x in products if x['name'] == 'Debug Product'][0]
        print("\nProduct Variants:")
        print(json.dumps(p.get('variants', []), indent=2))
        print("\nProduct Images:")
        print(json.dumps(p.get('images', []), indent=2))
        
    if os.path.exists("dummy.jpg"):
        os.remove("dummy.jpg")

if __name__ == "__main__":
    run()
