# pushes post from normalize to kafka services

import json
from kafka import KafkaProducer
from kafka.errors import KafkaError
from services.broker.config import (
    KAFKA_ACKS,
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_DELIVERY_TIMEOUT_MS,
    KAFKA_PRODUCER_RETRIES,
    KAFKA_REQUEST_TIMEOUT_MS,
    KAFKA_RETRY_BACKOFF_MS,
    KAFKA_SEND_TIMEOUT_SECONDS,
    SOCIAL_POSTS_TOPIC,
)
from services.logging_utils import get_logger


logger = get_logger("services.ingestion.producer")


class KafkaPostProducer:
    def __init__(self):
        logger.info(
            "Initializing Kafka producer for topic=%s bootstrap_servers=%s",
            SOCIAL_POSTS_TOPIC,
            KAFKA_BOOTSTRAP_SERVERS,
        )
        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            acks=KAFKA_ACKS,
            retries=KAFKA_PRODUCER_RETRIES,
            retry_backoff_ms=KAFKA_RETRY_BACKOFF_MS,
            request_timeout_ms=KAFKA_REQUEST_TIMEOUT_MS,
            delivery_timeout_ms=KAFKA_DELIVERY_TIMEOUT_MS,
            value_serializer=lambda post: json.dumps(post).encode("utf-8"),
        )

    def send_post(self, post: dict):
        post_id = post.get("post_id", "unknown")

        try:
            future = self.producer.send(SOCIAL_POSTS_TOPIC, post)
            metadata = future.get(timeout=KAFKA_SEND_TIMEOUT_SECONDS)
            logger.info(
                "Published post to Kafka: %s (partition=%s, offset=%s)",
                post_id,
                metadata.partition,
                metadata.offset,
            )
            return True
        except KafkaError as error:
            logger.error("Failed to publish post to Kafka: %s. Error: %s", post_id, error)
            return False

    def flush(self):
        self.producer.flush()

    def close(self):
        self.producer.flush()
        self.producer.close()
        logger.info("Kafka producer closed.")
