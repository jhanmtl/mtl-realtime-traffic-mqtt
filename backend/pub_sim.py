import random
import time
from paho.mqtt import client as mqtt_client
import backend_utils
import datetime
import pytz
import argparse
import json
import pandas as pd
import numpy as np

df = pd.read_csv("../data/bimodal_dist.csv")

speed_sim = backend_utils.BimodalSim(df, inverse=True)
gaptime_sim = backend_utils.BimodalSim(df, inverse=True)
count_sim = backend_utils.BimodalSim(df)

def randomize():
    global speed_sim
    global count_sim
    global gaptime_sim

    speed_min = np.random.randint(20, 50)
    speed_max = np.random.randint(speed_min, 100)
    speed_noise = np.random.uniform(0.25, 1.0)
    speed_sim.set_params(speed_min, speed_max, speed_noise)

    count_min = np.random.randint(10, 30)
    count_max = np.random.randint(count_min, 60)
    count_noise = np.random.uniform(0.25, 1.0)
    count_sim.set_params(count_min, count_max, count_noise)

    gaptime_min = np.random.randint(15, 30)
    gaptime_max = np.random.randint(gaptime_min, 180)
    gaptime_noise = np.random.uniform(0.25, 1.0)
    gaptime_sim.set_params(gaptime_min, gaptime_max, gaptime_noise)


def generate_msg(desc, unit, sim):
    created_at = datetime.datetime.now(tz=pytz.timezone("America/New_York"))
    expires_at = created_at + datetime.timedelta(minutes=1)

    sim_input = int(created_at.strftime("%H"))
    value = sim.generate(sim_input)

    created_at = created_at.strftime("%Y-%m-%dT%H:%M:%S")
    expires_at = expires_at.strftime("%Y-%m-%dT%H:%M:%S")

    msg = {"CreateUtc": created_at,
           "Desc": desc,
           "ExpiryUtc": expires_at,
           "Format": "ODNF1",
           "Status": "Good",
           "Unit": unit,
           "Value": value}

    return msg


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connected to MQTT broker")
    else:
        print("failed to connect with code {}".format(rc))


def publish(client, topics, pause):
    global speed_sim
    global count_sim
    global gaptime_sim

    while True:

        for t in topics:
            randomize()

            if "speed" in t:
                msg = generate_msg("Average-vehicle-speed-for-vehicles", "Km/h", speed_sim)
            elif "count" in t:
                msg = generate_msg("Number-of-vehicles-during-the-integration-interval", "", count_sim)
            else:
                msg = generate_msg("Vehicle-average-gap-time", "1/10sec", gaptime_sim)

            print(msg)
            print(t)
            msg = json.dumps(msg)
            client.publish(t, msg)

        time.sleep(pause)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t")
    args = parser.parse_args()
    pause = int(args.t)

    # ================== setting up the topics =====================
    df = backend_utils.read_csv("detectors-simulated.csv")
    ids = df['topics'].values.tolist()
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
    publish(client, topics, pause)


if __name__ == "__main__":
    main()
