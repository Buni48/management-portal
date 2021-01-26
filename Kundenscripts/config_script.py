import schedule
import time
import re
import os
import requests

"""
This config script is there to test if heartbeats have been received successfully
"""

"""
Global url of the management portal with the subdirectory '/heartbeat' which handles REST (POST) requests
"""
URL = "http://localhost:8000/heartbeat/"

def search_files(dir: str, counter: int = 0):
    """
    Searches files in 'Kundenscripts' directory.

    Parameters:
    dir     (str): root folder where the search for the sub-directory '/Kundenscripts' starts
    counter (int): helper variable for recursive function call with another root directory
    """
    global URL
    abspath_log    = ""
    abspath_config = ""

    if counter == 2:
        return

    for root, dirs, files in os.walk(dir):
        if os.path.basename(root) != 'Kundenscripts':
            continue

        abspath_log    = str(files[files.index('LOG.txt')])
        abspath_config = str(files[files.index('config.txt')])
        path           = open("./path.txt", "w")
        path.write(os.path.abspath(root))
        path.close()
        break

    if not abspath_log and not abspath_config:
        search_files("D:/", counter + 1)

    PARAMS = read_data(str(os.path.abspath(root)), abspath_log, abspath_config)

    requests.post(url=URL, data=PARAMS)

def read_data(dir: str, abspath_log: str, abspath_config: str):
    """
    Reads data of 'config.txt' and 'LOG.txt' and returns it.

    Parameters:
    dir            (str): directory to get data from
    abspath_log    (str): log file
    abspath_config (str): config file with license key within

    Returns:
    dict: data
    """
    if not dir or not abspath_log or not abspath_config:
        return None

    abspath_log    = dir + "\\" + abspath_log
    abspath_config = dir + "\\" + abspath_config

    log     = open(abspath_log, "r")
    message = str(log.read())
    log.close()

    pattern = "[0-2]{1}[0-9]{1}[:][0-5]{1}[0-9]{1}\s[0-3]{1}[0-9]{1}[.][0-1]{1}[0-9]{1}[.][2]{1}[0-1]{1}[0-9]{2}"
    try:
        message = re.findall(pattern + "\s[\[\]a-zA-Z0-9_ ]*", message)[-1]
    except:
        message = ''

    config  = open(abspath_config, "r")
    license = config.read()
    config.close()

    PARAMS = {
        "key": license,
        "log": message
    }

    return PARAMS

def direct_request(dir: str):
    """
    Sends a request to the heartbeat API.

    Parameters:
    dir (str): directory to get data from
    """
    PARAMS = read_data(dir, "LOG.txt", "config.txt")
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
        search_files("C:/")
    else:
        direct_request(abspathPath)

# Loop to send requests after a specific time.
schedule.every(1).seconds.do(execute)
while True:
    schedule.run_pending()
    time.sleep(1)
