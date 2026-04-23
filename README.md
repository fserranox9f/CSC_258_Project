# CSC 258 Project
Real-Time Social Media Adaptive Trend System

## Overview
This project collects social media post data, converts it into a shared internal format, and analyzes that data to identify trending terms.

Implementation 1 focuses on a working prototype with two main services:

- `producer`: connects to the Bluesky Jetstream feed, normalizes post data, and saves it to a JSON file
- `trend_service`: reads the saved post data and exposes trend results through a Flask API

## Current Architecture
Current implementation:

```text
Bluesky Jetstream -> Producer -> sample_post.json -> Trend Service API
```

Planned future architecture:

```text
Bluesky Jetstream -> Producer -> Kafka -> Trend Service -> API / Dashboard
```

Kafka is part of the planned distributed-system design, but the current submission uses file-based communication so the prototype can be run and demonstrated locally.

## What Is Implemented
- Bluesky post ingestion through a WebSocket consumer
- Normalization of incoming post data into a shared internal schema
- Storage of normalized posts in `storage/data/sample_post.json`
- Trend detection using recent posts and extracted hashtags/keywords
- Flask API endpoints for status and trend results
- Cached trend responses to improve repeated request performance

## Repository Structure
```text
common/
  normalize_shape.json
  post_schema.json
services/
  producer/
    src/
  trend_service/
    src/
storage/
  data/
    sample_post.json
```

## Requirements
- Python 3.11+ recommended
- Internet access is required only for the `producer` service when collecting live Bluesky data

## Run The Trend Service

From the project root:
```bash
pip install -r services/trend_service/requirements.txt
python services/trend_service/src/trend_detector.py
```

Open these endpoints in a browser:

- `http://127.0.0.1:5000/`
- `http://127.0.0.1:5000/trends`
- `http://127.0.0.1:5000/live-trends`

## Run The Producer
From the project root:

```bash
pip install -r services/producer/requirements.txt
python services/producer/src/main.py
```

What it does:
- connects to Bluesky Jetstream
- filters post events
- normalizes each post
- appends posts to `storage/data/sample_post.json`
- stops after reaching the configured sample limit

## Suggested Demo Flow
1. Start the trend service.
2. Open `/trends` to confirm the API is running.
3. Run the producer to collect or refresh post data.
4. Refresh `/trends` to view the current top trend output.
5. Open `/live-trends` to view the live-window trend response.

## API Endpoints

### `/`
Returns service status and available endpoints.

### `/trends`
Returns top trends from file-backed post data in `sample_post.json`.

### `/live-trends`
Returns trends from the in-memory live window. If the live window is empty, the service seeds it from the most recent stored posts so the endpoint remains useful during local demos.

## Notes For Implementation 1
- The current system is intentionally file-based
- Kafka is not yet wired into the running pipeline
- `docker-compose.yml` is not yet complete
- The current prototype is intended to demonstrate service separation, ingestion, normalization, and trend analysis

## Future Work
- Replace JSON file communication with Kafka topics
- Add a true streaming consumer path into the trend service
- Improve trend quality with better filtering and NLP techniques
- Add automated tests for producer normalization and trend extraction
- Add a dashboard or frontend for visualization
- Finish container orchestration for all services

## Files To Know
- [services/producer/src/main.py]
- [services/producer/src/normalizer.py]
- [services/trend_service/src/trend_detector.py]
- [storage/data/sample_post.json]
