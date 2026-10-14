"""Ex1 - client of the public CityBikes API.

Usage: python ex1_citybikes_client.py [city]      (default: Milano)
"""
import sys

import requests


class BikeCatalog:
    def __init__(self, base_url="https://api.citybik.es"):
        self.base_url = base_url

    def get_json(self, path):
        # one place for timeout + HTTP error handling
        response = requests.get(self.base_url + path, timeout=10)
        response.raise_for_status()  # 4xx / 5xx -> exception
        return response.json()

    def networks_of_city(self, city):
        # ask only for the fields we need: the full list is big
        data = self.get_json("/v2/networks?fields=id,name,href,location")
        return [n for n in data["networks"]
                if n["location"]["city"].lower() == city.lower()]

    def stations_of_network(self, network):
        # "href" is the path of the network, e.g. /v2/networks/to-bike
        data = self.get_json(network["href"])
        return data["network"]["stations"]


if __name__ == "__main__":
    city = sys.argv[1] if len(sys.argv) > 1 else "Milano"
    catalog = BikeCatalog()
    try:
        networks = catalog.networks_of_city(city)
        if not networks:
            print(f"No bike network found in {city}")
        for network in networks:
            stations = catalog.stations_of_network(network)
            print(f"\n{network['name']} - {len(stations)} stations")
            for station in stations:
                # some networks do not publish these values: they are None
                print(f"  {station['name']}: free bikes={station['free_bikes']}, "
                      f"empty slots={station['empty_slots']}")
    except requests.exceptions.Timeout:
        print("The server did not answer in 10 seconds")
    except requests.exceptions.HTTPError as err:
        print("HTTP error:", err)
    except requests.exceptions.RequestException as err:
        print("Connection problem:", err)
