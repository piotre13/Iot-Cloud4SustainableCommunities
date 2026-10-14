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


# TODO Ex2: GET /add, /sub, /mul, /div with params={"a": 10, "b": 4} and show() each response
# TODO Ex2: POST to base_url with json={"operation": "add", "operands": [1, 2, 3]}
# TODO Ex2: provoke errors (division by zero, missing parameter, unknown operation) and show()
raise NotImplementedError("TODO Ex2: write the client calls (see the comments above)")
