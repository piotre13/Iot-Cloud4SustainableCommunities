"""Small client of the catalog: what any other service (controller, bot, ...) will do.

Usage: python catalog_client.py [catalog_url]
"""
import sys

import requests

catalog = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"

# TODO Ex4: 1. list houses and their rooms  2. read the thresholds of house1/kitchen
#           3. change t_max with a partial PUT  4. try an invalid PUT (t_min=40) and print the status code
#           5. list the registered devices
raise NotImplementedError("TODO Ex4: write the five steps above with requests")
