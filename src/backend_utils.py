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


def load_detector_data():
    curdir = os.path.dirname(__file__)
    df_path = curdir.replace("src", "data/detectors.csv")
    df = pd.read_csv(df_path)
    return df


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
    d = json.loads(msg.payload.decode())
    val = d["Value"]
    now_time = d['CreateUtc']

    # gets the detector id associated with this message
    det_id = extract_detector_id(msg.topic)
    # gets the reading of this message
    subj = extractor_detection_type(msg.topic)

    # uses the detector id from this message to pull up dict of previous readings associated with this detector.
    detector_values = userdata[0][det_id]
    prev_time = detector_values['CreateUtc']

    # if the timestamp associated with this new reading is different than the previous timestamp, and if this reading
    # is not the very first reading ever recorded, aggregate the multiple readings already existing into a new reading,
    # write it to redis,and reset
    if now_time != prev_time and prev_time != 'init-time':
        a_data = parse_aggregated_values(now_time, detector_values, det_id)
        write_db(a_data, userdata[1])
        print(a_data)
    else:  # collect readings of the same time published at the same timestamp
        if subj in detector_values:
            detector_values[subj].append(val)
            detector_values['CreateUtc'] = now_time


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


def initialize_incoming_data(active_ids, value_types):
    """
    :param active_ids (list): unique ids of the detectors associated with a mqtt message
    :param value_types (list): reading_types of the detectors associated with a mqtt message
    :return incoming_data (dict):
    """
    incoming_data = {}
    for each_id in active_ids:
        incoming_data[each_id] = {}
        for each_type in value_types:
            incoming_data[each_id][each_type] = []
        incoming_data[each_id]["CreateUtc"] = "init-time"
    return incoming_data


def write_db(new_data, db):
    """
    writes the aggregated data for each det_id to redis
    :param new_data:
    :param db:
    :return:
    """
    det_id = new_data['id']
    existing_data = json.loads(db.get(det_id))
    for key in existing_data:
        # keep up to 24 hrs worth of data, with 1 datapoint per minute.
        # probably a better data structure than poping a list at idx 0.
        # but small enough to not impact performance. maybe future improve
        datalen=len(existing_data[key])
        if datalen > 1600:
            existing_data[key]=existing_data[key][datalen-1:datalen-1-1440]
        existing_data[key].append(new_data[key])
    db.set(det_id, json.dumps(existing_data))


def extract_detector_id(topic):
    raw_id = topic.split("/")[10]
    det_id = raw_id.split("-")[1]
    return det_id


def extractor_detection_type(topic):
    t = topic.split("/")[-1]
    return t


def parse_aggregated_values(now_time, detector_values, det_id):
    """
    aggregate multiple vehicle-speed, vehicle-count, and vehicle-gap-time readings according to:
    avg(vehicle-speed), avg(vehicle-gap-time), sum(vehicle-count)
    :param now_time (list): int
    :param detector_values (list): int
    :param det_id: str
    :return:
    """
    detector_values['CreateUtc'] = now_time
    aggregate = {}

    gptime = [i for i in detector_values['vehicle-gap-time'] if i > 0]
    vspeed = [i for i in detector_values['vehicle-speed'] if i > 0]

    if len(gptime) > 0:
        aggregate['vehicle-gap-time'] = int(sum(gptime) / len(gptime) * 0.1)
        # raw values emitted as 1/10s, convert & round to s
    else:
        aggregate['vehicle-gap-time'] = 0

    if len(vspeed) > 0:
        aggregate['vehicle-speed'] = int(sum(vspeed) / len(vspeed))
        # round to nearest kmh
    else:
        aggregate['vehicle-speed'] = 0

    aggregate['vehicle-count'] = sum(detector_values['vehicle-count'])
    aggregate['time'] = now_time
    aggregate['id'] = det_id

    # reset the list of each reading_type associated with this det_id
    for each_key in detector_values:
        if each_key != 'CreateUtc':
            detector_values[each_key] = []

    return aggregate


def read_csv(fname):
    curdir = os.path.dirname(__file__)
    basedir = os.path.abspath(os.path.join(curdir, os.pardir))
    datadir = os.path.join(basedir, "data")
    df = pd.read_csv(datadir + "/{}".format(fname), dtype={'id': str})
    return df


def extract_topics(df):
    topic_groups = [i.split(",") for i in df['topics'].values]
    topic_wildcards = []
    for each_group in topic_groups:
        subgroup = []
        for t in each_group:
            subgroup.append(t + "#")
        topic_wildcards.append(subgroup)

    topics = []
    for t_group in topic_wildcards:
        for t in t_group:
            topics.append((t, 0))

    return topics
