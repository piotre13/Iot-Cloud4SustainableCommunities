import time

import requests


class BikeCatalog:
    def __init__(self, base_url):
        self.base_url = base_url
        url = self.base_url + "/v2/networks"
        response = requests.get(url)
        self.data = response.json()
        # print(self.data)

    def get_networks(self, city):
        city_net_hrefs = []
        for net in self.data["networks"]:
            ct = net["location"]["city"]
            if ct.lower() == city.lower():
                city_net_hrefs.append(net["href"])
        return city_net_hrefs

    def stats(self, city):
        hrefs = self.get_networks(city)
        info_dict = {}
        for h in hrefs:
            id = h.split("/")[-1]
            info_dict[id] = {"largest": (None, 0), "most_free": (None, 0)}
            url = self.base_url + h
            net_data = requests.get(url).json()["network"]
            time.sleep(2)
            for station in net_data["stations"]:
                if 'slots' in station["extra"]:
                    if station["extra"]["slots"] > info_dict[id]["largest"][1]:
                        info_dict[id]["largest"] = (
                            station["name"],
                            station["extra"]["slots"],
                        )

                if station["free_bikes"] > info_dict[id]["most_free"][1]:
                    info_dict[id]["most_free"] = (
                        station["name"],
                        station["free_bikes"],
                    )
        return info_dict


if __name__ == "__main__":
    base_url = "http://api.citybik.es"
    bike_catalog = BikeCatalog(base_url)
    print(bike_catalog.stats("Barcelona"))





