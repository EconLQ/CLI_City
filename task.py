import argparse
import datetime
import geocoder
import json
import requests
import time
import typing
from functools import wraps


def read_data(file_name: str):
    with open(file_name, "r") as f:
        return json.load(f)


def write_data(file_name: str, data: list):
    with open(file_name, "w") as f:
        return json.dump(data, f, indent=3, ensure_ascii=False)


def get_geoname_id(city: str) -> str:
    """
    Get name of the city and returns its geoname id.
    geoname id is identifier in the GeoNames geographical database
    """
    g = geocoder.geonames(f"{city}", key="econlq", maxRows=2)
    return str(g.geonames_id)


def input_parser():
    """
    Parse through command line arguments
    """
    parser = argparse.ArgumentParser(description="Parse names of the cities")
    parser.add_argument('c', type=str, help="name of the city")
    return parser.parse_args()


def data_about_city(city: str) -> str:
    """
    Get user input and requesting city details for this city via World Geo API
    Returns string object with city details get from static_city_data.json
    """
    url = f"https://world-geo-data.p.rapidapi.com/cities/{get_geoname_id(city)}"

    response = requests.request("GET", url, headers=HEADERS,
                                params=QUERYSTRING)

    data.update(response.json())
    write_data("static_city_data.json", data=response.json())

    return f"--------------\n{data.get('name')}\n\n{data.get('country').get('name')}" \
                        f"\n{data.get('currency').get('code')}\n{data.get('population')}\n=============="


def invalid_city_name_exception(user_input: str):
    """
    Get user input as str and during writing data to the file it checks
    the status key value
    """
    try:
        if data.get("status") == "success":
            pass
        elif data.get("status") == "failed":
            print(f"--------------\n{user_input}\n\nInvalid city name: {user_input}\n==============")
    except AttributeError:
        print(f"--------------\nSystem Error\n==============")


def append_cities_to_file(url: str):
    """
    Get URL -> send request to World Geo Data API. After that appends received
    data to the file and return updated file
    """
    response = requests.request("GET", url, headers=HEADERS,
                                params=QUERYSTRING)

    data_2.append(response.json())
    return write_data("cities_test.json", data_2)


def is_there_more_than_two_cities(name_city: str) -> dict:
    """
    Get name of the city, and checks how many countries/places have the
    city with the same name. If the country is the same, then remove duplicated
    country and returns dict with unique keys (geoname_id) and values (country)
    """
    g = geocoder.geonames(f"{name_city}", key="econlq", maxRows=5)
    append_list = {}
    for result in g:
        append_list.update({result.geonames_id: result.country})
    temp = []
    final_result = dict()
    for key, value in append_list.items():
        if value not in temp:
            temp.append(value)
            final_result[key] = value
    return final_result


if __name__ == '__main__':
    data = read_data("static_city_data.json")
    data_2 = read_data("dynamic_cities_data.json")
    arg = input_parser()
    user_input = arg.c  # c -> name of the city
    QUERYSTRING = {"format": "json", "language": "en"}
    HEADERS = {
        "X-RapidAPI-Host": "world-geo-data.p.rapidapi.com",
        "X-RapidAPI-Key": "25fae88ae7mshfd287451137fc8dp10272ajsn3c85f02d7dd0"
    } # includes World Geo Data API host destination and my API key
    try:
        geonames_ids = [] # list where geoname ids of two cities will be written
        if len(is_there_more_than_two_cities(str(user_input))) == 2:
            cities = is_there_more_than_two_cities(user_input)
            for geoname_id in cities.keys():
                geonames_ids.append(geoname_id)

            for g_id in geonames_ids:
                url = f"https://world-geo-data.p.rapidapi.com/cities/{str(g_id)}"
                append_cities_to_file(url)
                # call time.sleep for 3 sec, as my API provider doesn't allow
                # more than 1 request/second
                time.sleep(3)
                for l in data_2:
                    print(
                        f"--------------\n{l.get('name')}\n\n{l.get('country').get('name')}" \
                        f"\n{l.get('currency').get('code')}\n{l.get('population')}\n==============")
        else:
            print(data_about_city(user_input))
    except (AttributeError, KeyboardInterrupt):
        invalid_city_name_exception(user_input)
    # writing empty list, so when run the file next time
    # we will have only two dictionaries in a list,
    # where we can get the requested data
    write_data("dynamic_cities_data.json", [])
