"""
Quick script to set superuser password
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.accounts.models import User

# Get or create superuser
user = User.objects.get(username='admin')
user.set_password('admin123')
user.role = 'admin'
user.is_verified = True
user.save()

print(f"✓ Superuser '{user.username}' password set to 'admin123'")
print(f"✓ Role: {user.role}")
print(f"✓ Email: {user.email}")
