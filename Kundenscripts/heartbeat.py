import random
import time
import re
import os
import requests
import string
from ctypes import windll
import subprocess

"""
Global url of the management portal with the subdirectory '/heartbeat' which handles REST (POST) requests
"""
URL = "http://localhost:8000/heartbeat/"

def search_files(dir: list, counter: int = 0):
    """
    Searches files in 'Kundenscripts' directory.

    Parameters:
    dir     (list): list of drives to search for the sub-directory '/Kundenscripts'
    counter (int) : helper variable for recursive function call with another root directory
    """
    global URL
    abspath_log    = ""
    abspath_config = ""

    for root, dirs, files in os.walk(dir[counter] + ":/"):
        if os.path.basename(root) != 'Kundenscripts':
            continue

        abspath_log    = str(files[files.index('LOG.txt')])
        abspath_config = str(files[files.index('config.txt')])
        path           = open("./path.txt", "w")
        path.write(os.path.abspath(root))
        path.close()
        break

    if not abspath_log and not abspath_config:
        counter += 1
        if counter == len(dir):
            return
        search_files(dir, counter)

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
        "log": message,
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

def get_drives():
    """
    Finds all existing drives and returns them.

    Returns:
    list: drives
    """
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drives.append(letter)
        bitmask >>= 1

    return drives

def execute():
    """
    Executes the heartbeat request and checks before if a path exists in 'path.txt' already.
    If it exists it sends directly the requests, if not it searchs for it before.
    """
    drives = get_drives()

    try:
        path        = open("./path.txt", "r")
        abspathPath = path.read()
        path.close()
    except FileNotFoundError:
        abspathPath = ""

    if not abspathPath:
        search_files(drives)
    else:
        direct_request(abspathPath)

# Periodically with coincidence all 24 hours
random_var  = int(random.uniform(1, 100))
duration    = 1439 + random_var
time.sleep(duration)
execute()

# Executes during the first start .bat file to trigger timer.
firstTime = open("initial.txt", "r").read()
firstTime = firstTime.replace("\n", "")

if firstTime.lower() == "false":
    subprocess.call([r'.\autostart.bat'])
    open("initial.txt", "w").write("True")
