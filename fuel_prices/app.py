from litestar.response import Template
from litestar import Litestar, get
from pathlib import Path
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.template.config import TemplateConfig
import requests
import json


def get_data() -> dict:
    links = {
        "asda": "https://storelocator.asda.com/fuel_prices_data.json",
        "applegreen": "https://applegreenstores.com/fuel-prices/data.json",
        "ascona": "https://fuelprices.asconagroup.co.uk/newfuel.json",
        "bp": "https://www.bp.com/en_gb/united-kingdom/home/fuelprices/fuel_prices_data.json",
        "esso": "https://fuelprices.esso.co.uk/latestdata.json",
        "morrisons": "https://www.morrisons.com/fuel-prices/fuel.json",
        "motor_fuel_group": "https://fuel.motorfuelgroup.com/fuel_prices_data.json",
        "rontec": "https://www.rontec-servicestations.co.uk/fuel-prices/data/fuel_prices_data.json",
        "sainsburys": "https://api.sainsburys.co.uk/v1/exports/latest/fuel_prices_data.json",
        "sgn": "https://www.sgnretail.uk/files/data/SGN_daily_fuel_prices.json",
        "shell": "https://www.shell.co.uk/fuel-prices-data.html",


    }
#"tesco": "https://www.tesco.com/fuel_prices/fuel_prices_data.json"
    parsed_data = {}
    headers = {"user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/120.0.0.0 Safari/537.36'}
    for name, link in links.items():
        print(f"Parsing {name}")
        parsed_data[name] = json.loads(requests.get(link, headers=headers).text)
    return parsed_data


@get("/", cache=1800)
async def index() -> Template:
    parsed_data = get_data()

    local_stations_dict = [{"Kelso": [{"sainsburys": "pinnaclehill"}]},
                           {"Galashiels": [{"asda": "galashiels"}, {"shell": "galashiels"}, {"esso": "galashiels"}]},
                           {"Straiton, Edinburgh": [{"asda": "Loanhead"}, {"sainsburys": "straiton"}]},
                           {"Berwick Upon Tweed": [{"asda": "Tweedmouth"}, {"morrisons": "Berwick"},
                                                   ]}
                           ]
    # {"tesco": "Berwick-upon-Tweed"}
    local_stations_result = {}
    for location in local_stations_dict:
        for place_name, local_stations in location.items():
            local_stations_result[place_name] = []
            for local_station in local_stations:
                for station in parsed_data[list(local_station.keys())[0]]["stations"]:
                    if list(local_station.values())[0].lower() in station["address"].lower():
                        for fuel_name, price in station["prices"].items():
                            if price < 10:
                                station["prices"][fuel_name] = round(station["prices"][fuel_name] * 100, 1)
                        local_stations_result[place_name].append(station)

    return Template(template_name="index.html.jinja2", context={"local_stations": local_stations_result, "fuel": "petrol"})


@get("/diesel", cache=1800)
async def diesel() -> Template:
    parsed_data = get_data()

    local_stations_dict = [{"Kelso": [{"sainsburys": "pinnaclehill"}]},
                           {"Galashiels": [{"asda": "galashiels"}, {"shell": "galashiels"}, {"esso": "galashiels"}]},
                           {"Straiton, Edinburgh": [{"asda": "Loanhead"}, {"sainsburys": "straiton"}]},
                           {"Berwick Upon Tweed": [{"asda": "Tweedmouth"}, {"morrisons": "Berwick"},
                                                   ]}
                           ]
    # {"tesco": "Berwick-upon-Tweed"}
    local_stations_result = {}
    for location in local_stations_dict:
        for place_name, local_stations in location.items():
            local_stations_result[place_name] = []
            for local_station in local_stations:
                for station in parsed_data[list(local_station.keys())[0]]["stations"]:
                    if list(local_station.values())[0].lower() in station["address"].lower():
                        for fuel_name, price in station["prices"].items():
                            if price < 10:
                                station["prices"][fuel_name] = round(station["prices"][fuel_name] * 100, 1)
                        local_stations_result[place_name].append(station)

    return Template(template_name="index.html.jinja2", context={"local_stations": local_stations_result, "fuel": "diesel"})


template_config = TemplateConfig(directory=Path("templates"), engine=JinjaTemplateEngine, )
app = Litestar([index, diesel], template_config=template_config)
print("Server running!")
