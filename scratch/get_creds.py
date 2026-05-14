import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from users.models import User, Author, Reader, AdminUser

with open('credentials.md', 'w') as f:
    f.write("# Project Credentials\n\n")
    f.write("Here are the credentials for the users currently populated in the system for testing.\n\n")
    
    # Superuser
    f.write("### Administrators\n")
    for u in User.objects.filter(is_superuser=True):
        f.write(f"- **Username:** `{u.username}` | **Password:** `admin` | **Type:** Superadmin\n")
    
    f.write("\n### Authors\n")
    for u in Author.objects.all():
        f.write(f"- **Username:** `{u.username}` | **Password:** `password` | **Domain Role:** {u.role}\n")
        
    f.write("\n### Readers\n")
    for u in Reader.objects.all():
        f.write(f"- **Username:** `{u.username}` | **Password:** `password` | **Domain Role:** {u.role}\n")
