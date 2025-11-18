import requests

res = requests.post("http://127.0.0.1:8080/sum", json={"ciao": 23, "d": 45, "dis": 456})

print(res)
print(res.json())
