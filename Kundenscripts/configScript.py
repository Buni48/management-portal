import schedule
import time
import re
import os
import requests

"""
Dieser configScript dient zur Testzwecken, bei der Überprüfung ob Heartbeats erfolgreich empfangen wurden
"""

"""
Global url of the management portal with the subdirectory '/heartbeat' which handles REST (POST) requests
"""
URL = "http://localhost:8000/heartbeat/"

def searchFiles(dir: str, counter: int = 0):
    """
    Searches files in 'Kundenscripts' directory.

    Parameters:
    dir     (str): root folder where the search for the sub-directory '/Kundenscripts' starts
    counter (int): helper variable for recursive function call with another root directory
    """
    global URL
    abspathLog    = ""
    abspathConfig = ""

    if counter == 2:
        return

    for root, dirs, files in os.walk(dir):
        print(root)
        if os.path.basename(root) != 'Kundenscripts':
            continue

        abspathLog    = str(files[files.index('LOG.txt')])
        abspathConfig = str(files[files.index('config.txt')])
        path          = open("./path.txt", "w")
        path.write(os.path.abspath(root))
        path.close()
        break

    if not abspathLog and not abspathConfig:
        searchFiles("D:/", counter + 1)

    PARAMS = readData(str(os.path.abspath(root)), abspathLog, abspathConfig)
    print(PARAMS)

    requests.post(url=URL, data=PARAMS)

def readData(dir: str, abspathLog: str, abspathConfig: str):
    """
    Liest die Daten aus config.txt und LOG.txt aus und speichert sie im PARAMS dict
    Reads data of 'config.txt' and 'LOG.txt' and returns it.

    Parameters:
    dir           (str): directory to get data from
    abspathLog    (str): log
    abspathConfig (str): config

    Returns:
    dict: data
    """
    if not dir or not abspathLog or not abspathConfig:
        return None

    abspathLog    = dir + "\\" + abspathLog
    abspathConfig = dir + "\\" + abspathConfig
    print(abspathLog + "      " + abspathConfig)

    log     = open(abspathLog, "r")
    message = str(log.read())
    log.close()

    pattern = "[0-2]{1}[0-9]{1}[:][0-5]{1}[0-9]{1}\s[0-3]{1}[0-9]{1}[.][0-1]{1}[0-9]{1}[.][2]{1}[0-1]{1}[0-9]{2}"
    try:
        message = re.findall(pattern + "\s[\[\]a-zA-Z0-9_ ]*", message)[-1]
    except:
        message = ''

    config = open(abspathConfig, "r")
    license = config.read()
    config.close()

    PARAMS = {
        "key": license,
        "log": message
    }

    return PARAMS

def directRequest(dir: str):
    """
    Sends a request to the heartbeat API.

    Parameters:
    dir (str): directory to get data from
    """
    PARAMS = readData(dir, "LOG.txt", "config.txt")
    requests.post(url= URL, data= PARAMS)

def execute():
    """
    Executes the heartbeat request and checks before if a path exists in 'path.txt' already.
    If it exists it sends directly the requests, if not it searchs for it before.
    """
    try:
        path        = open("./path.txt", "r")
        abspathPath = path.read()
        path.close()
    except FileNotFoundError:
        abspathPath = ""

    if not abspathPath:
        searchFiles("C:/")
    else:
        directRequest(abspathPath)

# Loop to send requests after a specific time.
schedule.every(1).seconds.do(execute)
while True:
    schedule.run_pending()
    time.sleep(1)
