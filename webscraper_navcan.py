import requests
from cs50 import get_string
import re


def navcanada(ident):
    airport = ident
    print(airport)

    response = requests.get(
        f"https://plan.navcanada.ca/weather/api/search/en?",
        params=[('include_polygons', 'true'), ('filter[value]', airport)]
        )

    response_split = response.text.split('"')
    coord1 = response_split[15]
    coord2 = response_split[17]
    # print(coord1, coord2)

    notams = requests.get(
        f"https://plan.navcanada.ca/weather/api/alpha/?",
        params={'point': f'{coord1},{coord2},{airport},site', 'alpha': 'notam'}
        )

    notams_list = []
    # Iterate over result from 'notams', by skipping the first element
    for key, value in list(notams.json().items())[1:]:
        for data in value:
            # Store data in new variable for readability
            entry = data['text']

            # Check for french RSC
            if '000000F' in entry :
                continue
            else:
                # Remove french part of notams
                notams_list.append((entry[:entry.find('\n\nFR:')], ')\n'))

    return notams_list

    # Only show first element (now, notam count and messages)
    #for key, value in list(notams.json().items())[:1]:
        #print(value)

if __name__ == "__main__":
    main()