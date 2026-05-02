# main entry to ingestion

from services.ingestion.config import *
from services.ingestion.normalize import normalize_post
from services.ingestion.consumer import WSconsumer
from services.ingestion.writer import SampleWriter
from services.ingestion.producer import KafkaPostProducer


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

    producer.send_post(post)

if __name__ == "__main__":

    # --- test local post dump ---
    # writer = SampleWriter(max_posts=MAX_SAMPLE_POSTS)
    # consumer = WSconsumer(on_event=handle_event, jetstream_index=JETSTREAM_INDEX)
    # consumer.run()

    # --- write post to kafka ---
    producer = KafkaPostProducer()
    consumer = WSconsumer(on_event=handle_kafka_event, jetstream_index=JETSTREAM_INDEX)

    try:
        consumer.run()
    finally:
        producer.close()