"""
this is a collection of utility methods to aid in extracting data from incoming mqtt messages and write them to a
locally running redis server. see ../backend/mqtt_collect.py's description for more details on the overall ideas
involved

"""
import pandas as pd
import random
from paho.mqtt import client as mqtt_client
import os
import json
import numpy as np
from scipy.interpolate import interp1d


def connect_mqtt(broker, port) -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to Broker")
            # a=1
        else:
            print("Failed to Connect, error code {}".format(rc))

    client_id = "id-{}".format(random.randint(0, 1000))
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def on_message(client, userdata, msg):
    """
    the callback function that's triggered everytime the client receivees a new mqtt message. see the desc in
    mqtt_collect.py for the main idea behind aggregating multiple readings of the same time for a given detector.

    :param client:
    :param userdata (list): custom data passed by user for performing necessary tasks. In this case, userdata is
    [dict, Redis] where the dict is of the form {det_id1:{reading_type1:[],reading_type2:[]...},det_id2:{}...} and
    Redis is a Redis instance from redis tha's connected to a server on the local machine
    :param msg:
    :return:
    """
    det_id = extract_detector_id(msg.topic)

    value_dict = json.loads(msg.payload.decode())
    reading = value_dict["Value"]
    time = value_dict['CreateUtc']
    subj = extractor_detection_type(msg.topic)

    maxsize = 300
    minsize = 240

    existing_data = json.loads(userdata.get(det_id))
    existing_sizes = [len(existing_data[k]) for k in existing_data]
    if min(existing_sizes) == maxsize:
        for k in existing_data:
            existing_data[k] = existing_data[k][(len(existing_data[k]) - minsize + 1):]

    existing_data[subj].append(reading)
    if time not in existing_data['time']:
        existing_data['time'].append(time)

    print("{:<6}  {:<4}  {:<20}  {:<16}".format(det_id, reading, time, subj))

    userdata.set(det_id, json.dumps(existing_data))


def initialize_db(db, active_ids, data_template):
    """
    checks whether data entries for a specific detecotr already exists. if so, not, initiate an empty dictionary-type
    value with the detector's id as key in the database. see the data_template variable in mqtt_collect.py for desc
    of the dictionary structure

    :param db: a Redis() object from redis module
    :param active_ids (list): list of detector ids
    :param data_template (dict): a dict with the types of readings to collect as keys and empty lists as values
    :return:
    """
    for each_id in active_ids:
        if db.exists(each_id) == 0:
            db.set(each_id, json.dumps(data_template))


def extract_detector_id(topic):
    raw_id = topic.split("/")[10]
    det_id = raw_id.split("-")[1]
    return det_id


def extractor_detection_type(topic):
    t = topic.split("/")[-1]
    return t


def read_csv(fname):
    curdir = os.path.dirname(__file__)
    basedir = os.path.abspath(os.path.join(curdir, os.pardir))
    datadir = os.path.join(basedir, "data")
    df = pd.read_csv(datadir + "/{}".format(fname), dtype={'id': str})
    return df


class TwoPeaks:
    def __init__(self):
        self.minval = None
        self.maxval = None
        self.wl = np.pi / 15
        self.noise = None
        self.amplitude=None

    def set_params(self, minval, maxval):
        self.minval = minval
        self.maxval = maxval
        self.amplitude = (self.maxval - self.minval) / 2

    def generate(self, x):
        self.noise = np.random.randint(0, 0.25 * self.maxval, dtype=np.int16)
        val = self.amplitude * np.sin(self.wl * (x - self.minval)) + self.amplitude + self.minval
        val += self.noise
        return int(val)


class OneTrough (TwoPeaks):
    def __init__(self):
        super().__init__()

    def generate(self, x):
        self.noise = np.random.randint(0, 0.25 * self.maxval, dtype=np.int16)
        val = self.amplitude * np.sin(0.5 * self.wl * (x + 2 * self.minval)) + self.amplitude + self.minval
        val += self.noise
        return int(val)
