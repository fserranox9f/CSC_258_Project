# main entry to ingestion

from services.logging_utils import get_logger
from services.ingestion.config import *
from services.ingestion.normalize import normalize_post
from services.ingestion.consumer import WSconsumer
from services.ingestion.writer import SampleWriter
from services.ingestion.producer import KafkaPostProducer


logger = get_logger("services.ingestion.main")


#def handle_local_event(event, ws):
#    post = normalize_post(event)

#    if post is None:
#        return

#    writer.add_post(post)

#    if writer.is_full():
#        writer.save()
#        ws.close()

def handle_kafka_event(event, ws):
    post = normalize_post(event)

    if post is None:
        return

    sent = producer.send_post(post)

    if not sent:
        logger.warning("Kafka publish failed for a normalized post.")

if __name__ == "__main__":

    # --- test local post dump ---
    # writer = SampleWriter(max_posts=MAX_SAMPLE_POSTS)
    # consumer = WSconsumer(on_event=handle_event, jetstream_index=JETSTREAM_INDEX)
    # consumer.run()

    # --- write post to kafka ---
    producer = KafkaPostProducer()
    consumer = WSconsumer(on_event=handle_kafka_event, jetstream_index=JETSTREAM_INDEX)

    try:
        logger.info("Starting ingestion service with jetstream_index=%s", JETSTREAM_INDEX)
        consumer.run()
    except Exception:
        logger.exception("Ingestion service stopped because of an unexpected error.")
        raise
    finally:
        producer.close()
        logger.info("Ingestion service shut down.")
