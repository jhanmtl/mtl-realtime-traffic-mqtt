import backendtools
import redis

broker = 'broker.hivemq.com'
port = 1883
value_types = ["vehicle-gap-time", "vehicle-count", "vehicle-speed", "CreateUtc"]
data_template = {'vehicle-gap-time': [], 'vehicle-speed': [], 'vehicle-count': [], 'time': []}


def main():
    df = backendtools.read_csv("detectors-simulated.csv")
    detector_topics = df['topics'].values.tolist()
    detector_ids=df['id'].values.tolist()
    value_types = ["vehicle-gap-time", "vehicle-count", "vehicle-speed"]
    active_topics=[]
    for each_topic in detector_topics:
        for each_type in value_types:
            active_topics.append((each_topic + each_type,0))

    db = redis.Redis()
    backendtools.initialize_db(db, detector_ids, data_template)

    client = backendtools.connect_mqtt(broker, port)
    client.user_data_set(db)
    client.subscribe(active_topics)

    client.on_message = backendtools.on_message
    client.loop_forever()


if __name__ == "__main__":
    main()
