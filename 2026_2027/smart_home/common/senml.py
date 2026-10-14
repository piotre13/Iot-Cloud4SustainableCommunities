import time


def senml_record(bn, n, u, v):
    """One SenML measurement, e.g. bn='house1/kitchen', n='temperature', u='Cel'."""
    return {"bn": bn, "n": n, "u": u, "t": int(time.time()), "v": v}
