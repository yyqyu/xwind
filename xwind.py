import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

import requests

# import os

from cs50 import SQL
from flask import redirect, session, request
from functools import wraps
import itertools
from webscraper_navcan import query_navcanada
from webscraper_faa import query_faa



# Configure CS50 Library to use SQLite database
db = SQL('postgres://yslseapkhkqvfs:1296eb1622d1fc4fdc7864b5109102138cb7c3092199afdc7b747e5fd0b36bde@ec2-54-221-214-183.compute-1.amazonaws.com:5432/dau286g9ftm2ei')

# db = SQL("sqlite:///xwind.db")

# Get ident code
def get_ident(station):
    '''# That part is being called when using main app
    if not request.form.get("station"):
        station = request.args.get("station")
    else:
        request.form.get("station")'''

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


def get_code(ident):
    code = db.execute("SELECT id FROM airports WHERE ident=:ident", ident=ident)[0]['id']

    return code


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

def metar_raw(ident_list):
    
    requestor = ""
    for x in range(len(ident_list)):
        try:
            ident_list[x+1]
            requestor += ident_list[x]
            requestor += " "
        except Exception:
            requestor += ident_list[x]
    print(requestor)

    url_response = urllib.request.urlopen(
    "https://www.aviationweather.gov/adds/dataserver_current/httpparam?"
    "datasource=metars"                       # 'metars' or 'tafs'
    "&requestType=retrieve"                 # -- don't touch --
    "&format=xml"                           # -- don't touch --
    "&mostRecent=false"                      # use if only want latest
    "&hoursBeforeNow=3"                    # required even if latest
    f"&stationString={requestor}")              # station ICAO code

    root = ET.fromstring(url_response.read())
    
    print(root.find('data/METAR/raw_text').text)
    print(len(root.findall('data/METAR')))

    for metar in root.findall('data/METAR'):
        print(metar.text)

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
        wx_type.append("TAF FROM")
        for taf in islice(root_taf.findall('data/TAF/forecast'), 1, None):
            try:
                if taf.find('wind_dir_degrees').text:
                    if taf.find('change_indicator').text == "FM":
                        wx_type.append("TAF FROM")
                    elif taf.find('change_indicator').text == "TEMPO":
                        wx_type.append("TAF TEMPO")
                    elif taf.find('change_indicator').text == "PROB":
                        if taf.find('probability').text == "30":
                            wx_type.append("TAF PROB30")
                        elif taf.find('probability').text == "40":
                            wx_type.append("TAF PROB40")
                    elif taf.find('change_indicator').text == "BECMG":
                        wx_type.append("TAF BECMG")
            except Exception:
                continue

    return wx_type


def runways(code):
    runway_list = []
    rwys = db.execute(
        "SELECT le_ident, xhe_ident "
        "FROM runways "
        "WHERE airport_ref=:code AND closed='0' "
        "ORDER BY length_ft DESC", code=code)
    for r in rwys:
        runway_list.append(r)
    return runway_list

def runways_data(code):
    data = []
    rwy_data = db.execute(
        "SELECT length_ft, length_ft, width_ft, width_ft, surface, surface "
        "FROM runways "
        "WHERE airport_ref=:code AND closed='0' "
        "ORDER BY length_ft DESC", code=code)
    for info in rwy_data:
        if info["surface"] == "ASP":
            test = str(info['length_ft']) + "x" + str(info['width_ft']) + " Asphalt"
            data.append(test)
        elif info["surface"] == "CON":
            test = str(info['length_ft']) + "x" + str(info['width_ft']) + " Concrete"
            data.append(test)
        elif info["surface"] == "GVL":
            test = str(info['length_ft']) + "x" + str(info['width_ft']) + " Gravel"
            data.append(test)
        else:
            test = str(info['length_ft']) + "x" + str(info['width_ft']) + " " + info["surface"]
            data.append(test)

    return data

def headings(code):
    headings_list = []
    headings = db.execute(
        'SELECT "le_heading_degT", "xhe_heading_degT" '
        "FROM runways "
        "WHERE airport_ref=:code AND closed='0' "
        "ORDER BY length_ft DESC", code=code)
    for head in headings:
        headings_list.append(head)
    return headings_list


def get_notams(ident_list):
    navcanada_ident_list = []
    faa_ident_list = []
    navcanada_notams_list = []
    faa_notams_list = []
    for ident in ident_list:
        if ident[0] == "C" and len(ident) <= 4 :
            navcanada_ident_list.append(ident)
        else:
            faa_ident_list.append(ident)

    if navcanada_ident_list:
        navcanada_notams_list = query_navcanada(navcanada_ident_list)

    if faa_ident_list:
        faa_list = []
        for elem in faa_ident_list:
            faa_list = query_faa(elem)
            faa_notams_list.extend(faa_list)

    if navcanada_ident_list and faa_ident_list:
        combined_notams = navcanada_notams_list + faa_notams_list
        return combined_notams
    elif navcanada_notams_list:
        return navcanada_notams_list
    else:
        return faa_notams_list



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
