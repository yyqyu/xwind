import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

# import os

from cs50 import SQL
from flask import redirect, session, request
from functools import wraps
from itertools import islice


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database/xwind.db")

# Get ident code
def get_ident(station):
    if not request.form.get("station"):
        station = request.args.get("station")
    else:
        request.form.get("station")

    if len(station) <= 4:
        try:
            ident = check_if_exist(station)
        except Exception:
            try:
                ident = check_local_code(station)
            except Exception:
                ident = search(station)
    else:
        ident = search(station)

    return ident


# Check if station match with ICAO or IATA ident
def check_if_exist(station):
    station = station.upper()

    if len(station) == 4:
        icao = db.execute("SELECT ident FROM airports WHERE ident=:station",
                          station=station)[0]["ident"]
    else:
        icao = db.execute("SELECT ident FROM airports WHERE "
                          "iata_code=:station", station=station)[0]["ident"]

    return icao


# Check if station match with a local_code
def check_local_code(station):
    station = station.upper()
    icao = db.execute("SELECT ident FROM airports WHERE local_code=:station",
                      station=station)[0]["ident"]

    return icao


# Lookup through list of aiport names if nothing else matched
def search(station):
    station = station.upper()
    n = len(station) + 1
    while True:
        try:
            ident = db.execute(
                "SELECT ident FROM airports WHERE name LIKE "
                f"'%{station[:n]}%' ORDER BY type DESC")[0]["ident"]
            break
        except Exception:
            n = n - 1
    return ident


# Retrieve the raw text of last available TAF
def last_metar_raw(ident):
    url_response = urllib.request.urlopen(
        "https://www.aviationweather.gov/adds/dataserver_current/httpparam?"
        "datasource=metars"                     # 'metars' or 'tafs'
        "&requestType=retrieve"                 # -- don't touch --
        "&format=xml"                           # -- don't touch --
        "&mostRecent=true"                      # use if only want latest
        "&hoursBeforeNow=2"                     # required even if latest
        f"&stationString={ident}")              # station ICAO code

    root = ET.fromstring(url_response.read())

    if not (root.findall('data/METAR')):
        raw_text = "No weather available"
    else:
        if root.find('data/METAR/station_id').text[:1] == "K":
            if root.find('data/METAR/metar_type').text == "METAR":
                raw_text = ("METAR " + root.find('data/METAR/raw_text').text)
            elif root.find('data/METAR/metar_type').text == "SPECI":
                raw_text = ("SPECI " + root.find('data/METAR/raw_text').text)
        elif root.find('data/METAR/raw_text').text[9:][:2] == "00":
            raw_text = ("METAR " + root.find('data/METAR/raw_text').text)
        else:
            raw_text = ("SPECI " + root.find('data/METAR/raw_text').text)

    return raw_text


# Retrieve the raw text of last available TAF
def last_taf_raw(ident):
    url_response = urllib.request.urlopen(
        "https://www.aviationweather.gov/adds/dataserver_current/httpparam?"
        "datasource=tafs"                       # 'metars' or 'tafs'
        "&requestType=retrieve"                 # -- don't touch --
        "&format=xml"                           # -- don't touch --
        "&mostRecent=true"                      # use if only want latest
        "&hoursBeforeNow=12"                    # required even if latest
        f"&stationString={ident}")              # station ICAO code

    root = ET.fromstring(url_response.read())

    if not (root.find('data/TAF')):
        raw_text = " "
    else:
        raw_text = root.find('data/TAF/raw_text').text

    return raw_text


# Make TAF more readeable (like directly on ADDS)
def format_taf(raw_text):
    separate = raw_text.split()
    formatted = []
    for word in separate:
        if word[:2] == "FM":
            formatted.append("\n" + word + " ")
        elif word == ("TEMPO" or "BECMG" or "PROB30" or "PROB40"):
            formatted.append("\n" + word + " ")
        else:
            formatted.append(word + " ")

    new_text = ("".join(formatted))

    new_text_row = new_text.split('\n')
    return(new_text_row)


# Get name of  matching airport
def get_name(ident):
    name = db.execute(
        "SELECT name FROM airports WHERE ident = :ident",
        ident=ident)[0]["name"]
    return name


# Decorate routes to require login
# http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# Create a list of all existing wind directions in METAR and TAF
def wind_direction(ident):
    winddir = []
    url_response_metar = urllib.request.urlopen(
        "https://www.aviationweather.gov/adds/dataserver_current/httpparam?"
        "datasource=metars"                     # 'metars' or 'tafs'
        "&requestType=retrieve"                 # -- don't touch --
        "&format=xml"                           # -- don't touch --
        "&mostRecent=true"                      # use if only want latest
        "&hoursBeforeNow=1.25"                  # required even if latest
        f"&stationString={ident}")              # station ICAO code

    root_metar = ET.fromstring(url_response_metar.read())

    if not (root_metar.findall('data/METAR')):
        winddir.append(" ")
    else:
        winddir.append(root_metar.find('data/METAR/wind_dir_degrees').text)

    url_response_taf = urllib.request.urlopen(
        "https://www.aviationweather.gov/adds/dataserver_current/httpparam?"
        "datasource=tafs"                       # 'metars' or 'tafs'
        "&requestType=retrieve"                 # -- don't touch --
        "&format=xml"                           # -- don't touch --
        "&mostRecent=true"                      # use if only want latest
        "&hoursBeforeNow=1.25"                  # required even if latest
        f"&stationString={ident}")              # station ICAO code

    root_taf = ET.fromstring(url_response_taf.read())

    if not (root_taf.findall('data/TAF')):
        winddir.append(" ")
    else:
        for taf in root_taf.findall('data/TAF/forecast'):
            try:
                winddir.append(taf.find('wind_dir_degrees').text)
            except Exception:
                continue

    return winddir


# Create a list of all existing wind strength in METAR and TAF
def wind_strength(ident):
    windstr = []
    url_response_metar = urllib.request.urlopen(
        "https://www.aviationweather.gov/adds/dataserver_current/httpparam?"
        "datasource=metars"                     # 'metars' or 'tafs'
        "&requestType=retrieve"                 # -- don't touch --
        "&format=xml"                           # -- don't touch --
        "&mostRecent=true"                      # use if only want latest
        "&hoursBeforeNow=1.25"                  # required even if latest
        f"&stationString={ident}")              # station ICAO code

    root_metar = ET.fromstring(url_response_metar.read())

    if not (root_metar.findall('data/METAR')):
        windstr.append(" ")
    else:
        windstr.append(root_metar.find('data/METAR/wind_speed_kt').text)

    url_response_taf = urllib.request.urlopen(
        "https://www.aviationweather.gov/adds/dataserver_current/httpparam?"
        "datasource=tafs"                       # 'metars' or 'tafs'
        "&requestType=retrieve"                 # -- don't touch --
        "&format=xml"                           # -- don't touch --
        "&mostRecent=true"                      # use if only want latest
        "&hoursBeforeNow=1.25"                  # required even if latest
        f"&stationString={ident}")              # station ICAO code

    root_taf = ET.fromstring(url_response_taf.read())

    if not (root_taf.findall('data/TAF')):
        windstr.append(" ")
    else:
        for taf in root_taf.findall('data/TAF/forecast'):
            try:
                windstr.append(taf.find('wind_speed_kt').text)
            except Exception:
                continue

    return windstr


# Get list of each weather time
def weather_times(ident):
    wx_time = []
    url_response_metar = urllib.request.urlopen(
        "https://www.aviationweather.gov/adds/dataserver_current/httpparam?"
        "datasource=metars"                     # 'metars' or 'tafs'
        "&requestType=retrieve"                 # -- don't touch --
        "&format=xml"                           # -- don't touch --
        "&mostRecent=true"                      # use if only want latest
        "&hoursBeforeNow=1.25"                  # required even if latest
        f"&stationString={ident}")              # station ICAO code

    root_metar = ET.fromstring(url_response_metar.read())

    if not (root_metar.findall('data/METAR')):
        wx_time.append(" ")
    else:
        t = (root_metar.find('data/METAR/observation_time').text)[11:-4:]
        t = t.replace(":", "")
        wx_time.append(t + "Z")

    url_response_taf = urllib.request.urlopen(
        "https://www.aviationweather.gov/adds/dataserver_current/httpparam?"
        "datasource=tafs"                       # 'metars' or 'tafs'
        "&requestType=retrieve"                 # -- don't touch --
        "&format=xml"                           # -- don't touch --
        "&mostRecent=true"                      # use if only want latest
        "&hoursBeforeNow=1.25"                  # required even if latest
        f"&stationString={ident}")              # station ICAO code

    root_taf = ET.fromstring(url_response_taf.read())

    if not (root_taf.findall('data/TAF')):
        wx_time.append(" ")
    else:
        for taf in root_taf.findall('data/TAF/forecast'):
            try:
                if taf.find('wind_dir_degrees').text:
                    y = (taf.find('fcst_time_from').text)[11:-4:]
                    y = y.replace(":", "")
                    wx_time.append(y + "Z")
            except Exception:
                continue

    return wx_time


# Get list of each weather time's type
def weather_types(ident):
    wx_type = [] = []
    url_response_metar = urllib.request.urlopen(
        "https://www.aviationweather.gov/adds/dataserver_current/httpparam?"
        "datasource=metars"                     # 'metars' or 'tafs'
        "&requestType=retrieve"                 # -- don't touch --
        "&format=xml"                           # -- don't touch --
        "&mostRecent=true"                      # use if only want latest
        "&hoursBeforeNow=1.25"                  # required even if latest
        f"&stationString={ident}")              # station ICAO code

    root_metar = ET.fromstring(url_response_metar.read())

    print(root_metar.find('data/METAR/station_id').text[:1])

    if not (root_metar.findall('data/METAR')):
        wx_type.append(" ")
    elif root_metar.find('data/METAR/station_id').text[:1] == "K":
        wx_type.append(root_metar.find('data/METAR/metar_type').text)
    elif root_metar.find('data/METAR/raw_text').text[9:][:2] == "00":
        wx_type.append("METAR")
    else:
        wx_type.append("SPECI")

    url_response_taf = urllib.request.urlopen(
        "https://www.aviationweather.gov/adds/dataserver_current/httpparam?"
        "datasource=tafs"                       # 'metars' or 'tafs'
        "&requestType=retrieve"                 # -- don't touch --
        "&format=xml"                           # -- don't touch --
        "&mostRecent=true"                      # use if only want latest
        "&hoursBeforeNow=1.25"                  # required even if latest
        f"&stationString={ident}")              # station ICAO code

    root_taf = ET.fromstring(url_response_taf.read())

    if not (root_taf.findall('data/TAF')):
        wx_type.append(" ")
    else:
        wx_type.append("FROM")
        for taf in islice(root_taf.findall('data/TAF/forecast'), 1, None):
            try:
                if taf.find('wind_dir_degrees').text:
                    if taf.find('change_indicator').text == "FM":
                        wx_type.append("FROM")
                    elif taf.find('change_indicator').text == "TEMPO":
                        wx_type.append("TEMPO")
                    elif taf.find('change_indicator').text == "PROB":
                        if taf.find('change_indicator').text == "30":
                            wx_type.append("change_indicator")
                        elif taf.find('change_indicator').text == "40":
                            wx_type.append("PROB40")
                    elif taf.find('change_indicator').text == "BECMG":
                        wx_type.append("BECMG")
            except Exception:
                continue

    return wx_type


def runways(ident):
    runway_list = []
    rwys = db.execute(
        "SELECT runways.le_ident, runways.xhe_ident "
        "FROM runways "
        "WHERE runways.airport_ident=:ident "
        "ORDER BY length_ft DESC", ident=ident)
    for r in rwys:
        runway_list.append(r)
    return runway_list


def headings(ident):
    headings_list = []
    headings = db.execute(
        "SELECT runways.le_heading_degT, runways.xhe_heading_degT "
        "FROM runways "
        "WHERE runways.airport_ident=:ident "
        "ORDER BY length_ft DESC", ident=ident)
    for head in headings:
        headings_list.append(head)
    return headings_list


'''def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code,
                           bottom=escape(message)), code'''
