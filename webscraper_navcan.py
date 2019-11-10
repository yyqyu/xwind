import requests
from bs4 import BeautifulSoup
import jsbeautifier
from cs50 import get_string


def main():
    airport = get_string("Canadian airport: ")

    response = requests.get(f"https://plan.navcanada.ca/weather/api/search/en?include_polygons=true&filter[value]={airport}")
    print(response.text[1])


if __name__ == "__main__":
    main()