import requests
import json
import os

BASE_URL = 'http://127.0.0.1:8001/api/v1'

def login():
    res = requests.post(f"{BASE_URL}/auth/login/", json={
        "email": "admin@example.com",
        "password": "admin"
    })
    return res.json().get("access")

def test():
    token = login()
    headers = {"Authorization": f"Bearer {token}"}
    
    with open("dummy.jpg", "wb") as f:
        f.write(b"dummy")
        
    data = {
        "name": "Cloudinary Test Product",
        "slug": "cloudinary-test-product",
        "description": "Test",
        "price": "199.00",
        "status": "PUBLISHED"
    }
    
    with open("dummy.jpg", "rb") as f:
        files = {
            "images": ("dummy.jpg", f, "image/jpeg")
        }
        res = requests.post(f"{BASE_URL}/products/", data=data, files=files, headers=headers)
        
    print("POST Status:", res.status_code)
    
    get_res = requests.get(f"{BASE_URL}/products/")
    products = get_res.json().get("results", [])
    if products:
        last_product = products[0]
        print("\nLatest Product Image Data:")
        print(json.dumps(last_product.get("images", []), indent=2))
        
    if os.path.exists("dummy.jpg"):
        os.remove("dummy.jpg")

if __name__ == "__main__":
    test()
