import requests
from bs4 import BeautifulSoup
import jsbeautifier
from cs50 import get_string
import re

# Proof of concept
# Web scraper for FAA notams from https://notams.aim.faa.gov/notamSearch/


def request(offset, airport):

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
             "offset": offset,  # need to change this otherwise it only shows the first 30 notams....
             "notamsOnly": "false",
             }


    response = requests.post("https://notams.aim.faa.gov/notamSearch/search",
                                data=param)
    return response

def query_faa(airport):

    empty = False
    offset = 0
    notams = []
    while empty == False:
        response = request(offset, airport)
        offset += 30

    # Count to check if we got any notams in the request. Might need to change its place
        count = 0
        notams_list = []
        for key, value in response.json().items():
            try:
                for data in list(value):
                    icao = re.sub('(\\r\\n\\r\\n)','(\r\n)', data['icaoMessage'])
                    trad = data['traditionalMessage']
                    ident = data['icaoId']
                    if icao == ' ' and data['featureName'] != "LTA" and data['notamNumber'] != "N/A":
                        notams_list.append((trad, ident))
                        count += 1
                    elif data['featureName'] != "LTA":
                        notams_list.append((icao, ident, "FAA"))
                        count += 1
            except:
                pass

            if count == 0:
                empty = True
                break
        notams.extend(notams_list)
    return notams

def main():
    notams = query_faa('jfk')

if __name__ == "__main__":
    main()
