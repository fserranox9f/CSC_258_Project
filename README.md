# CSC 258 Project
Real-Time Social Media Adaptive Trend System

## Overview
This project collects social media post data, converts it into a shared internal format, and analyzes that data to identify trending terms.

Implementation 1 focuses on a working prototype with two main services:

- `producer`: connects to the Bluesky Jetstream feed, normalizes post data, and saves it to a JSON file
- `trend_service`: reads the saved post data and exposes trend results through a Flask API

## Adaptability

The project currently supports adaptability through:

- separate services that can change independently
- configurable producer and trend-service settings
- a shared normalized data contract that allows future components to reuse the same payload shape
- trend-service options for analysis mode and optional source filtering

This makes it easier to add new sources, adjust analysis behavior, or replace file-based communication later without rebuilding the whole system.

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

## Open Design

The project currently supports open design through:

- separate services with clear responsibilities
- a shared normalized post contract in [common/post_schema.json](C:/Users/miyan/OneDrive/Miazen_Documents/CSU_California-State/Spring-2026/CSC258/CSC_258_Project/common/post_schema.json)
- documented service boundaries in [INTERFACES.md](C:/Users/miyan/OneDrive/Miazen_Documents/CSU_California-State/Spring-2026/CSC258/CSC_258_Project/INTERFACES.md)

This makes it easier to replace the current file-based handoff with Kafka later without changing the meaning of the payload itself.

## What Is Done
- The project is split into separate services, including a `producer` and a `trend_service`
- The `producer` collects Bluesky post data and normalizes it into a shared internal format
- The normalized data is stored in `storage/data/sample_post.json` for downstream processing
- The `trend_service` reads the stored data and returns trending keywords through a Flask API
- The project demonstrates separation of concerns, modular service design, and a prototype of distributed-system architecture
- The system can be run locally and tested through endpoints such as `/trends` and `/live-trends`
- Cached trend responses improve repeated request performance

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
python -m pip install -r services/trend_service/requirements.txt
python services/trend_service/src/trend_detector.py
```

Open these endpoints in a browser:

- `http://127.0.0.1:5000/`
- `http://127.0.0.1:5000/trends`
- `http://127.0.0.1:5000/live-trends`

## Run The Producer
From the project root:

```bash
python -m pip install -r services/producer/requirements.txt
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
- Replace file-based communication with Kafka for true distributed messaging
- Connect the `producer` directly to Kafka topics
- Update the `trend_service` to consume messages in real time instead of relying on a local JSON file
- Improve fault tolerance and availability with better service recovery and messaging reliability
- Add stronger security between components
- Improve scalability by allowing more services or instances to run in parallel
- Improve trend quality with better filtering and NLP techniques
- Add automated tests for producer normalization and trend extraction
- Add a dashboard or frontend for visualization
- Finish container orchestration for all services

## Distributed System Evaluation

The current project already demonstrates some distributed-system ideas through service separation and modular design, 
but other qualities still need more implementation work.

### Easy
- `Open design`: the project already has separate services, clear roles, and defined endpoints
- `Adaptability`: the `producer` and `trend_service` are separated, so the system can be extended more easily
- `Consistency`: the current file-based workflow makes consistency simpler because both services rely on one shared data source

### Medium
- `Availability`: improving this would require better recovery behavior and more reliable service operation
- `Security`: this would require stronger validation, safer communication, and better control over component access

### Hard
- `Fault tolerance`: this would require stronger recovery from service failures, retries, and more durable communication
- `Scalability`: the current file-based system does not scale well, so true scalability would require Kafka or another distributed messaging system

In summary, the project currently shows the structure of a distributed-system prototype, but the more advanced qualities such as scalability and fault tolerance still require additional work.

## Files To Know
- [services/producer/src/main.py]
- [services/producer/src/normalizer.py]
- [services/trend_service/src/trend_detector.py]
- [storage/data/sample_post.json]
- [common/post_schema.json](C:/Users/miyan/OneDrive/Miazen_Documents/CSU_California-State/Spring-2026/CSC258/CSC_258_Project/common/post_schema.json)
- [INTERFACES.md](C:/Users/miyan/OneDrive/Miazen_Documents/CSU_California-State/Spring-2026/CSC258/CSC_258_Project/INTERFACES.md)
