import random
import time
import re
import os
import requests
import string
from ctypes import windll
import subprocess


"""
Globale Url des Management-Portals mit der subdirectory /heartbeat welche REST (POST) Abfragen bearbeitet
"""
URL = "http://localhost:8000/heartbeat/"

"""
dir: Root Ordner von dem aus angefangen wird nach dem /Kundenscripts subordner zu suchen
zaehler: Hilfsvariable für rekursiven Methodenaufruf mit anderem Root Ordner
"""
def searchFiles(dir, zaehler = 0):
    global URL
    abspathLog = ""
    abspathConfig = ""

    #print(dir[zaehler] + ":/")
    #print(zaehler)
    for root, dirs, files in os.walk(dir[zaehler] + ":/"):
        # print(files)
        # print(root)
        if os.path.basename(root) != 'Kundenscripts':
            continue

        abspathLog = str(files[files.index('LOG.txt')])
        abspathConfig = str(files[files.index('config.txt')])
        path = open("./path.txt", "w")
        path.write(os.path.abspath(root))
        path.close()
        break

    if not abspathLog and not abspathConfig:
        zaehler += 1
        if zaehler == len(dir):
            return
        searchFiles(dir, zaehler)

    PARAMS = readData(str(os.path.abspath(root)), abspathLog, abspathConfig)
    print(PARAMS)
    requests.post(url=URL, data=PARAMS)

"""
Liest die Daten aus config.txt und LOG.txt aus und speichert sie im PARAMS dict

@return dictionary
"""
def readData(dir: str, abspathLog: str, abspathConfig: str):
    if not dir or not abspathLog or not abspathConfig:
        return None

    abspathLog = dir + "\\" + abspathLog
    abspathConfig = dir + "\\" + abspathConfig
    print(abspathLog + "      " + abspathConfig)

    log = open(abspathLog, "r")
    meldung = str(log.read())
    log.close()

    pattern = "[0-2]{1}[0-9]{1}[:][0-5]{1}[0-9]{1}\s[0-3]{1}[0-9]{1}[.][0-1]{1}[0-9]{1}[.][2]{1}[0-1]{1}[0-9]{2}"
    try:
        meldung = re.findall(pattern + "\s[\[\]a-zA-Z0-9_ ]*", meldung)[-1]
    except:
        meldung = ''

    config = open(abspathConfig, "r")
    lizenz = config.read()
    config.close()

    PARAMS = {
        "key": lizenz,
        "log": meldung
    }

    return PARAMS

"""
Sendet den Request an die Heartbeat API
"""
def directRequest(dir: str):
    PARAMS = readData(dir, "LOG.txt", "config.txt")
    requests.post(url= URL, data= PARAMS)
"""
Findet alle existierenden Laufwerke und speichert diese in drives[]
"""
def get_drives():
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drives.append(letter)
        bitmask >>= 1

    return drives

"""
Führt den Heartbeat Request aus und prüft vorher ob path.txt einen Inhalt besitzt (den absoluten Pfad), 
um darauf basierend zwei verschiedene Wege zu gehen (searchFiles oder directRequest)
"""
def execute():
    drives = get_drives()
    print(drives)
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

#Periodisch mit Zufall alle 24h versetzt
zufall=int(random.uniform(1, 100))
zeit= 1439+zufall
time.sleep(zeit)
execute()

"""
Führt beim ersten .exe start die .bat File aus mit dem festlegten Timer 
die in der .bat File fest geschrieben und ausgelöst wird 
"""
firstTime = open("initial.txt", "r").read()
firstTime = firstTime.replace("\n", "")

if firstTime.lower() == "false":
    subprocess.call([r'.\autostart.bat'])
    open("initial.txt", "w").write("True")


"""
Automatiserter Heartbeat push mit der While schleife, zur test Zwecken 
"""
#schedule.every(1).seconds.do(execute)

#while True:
#    schedule.run_pending()
#    time.sleep(1)
