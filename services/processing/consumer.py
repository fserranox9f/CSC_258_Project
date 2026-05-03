# read data from kafka

import json
from kafka import KafkaConsumer
from kafka.errors import KafkaError

from services.broker.config import KAFKA_BOOTSTRAP_SERVERS, SOCIAL_POSTS_TOPIC
from services.logging_utils import get_logger


logger = get_logger("services.processing.consumer")

class KafkaPostConsumer:
    def __init__(self):
        logger.info(
            "Initializing Kafka consumer for topic=%s bootstrap_servers=%s",
            SOCIAL_POSTS_TOPIC,
            KAFKA_BOOTSTRAP_SERVERS,
        )
        self.consumer = KafkaConsumer(
            SOCIAL_POSTS_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda message: json.loads(message.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            group_id="processing-service",
        )
        self.invalid_messages_skipped = 0

    def read_posts(self):
        try:
            for message in self.consumer:
                post = message.value

                if self._is_valid_post(post):
                    yield post
                else:
                    self.invalid_messages_skipped += 1
                    logger.warning("Skipped invalid Kafka message payload.")
        except KafkaError as error:
            logger.error("Kafka consumer error: %s", error)

    def _is_valid_post(self, post):
        if not isinstance(post, dict):
            return False

        required_string_fields = ("post_id", "text", "author", "source")

        for field in required_string_fields:
            value = post.get(field)

            if not isinstance(value, str) or not value.strip():
                return False

        timestamp = post.get("timestamp")
        is_repost = post.get("is_repost")

        if timestamp is not None and not isinstance(timestamp, str):
            return False

        if not isinstance(is_repost, bool):
            return False

        return True

    def close(self):
        self.consumer.close()
        logger.info("Kafka consumer closed.")

