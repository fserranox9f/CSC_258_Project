# read data from kafka

import json
from kafka import KafkaConsumer

from services.broker.config import KAFKA_BOOTSTRAP_SERVERS, SOCIAL_POSTS_TOPIC

class KafkaPostConsumer:
    def __init__(self):
        self.consumer = KafkaConsumer(
            SOCIAL_POSTS_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda message: json.loads(message.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            group_id="processing-service",
        )

    def read_posts(self):
        for message in self.consumer:
            yield message.value

    def close(self):
        self.consumer.close()

