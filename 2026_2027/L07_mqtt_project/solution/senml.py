import time


def senml_record(bn, n, u, v):
    """One SenML measurement, e.g. bn='house1/kitchen', n='temperature', u='Cel'.

    bn = base name, bt = base time (unix seconds); each entry in "e" has its name, unit,
    time relative to bt and value:
    {"bn": "house1/kitchen", "bt": 1791970000, "e": [{"n": "temperature", "u": "Cel", "t": 0, "v": 21.4}]}
    """
    return {"bn": bn, "bt": int(time.time()), "e": [{"n": n, "u": u, "t": 0, "v": v}]}
