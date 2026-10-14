"""Ex1 - client of the public CityBikes API.

Usage: python ex1_citybikes_client.py [city]      (default: Milano)
"""
import sys

import requests


class BikeCatalog:
    def __init__(self, base_url="https://api.citybik.es"):
        self.base_url = base_url

    def get_json(self, path):
        # TODO: GET base_url + path with timeout=10, call raise_for_status(), return the JSON
        raise NotImplementedError("TODO Ex1: GET the path, check the status, return response.json()")

    def networks_of_city(self, city):
        # hint: path /v2/networks?fields=id,name,href,location ; compare location["city"] ignoring case
        raise NotImplementedError("TODO Ex1: return the networks whose city matches")

    def stations_of_network(self, network):
        # hint: network["href"] is the path of the network; stations are in data["network"]["stations"]
        raise NotImplementedError("TODO Ex1: return the list of stations of the network")


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
