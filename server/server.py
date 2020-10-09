import ipinfo
from multiprocessing import Process, Value, Lock
import os
import time
from datetime import datetime
from flask import Flask
from pathlib import Path
from tinydb import TinyDB, Query

IPINFO_ACCESS_TOKEN = '286e47d878963a'
DATA_DIR = '/data'

global sensorData
global location
location = {}

def getLocationDetails():
    handler = ipinfo.getHandler(IPINFO_ACCESS_TOKEN)
    details = handler.getDetails()
    
    location_info = {
        "ip": details.ip,
        "city": details.city,
        "region": details.region,
        "country": details.country,
        "loc": details.loc,
        "postal": details.postal
    }

    return location_info


def getDailyDB(year, month, day):
    # Create the directory if needed
    dirPath = os.path.dirname(os.path.realpath(__file__)) + DATA_DIR + '/' + str(year) + '/' + str(month).zfill(2)
    Path(dirPath).mkdir(parents =True, exist_ok=True)

    # Load / Create the DB
    db = TinyDB(dirPath + '/' + str(year) + '_' + str(month).zfill(2) + '_' + str(day).zfill(2) + '.json')
    return db

class SensorData(object):
    def __init__(self):
        self.location = getLocationDetails()
        self.lock = Lock()

LOCATION_DATA = {}
CURRENT_DATA = {}

app = Flask(__name__)
@app.route('/')
def example():
    return str(CURRENT_DATA)

@app.route('/location')
def lookupLocation():
    return str(location)

def runServer():
    app.run()

def runSensor():
    location = getLocationDetails()

    now = datetime.now()
    db = getDailyDB(now.year, now.month, now.day)
    
    db.insert({'location' : LOCATION_DATA})

    while True:
        print('Updating Sensor...')
        time.sleep(3)


if __name__ == '__main__':
    #LOCATION_DATA = multiprocessing.Manager().dict()
    #CURRENT_DATA = multiprocessing.Manager().dict()

    serverProcess = Process(name='server', target=runServer)
    serverProcess.start()

    time.sleep(1)

    sensorProcess = Process(name='sensor', target=runSensor)
    sensorProcess.start()