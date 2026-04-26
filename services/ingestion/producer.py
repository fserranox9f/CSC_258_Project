# pushes post from normalize to kafka services

import json
from kafka import KafkaProducer
from services.broker.config import KAFKA_BOOTSTRAP_SERVERS, SOCIAL_POSTS_TOPIC


class KafkaPostProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda post: json.dumps(post).encode("utf-8"),
        )

    def send_post(self, post: dict):
        self.producer.send(SOCIAL_POSTS_TOPIC, post)
        print(f"Published post to Kafka: {post.get('post_id')}")

    def flush(self):
        self.producer.flush()

    def close(self):
        self.producer.flush()
        self.producer.close()