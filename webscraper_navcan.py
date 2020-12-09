import requests
from cs50 import get_string
import re
import itertools
import json


def query_navcanada(idents):
    airports = idents
    coord1 = []
    coord2 = []

    for airport in airports:
        response = requests.get(
            f"https://plan.navcanada.ca/weather/api/search/en?",
            params=[('include_polygons', 'true'), ('filter[value]', airport)]
            )

        response_split = response.text.split('"')
        coord1.append(response_split[15])
        coord2.append(response_split[17])
    print(coord1, coord2)

    requestor = ""
    for (x, y, z) in zip(airports, coord1, coord2):
        requestor += 'point='
        requestor += x
        requestor += '|site|'
        requestor += y
        requestor += ','
        requestor += z
        requestor += '&'
    print(requestor)
    notams = requests.get(
        f"https://plan.navcanada.ca/weather/api/alpha/?",
        params=(f'{requestor}alpha=notam&notam_choice=english')
        )

    notams_list = []
    tracker = 0
    # Iterate over result from 'notams', by skipping the first element
    # print(list(notams.json().items())[0:1])

    for key, value in list(notams.json().items())[1:]:
        notams_test = []
        for data in value:
            # Store data in new variable for readability
            entry = data['text']
            test = data['position']['pointReference']
            no_french = entry[:entry.find('\n\nFR:')]
            # Check for french RSC
            if '000000F' in entry :
                continue
            elif 'NOTAMJ' in entry :
                notams_test.insert(tracker+1,(entry, test, "CANADA"))
                tracker += 1
            else:
                # Remove french part of notams
                notams_test.append((no_french, test, "CANADA"))
                tracker += 1
        notams_list.extend(notams_test)
    return notams_list

    # Only show first element (now, notam count and messages)
    #for key, value in list(notams.json().items())[:1]:
        #print(value)

if __name__ == "__main__":
    main()
