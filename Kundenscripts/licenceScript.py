import os
import requests
import string
from ctypes import windll
import json

"""
Globale Url des Management-Portals mit der subdirectory /heartbeat welche REST (POST) Abfragen bearbeitet
"""
URL = "http://localhost:8000/licenses/"

"""
dir: Root Ordner von dem aus angefangen wird nach dem /Kundenscripts subordner zu suchen
zaehler: Hilfsvariable für rekursiven Methodenaufruf mit anderem Root Ordner
"""

def searchFiles(dir: list, zaehler = 0):
    global URL
    abspathConfig = ""

    if zaehler == 2:
        return
    print(dir)
    for root, dirs, files in os.walk(dir[zaehler] + ":/"):
        if os.path.basename(root) != 'Kundenscripts':
            continue

        abspathConfig = str(files[files.index('config.txt')])
        path = open("./path.txt", "w")
        path.write(os.path.abspath(root))
        path.close()
        break

    if not abspathConfig:
        searchFiles("D:/", zaehler + 1)

    PARAMS = readData(str(os.path.abspath(root)), abspathConfig)
    print(PARAMS)


    x = requests.post(url=URL, data=PARAMS)
    print("SEARCH")
    print(json.loads(x.json())["lizenz"])



def readData(dir: str, abspathConfig: str) -> dict:
    """ Liest den Lizenzschlüssel aus config.txt und speichert sie im PARAMS dict

    Parameter
    ---------
    dir : str
        der absolute Pfad zu dem Root Ordner, in welchem sich der Lizenzschlüssel befindet
    abspathConfig : str
        die config (.txt) Datei mit dem Lizenzschlüssel

    Return
    ------
    PARAMS : dict
        dictionary mit den Key-Value-Paaren lizenzschluessel und meldung mit den dazugehörigen Werten
    """

    if not dir or not abspathConfig:
        return {}


    abspathConfig = dir + "\\" + abspathConfig

    config = open(abspathConfig, "r")
    lizenz = config.read()
    config.close()

    PARAMS = {
        "lizenzschluessel": lizenz
    }

    return PARAMS



def directRequest(dir: str):
    """ Sendet den Request an die Lizenz API

    Parameter
    ---------
    dir : str
        der absolute Pfad zu dem Root Ordner, in welchem sich der Lizenzschlüssel befindet
    """

    PARAMS = readData(dir, "config.txt")
    x = requests.post(url= URL, data= PARAMS)
    save = overwrite(json.loads(x.json()))

    requests.post(url="http://localhost:8000/lizenzheartbeat/lizenzsave", data=save)



def get_drives() -> list:
    """ Findet alle existierenden Laufwerke und speichert diese in drives[]

    Returns
    -------
    drives : list[str]
        Liste aller existierenden Laufwerke des Clients
    """

    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drives.append(letter)
        bitmask >>= 1

    return drives



def execute():
    """ Führt den Heartbeat Request aus und prüft vorher ob path.txt einen Inhalt besitzt (den absoluten Pfad),
        um darauf basierend zwei verschiedene Wege zu gehen (searchFiles oder directRequest)
    """
    drives = get_drives()
    try:
        path = open("./path.txt", "r")
        abspathPath = path.read()
        path.close()
    except FileNotFoundError:
        abspathPath = ""

    if not abspathPath:
        searchFiles(drives)
    else:
        directRequest(abspathPath)



"""
Öffnet die Config-Datei, leer diese und fügt neue Lizenzschlüssel hinein
"""
def overwrite(lizenz):
    overwrite = False
    old = ""
    new = ""

    if lizenz["exist"] == True:
        try:
            config = open("./config.txt", "r")
            old = config.read()
            config.close()

            config = open("./config.txt", "w")
            config.write(lizenz)
            config.close()

            new = lizenz
            overwrite = True
        except:
            pass

    data = {
        "old": old,
        "new": new,
        "bool": overwrite
    }


    return data




execute()


