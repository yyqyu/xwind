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
    print(response.status_code)
    return response

def query_faa(airport):

    #print(response.headers['Content-Type'])
    #print(type(response.json()))
    empty = False
    offset = 0
    notams = ["FAA"]
    while empty == False:
        response = request(offset, airport)
        offset += 30
        print(response.json().items())

    # Count to check if we got any notams in the request. Might need to change its place
        count = 0
        for key, value in response.json().items():
            try:
                for data in list(value):
                    # print(data)
                    icao = re.sub('(\\r\\n\\r\\n)','(\r\n)', data['icaoMessage'])
                    trad = data['traditionalMessage']
                    if icao == ' ' and data['featureName'] != "LTA" and data['notamNumber'] != "N/A":
                        # print(trad, '\n')
                        notams.append(trad)
                        count += 1
                    elif data['featureName'] != "LTA":
                        notams.append(icao)
                        # print(icao, '\n')
                        count += 1
            except:
                pass

            if count == 0:
                empty = True
                break
    return notams



    #to_write = jsbeautifier.beautify(response.text)

    # Write all notams into a file in JSON format
    #filename = (f"./test_scraper/response_{airport}.js")
    #with open(filename, "w") as file:
    #    file.write(to_write)

def main():
    notams = query_faa('jfk')
    print(notams)

if __name__ == "__main__":
    main()
