# -----------------------------------------------------
# Read JSON messages from Kafka, decode them into python dict, validate them and return message
# 
#   -- Scalability --
#       Consumers with the same group ID divide work across Kafka partitions.
#       if the Kafka topic has multiple partitions, multiple processing containers in the same group can scale horizontally
#   -- Falut tolerance --
#       Bad messages do not crash the service 
#       Docker restart policy can bring the service back
#   -- Security --
#       Validates message type and required fields
# -----------------------------------------------------

import json
import time

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
            SOCIAL_POSTS_TOPIC,                                                         # Config in broker. defines the topic name that ingestion publishes to and processing consumes from.
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,                                  # points to kafka servers
            value_deserializer=lambda message: json.loads(message.decode("utf-8")),     # converts JSON to python dict       
            auto_offset_reset="earliest",   # If consumer group has no saved offset yet, it starts from earliest available Kafka messages. fresh processing service can process existing messages instead of only new ones.
            enable_auto_commit=True,
            group_id="processing-service",
        )
        self.invalid_messages_skipped = 0

    # loops through kafka messages 
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

        if not isinstance(post, dict):      # check if its a python dictonary
            return False

        required_string_fields = ("post_id", "text", "author", "source")    

        for field in required_string_fields:    # check if all fields exists
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

    def _create_consumer_with_retry(self):
        for attempt in range(1, KAFKA_STARTUP_MAX_ATTEMPTS + 1):
            try:
                return KafkaConsumer(
                    SOCIAL_POSTS_TOPIC,
                    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                    value_deserializer=lambda message: json.loads(message.decode("utf-8")),
                    auto_offset_reset="earliest",
                    enable_auto_commit=True,
                    group_id="processing-service",
                )
            except NoBrokersAvailable:
                logger.warning(
                    "Kafka broker not ready for consumer initialization "
                    "(attempt %s/%s). Retrying in %.1f seconds.",
                    attempt,
                    KAFKA_STARTUP_MAX_ATTEMPTS,
                    KAFKA_STARTUP_RETRY_DELAY_SECONDS,
                )
                time.sleep(KAFKA_STARTUP_RETRY_DELAY_SECONDS)

        raise NoBrokersAvailable()
