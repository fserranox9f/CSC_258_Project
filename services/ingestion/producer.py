# -----------------------------------------------
# Takes the normalized post and pushes it to Kafka 
# 
#   -- open design --
#       main.py does not need to know how Kafka serialization, retries, topics, or acknowledgements work
#       Kafka logic is encapsulated in KafkaPostProducer
#
#   -- Fault Tolerance --
#       If Kafka has a temporary problem, the producer retries instead of failing immediately.
#       prevents the service from waiting forever when Kafka is unhealthy
#       Kafka gives the service a real success/failure signal

#   -- Scalability --
#       Kafka itself is the major scalability feature
#       ingestion and processing are decoupled

#   -- security --
#       Full post text is not logged. social media text can contain personal data,
#       sensitive content not want copied into logs.
#
# -----------------------------------------------

import json
from kafka import KafkaProducer
from kafka.errors import KafkaError
from services.broker.config import *
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
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,      # Kafka broker address. Docker server address
            acks=KAFKA_ACKS,                                # Require Kafka acknowledgement before treating a message as delivered.
            retries=KAFKA_PRODUCER_RETRIES,                 # Retry temporary Kafka publish failures before giving up.
            retry_backoff_ms=KAFKA_RETRY_BACKOFF_MS,
            request_timeout_ms=KAFKA_REQUEST_TIMEOUT_MS,        # Bound how long the producer waits for Kafka requests/delivery.
            delivery_timeout_ms=KAFKA_DELIVERY_TIMEOUT_MS,
            value_serializer=lambda post: json.dumps(post).encode("utf-8"),  # Convert the normalized post dictionary into JSON bytes for Kafka
        )

    # publishes a post to kafka
    def send_post(self, post: dict):
        post_id = post.get("post_id", "unknown")

        try:
            future = self.producer.send(SOCIAL_POSTS_TOPIC, post)
            metadata = future.get(timeout=KAFKA_SEND_TIMEOUT_SECONDS)       # Wait for Kafka to confirm the send and return partition/offset metadata.
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
