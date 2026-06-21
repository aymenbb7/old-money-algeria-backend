import requests
import json
import time

def run_test():
    # Login
    print("Logging in...")
    login_res = requests.post('http://127.0.0.1:8001/api/v1/auth/login/', json={
        'email': 'admin2@test.com',
        'password': 'adminpassword2'
    })
    if login_res.status_code != 200:
        print("Login failed:", login_res.text)
        # Attempt to create admin
        from django.contrib.auth import get_user_model
        import os, django
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.base")
        django.setup()
        User = get_user_model()
        User.objects.create_superuser('admin2@test.com', 'adminpassword2')
        login_res = requests.post('http://127.0.0.1:8001/api/v1/auth/login/', json={'email': 'admin2@test.com', 'password': 'adminpassword2'})

    token = login_res.json()['access']
    print("Got token")

    data = {
        'name': 'Dashboard Test Product',
        'slug': 'dashboard-test-product',
        'description': 'Full desc',
        'short_description': 'Short desc',
        'price': '10.00',
        'status': 'DRAFT',
        'tags': '',
        'is_featured': 'False',
        'is_bestseller': 'False',
        'is_new_arrival': 'False',
        'variants': json.dumps([{"size": "M", "color": "Black", "stock": 10}])
    }
    
    # We will upload a dummy image
    files = {
        'images': ('test.jpg', b'dummy content', 'image/jpeg')
    }

    print("Sending POST request to /api/v1/products/...")
    res = requests.post(
        'http://127.0.0.1:8001/api/v1/products/',
        headers={'Authorization': f'Bearer {token}'},
        data=data,
        files=files
    )

    print("Status code:", res.status_code)
    try:
        print("JSON Response:", res.json())
    except:
        print("HTML Response text (first 1000 chars):", res.text[:1000])

if __name__ == '__main__':
    run_test()
