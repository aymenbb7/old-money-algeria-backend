from users.models import User

u, created = User.objects.get_or_create(email='admin3@example.com', defaults={'username': 'admin3'})
u.set_password('admin3')
u.is_staff = True
u.is_superuser = True
u.save()
print("Superuser admin3 created/updated")
