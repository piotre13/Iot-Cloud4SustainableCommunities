"""Client of the calculator service (ex2_calculator.py).

Usage: python ex2_client.py [base_url]      (default http://localhost:8080)
"""
import sys

import requests

base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"


def show(response):
    if response.status_code == 200:
        print(response.status_code, response.json())
    else:
        print(response.status_code, "ERROR")  # the body is an HTML error page


# GET: operation in the path, numbers in the query string
for op in ("add", "sub", "mul", "div"):
    show(requests.get(f"{base_url}/{op}", params={"a": 10, "b": 4}, timeout=10))

# POST: everything in the JSON body (json= sets the Content-Type header too)
show(requests.post(base_url, json={"operation": "add", "operands": [1, 2, 3]}, timeout=10))
show(requests.post(base_url, json={"operation": "mul", "operands": [2, 3, 4]}, timeout=10))

# errors
print("--- errors")
show(requests.get(f"{base_url}/div", params={"a": 1, "b": 0}, timeout=10))
show(requests.get(f"{base_url}/add", params={"a": 1}, timeout=10))
show(requests.get(f"{base_url}/power", params={"a": 1, "b": 2}, timeout=10))
show(requests.post(base_url, json={"operation": "pow", "operands": [1, 2]}, timeout=10))
