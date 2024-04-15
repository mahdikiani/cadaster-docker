import requests

r = requests.get("http://keygen:3000/key?x=1&y=2&z=3&")
print(r.text)
