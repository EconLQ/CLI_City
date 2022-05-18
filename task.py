import argparse
import datetime
import geocoder
import json
import requests
import typing
from functools import wraps


def read_data(file_name: str):
    with open(file_name, "r") as f:
        return json.load(f)


def write_data(file_name: str, data: dict):
    with open(file_name, "w") as f:
        return json.dump(data, f, indent=3, ensure_ascii=False)


def city_details(name_of_city: str):
    g = geocoder.geonames(f"{name_of_city}", key="econlq")
    return f"--------------\n{g.address}\n\n{g.country}" \
           f"\n{g.population}\n=============="


def get_geoname_id(city: str):
    g = geocoder.geonames(f"{city}", key="econlq")
    return str(g.geonames_id)


def input_parser():
    """
    Parse through command line arguments
    """
    parser = argparse.ArgumentParser(description="Parse names of the cities")
    parser.add_argument('c', type=str, help="name of the city")
    return parser.parse_args()


def test_func(city : str):
    url = f"https://world-geo-data.p.rapidapi.com/cities/{get_geoname_id(city)}"

    querystring = {"format": "json", "language": "en"}

    headers = {
        "X-RapidAPI-Host": "world-geo-data.p.rapidapi.com",
        "X-RapidAPI-Key": "25fae88ae7mshfd287451137fc8dp10272ajsn3c85f02d7dd0"
    }

    response = requests.request("GET", url, headers=headers,
                                params=querystring)

    data.update(response.json())
    write_data("cities_data.json", data=response.json())

    currency = data.get("currency").get("code")
    g = geocoder.geonames(f"{city}", key="econlq")
    return f"--------------\n{g.address}\n\n{g.country}" \
           f"\n{currency}\n{g.population}\n=============="
    # return f"{name_of_the_city}\n{population}\n{currency}"


if __name__ == '__main__':
    # arg = input_parser()
    # user_input = arg
    data = read_data("cities_data.json")
    print(test_func("Tel Aviv"))
    # if not data.get("status"):
    #     print(test_func(str(user_input.lower())))
    # else:
    #     print(f"--------------\n{user_input}\n\nInvalid city name: {user_input}\n==============")
