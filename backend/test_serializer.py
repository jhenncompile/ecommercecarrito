import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.customers.users.models.usuario import Usuario
from apps.customers.users.api.serializers import UsuarioCrudSerializer

try:
    user = Usuario.objects.first()
    if user:
        print("User:", user.email)
        data = UsuarioCrudSerializer(user).data
        print("Data:", data)
    else:
        print("No users found")
except Exception as e:
    import traceback
    traceback.print_exc()
