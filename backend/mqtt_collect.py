""" MQTT Data Collector

This script connects to the mqtt broker on which the thermal and radar detectors from Monrteal's Realtime Traffic
program (https://donnees.montreal.ca/ville-de-montreal/circulation-mobilite-temps-reel)
broadcasts data.

Data type collected are vehicle speed, vehicle count, and vehicle gaptime. To run, make sure a redis server is already
running locally on the machine and then start script from terminal with 'python mqtt_collect.py'

The main difficulty encountered and solved here is that a single detector records readings from multiple lanes.
For example, det_1 may have 3 vehicle-speed readings on a three-lane road. For the purpose of this project, I
wanted to aggregate those multiple readings of a same type into a single reading with the following scheme:
vehicle-speed by avg speed across all lanes, vehicle-count by sum of all lanes, and gaptime by average across all lanes.

Ao achieve this, the on_message callback function,associated with the mqtt client upon reception of a new message,
operates on a dictionary called incoming_data of the form {det_id1:{},det_id2:{},det_id3:{},...} where the nested dict
associated with each det_id key is of the form {vehicle-speed:[],vehicle-count:[],vehicle-gap-time,CreatedUtc:[]}

det_id, reading_type, reading_value and timestamp is extracted from each new message. The timestamp is appended to the
CreatedUtc list of the det_id's nested dictionary. If the newly appended timestamp is the same as existing timestamps
in that list, then the new reading_value is also appended to the appropriate list in the det_id's nested dictionary.
Upon reception of a message with a different timestamp than what's already in the det_id's CreateUtc list, then it is
time to aggregate all the readings in the other lists according to the rules defined, write the aggregated value to
the redis database under the appropriate det_id and value type, empty the list in the nested dict associated with
the det_id/readinding_type, and reset the CreatedUtc list to a single element that's the new timestamp.

Corresponding methods for performing the above tasks are identified below and also in ../src/backend_utils.py

"""
import backend_utils
import redis

broker = 'mqtt.cgmu.io'
port = 1883
value_types = ["vehicle-gap-time", "vehicle-count", "vehicle-speed", "CreateUtc"]
data_template = {'vehicle-gap-time': [], 'vehicle-speed': [], 'vehicle-count': [], 'time': []}


def main():
    df = backend_utils.read_csv('detectors-active.csv')
    active_ids = df['id'].values.tolist()
    active_topics = backend_utils.extract_topics(df)

    db = redis.Redis(host='localhost', port=6379, db=0)
    backend_utils.initialize_db(db, active_ids, data_template)

    # constructs the nested dict structure that's operated on by the on_message callback for aggregating
    # mutliple readings of the same type for a given det_id
    incoming_data = backend_utils.initialize_incoming_data(active_ids, value_types)

    client = backend_utils.connect_mqtt(broker, port)

    # passes in the incoming_data to the client so it can be operated on during the on_message callback
    client.user_data_set([incoming_data, db])

    client.subscribe(active_topics)

    client.on_message = backend_utils.on_message
    client.loop_forever()

if __name__ == "__main__":
    main()
