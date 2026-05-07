#-----------------------------------------------------
# Main Entry of Ingestion service
# Connect to Bluesky through websocket and get post based on event trigger. 
# The post is then JSON normalized and pushed to Kafka. 
#-----------------------------------------------------

from services.ingestion.config import *
from services.ingestion.normalize import normalize_post
from services.ingestion.consumer import WSconsumer
from services.ingestion.producer import KafkaPostProducer
from services.logging_utils import get_logger

logger = get_logger("services.ingestion.main")

# this is called everytime the websocket consumer detects an event.
def handle_kafka_event(event):

    # converts the event to a normalized format 
    post = normalize_post(event)    

    # skip unusable event 
    if post is None:
        return

    # send the normalized post to kafka
    sent = producer.send_post(post)

    if not sent:
        logger.warning("Kafka publish failed for a normalized post.")


if __name__ == "__main__":
    
    producer = KafkaPostProducer()                                                          # create kafka (producer)
    consumer = WSconsumer(on_event=handle_kafka_event, jetstream_index=JETSTREAM_INDEX)     # Create websocket (consumer)

    try:
        logger.info("Starting ingestion service with jetstream_index=%s", JETSTREAM_INDEX)
        consumer.run()                                                                      # *** Starts the websocket open loop *** 
    except Exception:
        logger.exception("Ingestion service stopped because of an unexpected error.")       
        raise
    finally:
        producer.close()                                            
        logger.info("Ingestion service shut down.")
