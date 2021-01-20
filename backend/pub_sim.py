import random
import time
from paho.mqtt import client as mqtt_client
import backend_utils
import datetime
import pytz
import numpy as np
import json

def generate_msg(desc, unit, value):
    created_at = datetime.datetime.now(tz=pytz.timezone("Etc/UTC"))
    expires_at = created_at + datetime.timedelta(minutes=1)

    created_at = created_at.strftime("%Y-%m-%dT%H:%M:%S")
    expires_at = expires_at.strftime("%Y-%m-%dT%H:%M:%S")

    msg = {"CreateUtc":created_at,
           "Desc":desc,
           "ExpiryUtc":expires_at,
           "Format":"ODNF1",
           "Status":"Good",
           "Unit":unit,
           "Value":value}

    return msg


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connected to MQTT broker")
    else:
        print("failed to connect with code {}".format(rc))


def publish(client, topics):
    while True:
        for t in topics:
            if "speed" in t:
                val = np.random.randint(10, 100)
                msg = generate_msg("Average-vehicle-speed-for-vehicles", "Km/h", val)
            elif "count" in t:
                val = np.random.randint(1, 30)
                msg = generate_msg("Number-of-vehicles-during-the-integration-interval", "", val)
            else:
                val = np.random.randint(50, 300)
                msg = generate_msg("Vehicle-average-gap-time", "1/10sec", val)

            print(msg)
            msg=json.dumps(msg)
            client.publish(t, msg)

        time.sleep(10)


def main():
    # ================== setting up the topics =====================
    df = backend_utils.read_csv("detectors-ids-unpacked.csv")
    ids = df['topic'].values.tolist()
    value_types = ["vehicle-gap-time", "vehicle-count", "vehicle-speed"]
    topics = []
    for each_id in ids:
        for each_type in value_types:
            topics.append(each_id + each_type)

    # ================== mqtt =====================================
    broker = 'broker.hivemq.com'
    port = 1883
    client_id = 'python-mqtt-{}'.format(random.randint(0, 1000))

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    client.loop_start()
    publish(client, topics)


if __name__ == "__main__":
    main()
