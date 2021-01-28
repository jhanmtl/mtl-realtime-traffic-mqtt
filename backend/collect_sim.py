import backend_utils
import redis

broker = 'broker.hivemq.com'
port = 1883
value_types = ["vehicle-gap-time", "vehicle-count", "vehicle-speed", "CreateUtc"]
data_template = {'vehicle-gap-time': [], 'vehicle-speed': [], 'vehicle-count': [], 'time': []}


def main():
    df = backend_utils.read_csv('detectors-active.csv')
    active_ids = df['id'].values.tolist()
    active_topics = backend_utils.extract_topics(df)

    db = redis.Redis(host='localhost', port=6379, db=1)
    backend_utils.initialize_db(db, active_ids, data_template)
    incoming_data = backend_utils.initialize_incoming_data(active_ids, value_types)

    client = backend_utils.connect_mqtt(broker, port)
    client.user_data_set([incoming_data, db])
    client.subscribe(active_topics)

    client.on_message = backend_utils.on_message
    client.loop_forever()


if __name__ == "__main__":
    main()
