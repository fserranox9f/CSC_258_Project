from services.processing.consumer import KafkaPostConsumer
from services.processing.processor import TrendProcessor
from services.processing.config import POSTS_LAP, TOP_TERMS
from services.storage.trend_save import TrendStore



def print_top_terms(posts_processed: int, trends: list):
    print(f"\nProcessed {posts_processed} posts")
    print("Top trending words:")

    for term, count in trends:
        print(f"{term}: {count}")


if __name__ == "__main__":
    consumer = KafkaPostConsumer()
    processor = TrendProcessor()
    store = TrendStore()

    try:
        for post in consumer.read_posts():
            processor.process_post(post)

            if processor.posts_processed % POSTS_LAP == 0:
                trends = processor.top_terms(limit=TOP_TERMS)
                examples = processor.top_examples(limit=TOP_TERMS)
                print_top_terms(processor.posts_processed, trends)
                store.save_snapshot(processor.posts_processed, trends)
                store.save_example_posts(processor.posts_processed, examples)
    finally:
        consumer.close()
