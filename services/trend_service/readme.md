# Trend Detection Service

## Overview

The Trend Detection Service analyzes social media posts and identifies trending topics in real time. It processes text data, extracts hashtags, and returns the most frequent keywords as trends.

This service is part of our distributed microservices architecture for the CSC258 project.

---

## Why This Service Was Created

In a distributed system, different services handle different responsibilities. While the producer service collects data from social media, a separate service is needed to process that data and extract useful insights.

This service was created to:

* Analyze incoming social media data
* Identify trending topics based on hashtag frequency
* Simulate real-time stream processing
* Serve as a foundation for future streaming integration (Kafka / Bluesky)

It demonstrates key distributed systems concepts such as:

* Separation of concerns
* Scalability
* Real-time processing

---

## How It Works

### Data Source

The service currently reads posts from:

```
storage/data/sample_post.json
```

### Processing Steps

For each post:

* Text is cleaned (lowercase, punctuation removed)
* Hashtags are extracted

### Trend Detection

* Uses a **sliding window** of recent posts
* Counts hashtag frequency
* Returns the **top trending keywords**

---

## API Endpoints

The service is implemented as a Flask API.

### `/`

Returns service status.

### `/trends`

Returns top trends based on stored data.

### `/live-trends`

Returns trends from live in-memory data (used for future streaming integration).

---

## How to Run

Install dependencies and run the service from the project workspace:

```bash
python -m pip install -r services/trend_service/requirements.txt
python services/trend_service/src/trend_detector.py
```

Then open in your browser:

```
http://127.0.0.1:5000/trends
```

---

## Configurable Settings

The trend service now supports configuration through environment variables:

- `TREND_DATA_PATH`: path to the normalized post data file
- `TREND_WINDOW_SIZE`: number of recent posts to analyze
- `TREND_TOP_K`: number of top trend terms to return
- `TREND_TERM_MODE`: analysis mode (`auto`, `hashtags`, or `keywords`)
- `TREND_SOURCE_FILTER`: optional source name filter such as `bluesky`
- `TREND_SEED_LIVE_FROM_FILE`: whether `/live-trends` seeds from file data when empty
- `TREND_SERVICE_HOST`: host used by the Flask app
- `TREND_SERVICE_PORT`: port used by the Flask app
- `TREND_SERVICE_DEBUG`: enables or disables Flask debug mode

Example:

```bash
set TREND_WINDOW_SIZE=100
set TREND_TOP_K=10
set TREND_TERM_MODE=hashtags
python services/trend_service/src/trend_detector.py
```

---

## Dependencies

* Flask (for API)
* Python standard libraries:

  * `json`
  * `re`
  * `collections`
  * `pathlib`

---

## Kafka (Future Integration)

Kafka will be used as a message broker between services.

### How it will work:

```
Producer → Kafka Topic → Trend Service → API / Dashboard
```

* The producer will send social media posts to a Kafka topic
* The trend service will consume messages in real time
* This replaces file-based communication

### Benefits:

* Scalability
* Fault tolerance
* Loose coupling between services
* Real-time processing

---

## Future Improvements

* Connect to Kafka for real-time streaming
* Integrate Bluesky live data stream
* Improve trend detection using NLP techniques
* Connect to a dashboard for visualization
* Containerize using Docker

---

## How It Was Implemented

* Built using Python
* Designed as a microservice inside `services/`
* Implemented hashtag-based trend detection
* Added sliding window logic for recent trends
* Converted into a Flask API for integration with other services

---

## Resources

* Python Documentation: https://docs.python.org/3/
* Flask Documentation
* Python `collections` module (Counter, deque)
* Python `re` module
* Course materials (CSC258 Distributed Systems)

---

## Contribution

This service was designed and implemented to handle trend detection and provide a real-time API for retrieving trending topics.
