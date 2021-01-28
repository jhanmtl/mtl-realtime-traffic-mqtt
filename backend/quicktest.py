
import backend_utils
import redis
import json
import pprint

def on_message(client, userdata, msg):

    d = json.loads(msg.payload.decode())
    pprint.pprint(d)



broker = 'mqtt.cgmu.io'
port = 1883
value_types = ["vehicle-gap-time", "vehicle-count", "vehicle-speed", "CreateUtc"]
data_template = {'vehicle-gap-time': [], 'vehicle-speed': [], 'vehicle-count': [], 'time': []}


def main():

    client = backend_utils.connect_mqtt(broker, port)

    topic="worldcongress2017/pilot_resologi/odtf1/ca/qc/mtl/mobil/traf/detector/det1/det-00773-01/zone1/class5/vehicle-speed"

    client.subscribe(topic)

    client.on_message = on_message
    client.loop_forever()

if __name__ == "__main__":
    main()
