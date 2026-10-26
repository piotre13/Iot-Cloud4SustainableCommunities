# Starts each reference solution on its own port, checks it, stops it. Run: python test_solutions.py
import subprocess
import sys
import time
import requests


def run(script, port, checks):
    proc = subprocess.Popen([sys.executable, script, str(port)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = f"http://localhost:{port}"
    try:
        for _ in range(50):  # wait until the server answers
            try:
                requests.get(base, timeout=0.5)
                break
            except requests.ConnectionError:
                time.sleep(0.2)
        for path, status, check in checks:
            r = requests.get(base + path)
            assert r.status_code == status, (script, path, r.status_code, r.text)
            assert check(r.json()), (script, path, r.json())
        print("OK  ", script)
    finally:
        proc.terminate()
        proc.wait()


run("mock_coding.py", 8170, [
    ("/comfort?temperature=28&humidity=45", 200, lambda j: j["comfort"] == "too_hot" and j["hvac_command"] == "OFF"),
    ("/comfort?temperature=15&humidity=45", 200, lambda j: j["comfort"] == "too_cold"),
    ("/comfort?temperature=22&humidity=75", 200, lambda j: j["comfort"] == "too_humid"),
    ("/comfort?temperature=22&humidity=40", 200, lambda j: j["comfort"] == "comfortable" and j["hvac_command"] == "OFF"),
    ("/comfort?temperature=abc&humidity=40", 400, lambda j: "error" in j),
    ("/comfort?temperature=22", 400, lambda j: "error" in j),
    ("/comfort?temperature=22&humidity=140", 400, lambda j: "error" in j),
])
run("past_sensors.py", 8171, [
    ("/sensors", 200, lambda j: len(j["readings"]) == 2),
    ("/sensors?type=light", 200, lambda j: len(j["readings"]) == 1 and 0 <= j["readings"][0]["value"] <= 1000),
    ("/sensors?type=temperature", 200, lambda j: "temperature:" in j["readings"][0]["message"]),
    ("/sensors?type=wind", 400, lambda j: "error" in j),
])
run("past_calculator.py", 8172, [
    ("/calculator/sum?operand_1=5&operand_2=25", 200,
     lambda j: j == {"operand_1": 5, "operand_2": 25, "operation": "sum", "result": 30}),
    ("/calculator/difference?operand_1=5&operand_2=25", 200, lambda j: j["result"] == -20),
    ("/calculator/multiplication?operand_1=5&operand_2=25", 200, lambda j: j["result"] == 125),
    ("/calculator/division?operand_1=5&operand_2=2", 200, lambda j: j["result"] == 2.5),
    ("/calculator/division?operand_1=5&operand_2=0", 400, lambda j: "error" in j),
    ("/calculator/power?operand_1=5&operand_2=2", 400, lambda j: "error" in j),
    ("/calculator/sum?operand_1=x&operand_2=2", 400, lambda j: "error" in j),
])
run("past_converter.py", 8173, [
    ("/convert/kilometers_to_miles?value=100", 200,
     lambda j: j == {"input_value": 100, "conversion": "kilometers_to_miles", "result": 62.13}),
    ("/convert/miles_to_kilometers?value=10", 200, lambda j: j["result"] == 16.09),
    ("/convert/celsius_to_fahrenheit?value=100", 200, lambda j: j["result"] == 212),
    ("/convert/fahrenheit_to_celsius?value=32", 200, lambda j: j["result"] == 0),
    ("/convert/parsecs?value=1", 400, lambda j: "error" in j),
    ("/convert/celsius_to_fahrenheit", 400, lambda j: "error" in j),
])
print("all passed")
