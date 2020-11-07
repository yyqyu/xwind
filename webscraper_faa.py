import requests
from bs4 import BeautifulSoup
import jsbeautifier
from cs50 import get_string
import re

# Proof of concept
# Web scraper for FAA notams from https://notams.aim.faa.gov/notamSearch/


def main():

    # Ask user for airport
    # !!!! Make multiple requests at the same time with offsets of 0 to whatever, if nothing comesback stop, then aggregate result.
    airport = get_string("Airport: ")
    offset = "150"

    param = {"searchType": '0',
             "designatorsForLocation": airport,
             "latMinutes": "0",
             "latSeconds": "0"
Wrong Airport Landings 
,
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
             "offset": offset,  # need to change this otherwise it only shows the first 30 notams....
             "notamsOnly": "false",
             }

    #response = requests.get("https://notams.aim.faa.gov/notamSearch")
    response = requests.post("https://notams.aim.faa.gov/notamSearch/search",
                             data=param)

    # Print to terminal some info to ensure request went well.
    print(response.status_code)
    #print(response.headers['Content-Type'])
    #print(type(response.json()))

    # Count to check if we got any notams in the request. Might need to change its place
    count = 0
    for key, value in response.json().items():
        try:
            for data in list(value):
                icao = re.sub('(\\r\\n\\r\\n)','(\r\n)', data['icaoMessage'])
                trad = data['traditionalMessage']
                if icao == ' ':
                    print(trad, '\n')
                    count += 1
                else:
                    print(icao, '\n')
                    count += 1
        except:
            pass

        if count == 0:
            print('Empty!')
            break



    #to_write = jsbeautifier.beautify(response.text)

    # Write all notams into a file in JSON format
    #filename = (f"./test_scraper/response_{airport}.js")
    #with open(filename, "w") as file:
    #    file.write(to_write)


if __name__ == "__main__":
    main()
