from services.logging_utils import get_logger
from services.processing.consumer import KafkaPostConsumer
from services.processing.processor import TrendProcessor
from services.processing.config import POSTS_LAP, TOP_TERMS
from services.storage.trend_save import TrendStore


logger = get_logger("services.processing.main")


def print_top_terms(posts_processed: int, trends: list):
    logger.info("Processed %s posts", posts_processed)

    for term, count in trends:
        logger.info("Top trending term: %s=%s", term, count)


if __name__ == "__main__":
    consumer = KafkaPostConsumer()
    processor = TrendProcessor()
    store = TrendStore()

    try:
        logger.info("Starting processing service.")
        for post in consumer.read_posts():
            processed = processor.process_post(post)

            if not processed:
                logger.warning("Skipped invalid or unusable post during processing.")
                continue

            if processor.posts_processed % POSTS_LAP == 0:
                trends = processor.top_terms(limit=TOP_TERMS)
                examples = processor.top_examples(limit=TOP_TERMS)
                print_top_terms(processor.posts_processed, trends)
                store.save_snapshot(processor.posts_processed, trends)
                store.save_example_posts(processor.posts_processed, examples)
    except Exception:
        logger.exception("Processing service stopped because of an unexpected error.")
        raise
    finally:
        if consumer.invalid_messages_skipped:
            logger.warning(
                "Invalid Kafka messages skipped: %s",
                consumer.invalid_messages_skipped,
            )

        if processor.invalid_posts_skipped:
            logger.warning(
                "Invalid posts skipped during processing: %s",
                processor.invalid_posts_skipped,
            )

        if processor.pruned_topics:
            logger.warning("Tracked topics pruned from memory: %s", processor.pruned_topics)

        consumer.close()
        logger.info("Processing service shut down.")
