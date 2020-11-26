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
    print(coord1, coord2)

    notams = requests.get(
        f"https://plan.navcanada.ca/weather/api/alpha/?",
        params={'point': f'{airport}|site|{coord1},{coord2}', 'alpha': 'notam', 'notam_choice': 'english'}
        )

    notams_list = ["CANADA"]
    # Iterate over result from 'notams', by skipping the first element
    # print(list(notams.json().items())[0:1])
    for key, value in list(notams.json().items())[1:]:
        for data in value:
            # Store data in new variable for readability
            entry = data['text']

            # Check for french RSC
            if '000000F' in entry :
                continue
            elif 'NOTAMJ' in entry :
                # print(entry)
                notams_list.append((entry, '\n'))
            else:
                # Remove french part of notams
                notams_list.append((entry[:entry.find('\n\nFR:')], '\n'))
                # print(entry.find('\n\nFR:'))
                # Adding +1 solved the last character notam issue

    # print(notams_list)
    return notams_list

    # Only show first element (now, notam count and messages)
    #for key, value in list(notams.json().items())[:1]:
        #print(value)

if __name__ == "__main__":
    main()