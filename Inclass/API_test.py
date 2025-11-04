import requests

response = requests.get("http://api.citybik.es/v2/networks/")
data = response.json()
print(type(data))
cnt = 0
tot_n = len(response.json()["networks"])
for network in response.json()["networks"]:
    endpoint = network['']["href"]
    net_response = requests.get(f"http://api.citybik.es{endpoint}")
    if "stations" in net_response.json():
        cnt += 1

print(f"Total networks: {tot_n}")
print(f"Networks with 'station' key: {cnt}")
print(response)
