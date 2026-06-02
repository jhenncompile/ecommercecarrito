import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework_simplejwt.tokens import RefreshToken
from apps.customers.users.models.usuario import Usuario
import requests

# Generar token para el primer usuario
user = Usuario.objects.first()
refresh = RefreshToken.for_user(user)
token = str(refresh.access_token)

url = "http://192.168.100.244:8001/api/pedidos/33/cambiar-estado/"
headers = {
    "Authorization": f"Bearer {token}",
    "Host": "tecno",
    "Content-Type": "application/json"
}
data = {"estado": "ENTREGADO"}

print("Realizando petición a:", url)
response = requests.post(url, headers=headers, json=data)
print("Status:", response.status_code)
print("Response:", response.text)
