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


def write_data(file_name: str, data: (list, dict)):
    with open(file_name, "w") as f:
        return json.dump(data, f, indent=3, ensure_ascii=False)


def request_api_data(_url: str):
    querystring = {"format": "json", "language": "en"}
    headers = {
        "X-RapidAPI-Host": "world-geo-data.p.rapidapi.com",
        "X-RapidAPI-Key": keys.get("X-RapidAPI-Key")
    }
    return requests.request("GET", _url, headers=headers, params=querystring)


def line_printer(*args):
    line_beg = "--------------"
    line_end = "=============="
    print(line_beg, f"{args[0]}", "", f"{args[1]}", line_end, sep="\n")\
        if len(args) != 1 \
        else print(line_beg, f"{args[0]}", line_end, sep="\n")


def get_geoname_id(city: str) -> str:
    """
    Get name of the city and returns its geoname id.
    geoname id is identifier in the GeoNames geographical database
    """
    g = geocoder.geonames(f"{city}", key=keys.get("geonames_api_key"), maxRows=2)
    if g.geonames_id is not None:
        return str(g.geonames_id)


def input_parser():
    """
    Parse through command line arguments
    """
    parser = argparse.ArgumentParser(description="Parse names of the cities")
    parser.add_argument('c', type=str, help="name of the city", nargs="+")
    return parser.parse_args()


def data_about_one_city(city: str):
    """
    Get user input and requesting city details for this city via World Geo API
    Returns string object with city details get from static_city_data.json
    """
    _url = f"https://world-geo-data.p.rapidapi.com/cities/{get_geoname_id(city)}"
    write_data("static_city_data.json",
               static_city_data.update(request_api_data(_url).json()) or {})
    if isinstance(get_geoname_id(city), str):
        return line_printer(f"{static_city_data.get('name')}\n"
                            f"\n{static_city_data.get('country').get('name')}"
                            f"\n{static_city_data.get('currency').get('code')}"
                            f"\n{static_city_data.get('population')}")
    else:
        return line_printer(f"{user_input[0]}\n"
                            f"\nInvalid city name: {user_input[0]}")


def append_cities_to_file(_url: str):
    """
    Appends received data to the file and returns updated file
    """
    return write_data("dynamic_cities_data.json",
                      dynamic_cities_data.append(request_api_data(_url).json()))


def is_there_more_than_two_cities(name_city: str) -> dict:
    """
    Get name of the city, and checks how many countries/places have the
    city with the same name. If the country is the same, then remove duplicated
    country and returns dict with unique keys (geoname_id) and values (country)
    """
    g = geocoder.geonames(f"{name_city}", key=keys.get("geonames_api_key"),
                          maxRows=5)
    append_list = {result.geonames_id: result.country for result in g}
    temp = []
    final_result = {}
    for key, value in append_list.items():
        if value not in temp:
            temp.append(value)
            final_result[key] = value
    return final_result


if __name__ == '__main__':
    static_city_data = read_data("static_city_data.json")
    dynamic_cities_data = read_data("dynamic_cities_data.json")
    keys = read_data("keys.json")
    arg = input_parser()
    user_input = arg.c  # c -> name of the city

    try:
        geonames_ids = [] # list where geoname ids of two cities will be written
        if len(is_there_more_than_two_cities(str(user_input))) == 2:
            cities = is_there_more_than_two_cities(user_input)
            geonames_ids.extend(iter(cities.keys()))
            for g_id in geonames_ids:
                url = f"https://world-geo-data.p.rapidapi.com/cities/{str(g_id)}"
                append_cities_to_file(url)
                # call time.sleep for 3 sec, as my API provider doesn't allow
                # more than 1 request/second
                time.sleep(3)
                for l in dynamic_cities_data:
                    line_printer(f"{l.get('name')}\n\n{l.get('country').get('name')}"
                        f"\n{l.get('currency').get('code')}\n{l.get('population')}")
        else:
            print(data_about_one_city(user_input))
    except (AttributeError, KeyboardInterrupt):
        line_printer("System Error")
    # writing empty list, so when run the file next time
    # we will have only two dictionaries in a list, where we can get the requested data
    write_data("dynamic_cities_data.json", [])
