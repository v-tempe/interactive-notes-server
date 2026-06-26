import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'interactive_notes.settings')
django.setup()

from django.contrib.auth.models import User

username = os.environ.get('ADMIN_USERNAME', 'admin')
password = os.environ.get('ADMIN_PASSWORD')
if not password:
    raise RuntimeError('You must provide ADMIN_PASSWORD in .env file.')
email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser {username} created successfully.")
else:
    print(f"Superuser {username} already exists.")
