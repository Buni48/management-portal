import os
import requests
import string
from ctypes import windll
import json

"""
Global url of the management portal which handles REST (POST) requests
"""
URL = "http://localhost:8000/licenses/license-heartbeat"

def search_files(dir: list, counter: int = 0):
    """
    Searches files in 'Kundenscripts' directory.

    Parameters:
    dir     (list): list of drives to search for the sub-directory '/Kundenscripts'
    counter (int) : helper variable for recursive function call with another root directory
    """
    global URL
    abspath_config = ""

    if counter == 2:
        return
    for root, dirs, files in os.walk(dir[counter] + ":/"):
        if os.path.basename(root) != 'Kundenscripts':
            continue

        abspath_config = str(files[files.index('config.txt')])
        path           = open("./path.txt", "w")
        path.write(os.path.abspath(root))
        path.close()
        break

    if not abspath_config:
        search_files("D:/", counter + 1)

    PARAMS = read_data(str(os.path.abspath(root)), abspath_config)
    requests.post(url=URL, data=PARAMS)

def read_data(dir: str, abspath_config: str) -> dict:
    """
    Reads data of 'config.txt' and returns it.

    Parameters:
    dir            (str): directory to get data from
    abspath_config (str): config file with license key within

    Returns:
    dict: data
    """
    if not dir or not abspath_config:
        return {}

    abspath_config = dir + "\\" + abspath_config
    config         = open(abspath_config, "r")
    license        = config.read()
    config.close()

    PARAMS = {
        "key": license
    }

    return PARAMS

def direct_request(dir: str):
    """
    Sends a request to the license heartbeat API.

    Parameters:
    dir (str): directory to get data from
    """
    PARAMS   = read_data(dir, "config.txt")
    response = requests.post(url= URL, data= PARAMS)
    save     = overwrite(response.json())
    requests.post(url="http://localhost:8000/licenses/license-heartbeat/save", data=save)

def get_drives() -> list:
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
        path = open("./path.txt", "r")
        abspathPath = path.read()
        path.close()
    except FileNotFoundError:
        abspathPath = ""

    if not abspathPath:
        search_files(drives)
    else:
        direct_request(abspathPath)

def overwrite(license: dict) -> dict:
    """
    Opens the config file and replaces the license key in it.

    Parameters:
    license (dict): license key and if new exists

    Returns:
    dict: old key, new key and if overwrite
    """
    overwrite = False
    old       = ""
    new       = ""

    if license["exist"] == True:
        try:
            config = open("./config.txt", "r")
            old    = config.read()
            config.close()

            config = open("./config.txt", "w")
            config.write(license['key'])
            config.close()

            new       = license['key']
            overwrite = True
        except:
            pass

    data = {
        "old"       : old,
        "new"       : new,
        "new_exists": overwrite
    }

    return data

execute()
