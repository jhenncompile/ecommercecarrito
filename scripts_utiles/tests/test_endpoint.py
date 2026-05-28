import urllib.request as ur
import urllib.error as ue
import json

req = ur.Request('http://157.173.102.129/api/token/', data=json.dumps({"username":"user1@empresa1.local","password":"user123456"}).encode(), headers={'Content-Type': 'application/json', 'Host': '157.173.102.129'})
try:
    ur.urlopen(req)
except ue.HTTPError as e:
    html = e.read().decode()
    open('error_500.html', 'w', encoding='utf-8').write(html)

