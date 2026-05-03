# CSC 258 Project
Real-Time Social Media Adaptive Trend System

## Overview
This project ingests live Bluesky posts, publishes normalized posts to Kafka, processes those posts into trend snapshots, saves the results locally, and exposes them to a simple dashboard.

The current tracked codebase is organized around these active services:

- `ingestion`: reads Bluesky Jetstream data, normalizes posts, and publishes them
- `broker`: stores shared Kafka connection settings
- `processing`: consumes normalized posts from Kafka and computes trend terms
- `storage`: saves trend snapshots and example posts to local JSON files
- `dashboard`: reads the saved JSON snapshots and renders a frontend view

## Current Architecture

```text
Bluesky Jetstream -> ingestion -> Kafka -> processing -> storage -> dashboard
```

## What Is Implemented
- Bluesky ingestion through WebSocket consumers
- Normalization into a shared post shape
- Kafka publishing and consuming with `kafka-python`
- Trend extraction from normalized posts
- Snapshot storage in local JSON files
- Dashboard frontend that reads saved snapshot files

## Repository Structure

```text
services/
  broker/
  dashboard/
  ingestion/
  processing/
  storage/
```

## Active Configuration
The current tracked code uses Python config modules rather than environment-variable loading.

Main config files:

- `services/broker/config.py`
- `services/ingestion/config.py`
- `services/processing/config.py`
- `services/storage/config.py`

Reference file:

- `.env.example` mirrors the current config values as a documentation template, but it is not auto-loaded by the running services
- all services also support shared logging level control through `LOG_LEVEL`
- the ingestion service also supports reconnect tuning through `RECONNECT_DELAY_SECONDS`, `MAX_RECONNECT_DELAY_SECONDS`, and `RECONNECT_BACKOFF_MULTIPLIER`
- the broker and ingestion path also support Kafka delivery tuning through `KAFKA_ACKS`, `KAFKA_PRODUCER_RETRIES`, `KAFKA_RETRY_BACKOFF_MS`, `KAFKA_REQUEST_TIMEOUT_MS`, `KAFKA_DELIVERY_TIMEOUT_MS`, and `KAFKA_SEND_TIMEOUT_SECONDS`
- the processing service also supports memory bounds through `MAX_EXAMPLES_PER_TOPIC` and `MAX_TRACKED_TOPICS`

## Run Paths In The Current Repo

### Docker Compose

You can start the main local stack with:

```bash
docker compose up
```

This Compose stack starts:

- `broker` on `localhost:9092`
- `ingestion` as a Python service that publishes posts to Kafka
- `processing` as a Python service that consumes Kafka posts and writes trend snapshots
- `dashboard` on `http://localhost:8000/dashboard/index.html`

Notes:

- the dashboard serves the `services/` directory so it can read `storage/logs/*.json`
- the Python services use `broker:9093` inside Docker, while host tools can still use `localhost:9092`

Useful commands:

```bash
docker compose up -d
docker compose ps
docker compose logs --tail=50
docker compose down
```

Current verification status:

- the Compose stack has been validated with `docker compose config`
- `broker`, `ingestion`, `processing`, and `dashboard` were all started successfully
- the dashboard is available at `http://localhost:8000/dashboard/index.html`

### Ingestion service
Entry point:

```bash
python services/ingestion/main.py
```

Behavior:
- consumes Bluesky Jetstream events
- normalizes valid posts
- publishes them to Kafka
- retries Jetstream connections with bounded exponential backoff if the socket drops
- waits for Kafka send acknowledgements and logs producer delivery failures

### Processing service
Entry point:

```bash
python services/processing/main.py
```

Behavior:
- consumes normalized posts from Kafka
- validates consumed messages before processing them
- computes top trend terms
- keeps per-topic examples and tracked topic state bounded in memory
- stores trend snapshots and example posts

### Dashboard
Static files:

- `services/dashboard/index.html`
- `services/dashboard/script.js`
- `services/dashboard/styles.css`

The dashboard reads:

- `services/storage/logs/trends.json`
- `services/storage/logs/example_posts.json`

Local dashboard server:

```bash
python -m http.server 8000 --directory services
```

Then open:

```text
http://localhost:8000/dashboard/index.html
```

## Consistency
The current codebase improves consistency through:

- a normalized post structure produced before Kafka publishing
- Kafka as the handoff layer between ingestion and processing
- snapshot files written in a consistent JSON structure by storage helpers
- atomic temp-file replacement when trend snapshots are saved
- validation of consumed Kafka payloads before trend processing
- processing logic that only works from the consumed normalized post payload shape

## Open Design
The current codebase supports open design through:

- separate services for ingestion, processing, storage, broker settings, and dashboard rendering
- shared broker settings in a dedicated module
- clear service entry points in `main.py` files
- documented component boundaries in `INTERFACES.md`

## Adaptability
The current codebase supports adaptability through:

- modular service separation
- isolated config files per service
- the ability to switch Jetstream endpoints and Kafka settings from config modules
- storage and dashboard components that can be changed without rewriting ingestion logic

## Remaining Work By Effort

| Effort | Distributed Component Areas | Work To Do |
|---|---|---|
| Low | Open design, Adaptability, Consistency | Keep interface docs aligned with the tracked services, move more settings toward a consistent config pattern, add payload validation tests, and make storage writes safer with atomic file replacement. |
| Medium | Availability, Scalability | Finish `docker-compose.yml`, add reconnect and retry behavior for Jetstream and Kafka, improve service startup reliability, and reduce unbounded in-memory or file growth in processing and storage. |
| High | Fault tolerance, Security | Add stronger recovery behavior for crashes and partial failures, improve replay-safe processing and delivery guarantees, protect broker and service configuration, and introduce safer access control and communication between components. |

### Effort Ranking
1. `Low`: Open design, Adaptability, Consistency
2. `Medium`: Availability, Scalability
3. `High`: Fault tolerance, Security

## Project Completion Checklist

### Must Finish
- [x] Finish `docker-compose.yml` so the full pipeline can be started more easily
- [x] Add a documented dashboard run method
- [x] Add a single end-to-end startup flow for broker, ingestion, processing, and dashboard
- [x] Keep the top-level docs aligned with the active Kafka-based architecture

### Should Finish
- [x] Add reconnect and retry behavior for the Bluesky Jetstream consumer
- [x] Add stronger Kafka producer delivery and error handling
- [x] Make trend snapshot writes use atomic temp-file replacement
- [x] Validate consumed messages before trend processing
- [x] Add tests for normalization, processing, and storage output
- [x] Improve startup, runtime, and failure logging
- [x] Clean tracked logs, generated JSON snapshots, and tracked `__pycache__` files if they are not intended submission artifacts

### Nice To Finish
- [ ] Improve trend quality and reduce noisy keywords
- [x] Limit unbounded in-memory growth in the trend processor
- [ ] Add rotation or retention rules for stored snapshots
- [ ] Move more runtime settings toward a clearer environment-based configuration pattern
- [ ] Add a simple verification script or CI workflow

## Notes
- The root README and `INTERFACES.md` now describe the active Kafka-based pipeline.
- The active tracked code centers on `ingestion`, `processing`, `storage`, `broker`, and `dashboard`.
- `.env.example` is included as a reference sheet for current settings, not as the active runtime configuration source.

## Files To Know
- [services/ingestion/main.py](C:/Users/miyan/OneDrive/Miazen_Documents/CSU_California-State/Spring-2026/CSC258/CSC_258_Project/services/ingestion/main.py)
- [services/ingestion/config.py](C:/Users/miyan/OneDrive/Miazen_Documents/CSU_California-State/Spring-2026/CSC258/CSC_258_Project/services/ingestion/config.py)
- [services/processing/main.py](C:/Users/miyan/OneDrive/Miazen_Documents/CSU_California-State/Spring-2026/CSC258/CSC_258_Project/services/processing/main.py)
- [services/processing/processor.py](C:/Users/miyan/OneDrive/Miazen_Documents/CSU_California-State/Spring-2026/CSC258/CSC_258_Project/services/processing/processor.py)
- [services/storage/trend_save.py](C:/Users/miyan/OneDrive/Miazen_Documents/CSU_California-State/Spring-2026/CSC258/CSC_258_Project/services/storage/trend_save.py)
- [services/dashboard/index.html](C:/Users/miyan/OneDrive/Miazen_Documents/CSU_California-State/Spring-2026/CSC258/CSC_258_Project/services/dashboard/index.html)
- [INTERFACES.md](C:/Users/miyan/OneDrive/Miazen_Documents/CSU_California-State/Spring-2026/CSC258/CSC_258_Project/INTERFACES.md)
