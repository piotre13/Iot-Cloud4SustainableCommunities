import time

import requests


class BikeCatalog:
    def __init__(self, base_url):
        self.base_url = base_url

    def data_on_city(self, city_name):
        response = requests.get(f"{self.base_url}/v2/networks/?field=location")
        data = response.json()
        city_networks_hrefs = []
        city_networks_data = []
        for network in data["networks"]:
            if network["location"]["city"].lower() == city_name.lower():
                city_networks_hrefs.append(network["href"])

        # perform requests to get all networks data
        for href in city_networks_hrefs:
            network_response = requests.get(f"{self.base_url}{href}")
            time.sleep(2)  # to avoid overwhelming the server
            network_data = network_response.json()
            city_networks_data.append(network_data)
            # process network_data as needed

        return city_networks_data

    def stats_on_city(self, city_name):
        city_networks_data = self.data_on_city(city_name)
        city_networks_stats = {}
        for net in city_networks_data:
            city_networks_stats[net["network"]["name"]] = {}
            net_info = {}
            net_info["largest_station"] = (None, 0)  # (station_name, n_slots)
            net_info["most_free"] = (None, 0)  # (station_name, n_free_bikes)

            for sta in net["network"]["stations"]:
                if "slots" in sta["extra"]:
                    if sta["extra"]["slots"] > net_info["largest_station"][1]:
                        net_info["largest_station"] = (
                            sta["name"],
                            sta["extra"]["slots"],
                        )
                if "free_bikes" in sta:
                    if sta["free_bikes"] > net_info["most_free"][1]:
                        net_info["most_free"] = (sta["name"], sta["free_bikes"])
            city_networks_stats[net["network"]["name"]] = net_info

        return city_networks_stats


if __name__ == "__main__":
    base_url = "http://api.citybik.es"
    bike_catalog = BikeCatalog(base_url)
    print(bike_catalog.stats_on_city("Barcelona"))
    # print(f"Largest network: {largest_network} with {station_count} stations")
    # city = "Milano"
    # total_networks, networks_in_city = bike_catalog.stats_on_city(city)
