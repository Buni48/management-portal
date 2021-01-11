import requests
import schedule
import time


def convert_list_to_string(org_list, seperator=' '):
    """ Convert list to string, by joining all item in list with given separator.
        Returns the concatenated string """
    return seperator.join(org_list)


# Open function to open the file "Config.txt" and "Error Log"
# (same directory) in read mode and
config = open("config.txt","r")
inhalt = config.readlines()
logDatei= open("LOG.txt","r")
errorLog= logDatei.readlines()
full_str = convert_list_to_string(inhalt)

#Initialisierung der Lizenz und Beatdaten

URL="http://localhost:8000/heartbeat"
lizenz= full_str[0:6]
beatData={'meldung':lizenz, 'log': errorLog}

print(inhalt)
print('##################################\nLizenz:')
print(lizenz)
print(errorLog)


#Requrest mit Beatdaten wird an URL gesendet
def job():
    requests.post(url=URL, data=beatData)
    print('request war erfolgreich!')


#Periodisch
schedule.every(2).seconds.do(job)
#schedule.every(150).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
