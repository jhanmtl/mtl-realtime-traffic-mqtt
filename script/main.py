import util
import redis
import json

broker = 'mqtt.cgmu.io'
port = 1883
value_types = ["vehicle-gap-time", "vehicle-count", "vehicle-speed", "CreateUtc"]
data_template = {'vehicle-gap-time': [], 'vehicle-speed': [], 'vehicle-count': [], 'time': []}


def main():
    df = util.read_csv('detectors-active.csv')
    active_ids = df['id'].values.tolist()
    active_topics = util.extract_topics(df)

    db = redis.Redis(host='localhost', port=6379, db=0)
    util.initialize_db(db, active_ids, data_template)
    incoming_data = util.initialize_incoming_data(active_ids, value_types)

    client = util.connect_mqtt(broker, port)
    client.user_data_set([incoming_data, db])
    client.subscribe(active_topics)

    client.on_message = util.on_message
    client.loop_forever()


if __name__ == "__main__":
    main()
