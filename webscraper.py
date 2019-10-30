import requests
from bs4 import BeautifulSoup
import jsbeautifier
from cs50 import get_string

# Web scraper for FAA notams from https://notams.aim.faa.gov/notamSearch/


def main():

    airport = get_string("Airport: ")

    param = {"searchType": '0',
             "designatorsForLocation": airport,
             "latMinutes": "0",
             "latSeconds": "0",
             "longMinutes": "0",
             "longSeconds": "0",
             "radius": "10",
             "sortColumns": " 5 false",
             "sortDirection": "true",
             "radiusSearchOnDesignator": "false",
             "latitudeDirection": "N",
             "longitudeDirection": "W",
             "flightPathBuffer": "4",
             "flightPathIncludeNavaids": "true",
             "flightPathIncludeArtcc": "false",
             "flightPathIncludeTfr": "false",
             "flightPathIncludeRegulatory": "false",
             "flightPathResultsType": "ALL NOTAMs",
             "offset": "0",
             "notamsOnly": "false",
             }

    response = requests.get("https://notams.aim.faa.gov/notamSearch")
    response = requests.post("https://notams.aim.faa.gov/notamSearch/search",
                             data=param)

    print (response.status_code)
    print (response.headers['Content-Type'])

    to_write = jsbeautifier.beautify(response.text)

    # filename = ("response_{airport}.js")
    # with open(filename, "w") as file:
    #     file.write(to_write)

    print(to_write)


if __name__ == "__main__":
    main()
