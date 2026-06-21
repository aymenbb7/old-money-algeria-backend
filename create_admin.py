from users.models import User

if not User.objects.filter(email='admin2@example.com').exists():
    User.objects.create_superuser('admin2@example.com', 'admin2', phone_number='0555555555')
    print("Superuser created")
else:
    print("Superuser already exists")
