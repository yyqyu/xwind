import requests
from cs50 import get_string
import re

result = requests.get(
    "https://plan.navcanada.ca/weather/api/search/en?include_polygons=true&filter[value]=cy&_=1583981516261")

result_list = []


for key, value in list(result.json().items()):
    print(len(key))
    # for x in range(len(value[x].items())):
    for x in value[y].items():
        print(x)
        y = y + 1
