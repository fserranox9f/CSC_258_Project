# Service Interfaces

This document describes the component boundaries in the active Kafka-based code path that is currently tracked in the repo.

## Current Service Flow

```text
Bluesky Jetstream -> ingestion -> Kafka -> processing -> storage -> dashboard
```

## Components

### Ingestion
Location:
- `services/ingestion/`

Responsibility:
- consume Bluesky Jetstream events
- normalize valid posts
- publish normalized posts to Kafka
- retry Jetstream connections after disconnects
- wait for Kafka delivery acknowledgement and surface publish failures

Key files:
- `main.py`
- `config.py`
- `normalize.py`
- `consumer.py`
- `producer.py`

### Broker
Location:
- `services/broker/`

Responsibility:
- define shared Kafka broker settings such as bootstrap server and topic name
- define producer delivery settings used by ingestion when publishing posts

Key file:
- `config.py`

### Processing
Location:
- `services/processing/`

Responsibility:
- consume normalized posts from Kafka
- validate the normalized Kafka payload shape before processing
- extract trend terms and phrases
- build trend snapshots and example posts

Key files:
- `main.py`
- `config.py`
- `consumer.py`
- `processor.py`

### Storage
Location:
- `services/storage/`

Responsibility:
- save trend snapshots to JSON files
- save example posts to JSON files for the dashboard

Key files:
- `trend_save.py`
- `config.py`

Output files:
- `services/storage/logs/trends.json`
- `services/storage/logs/example_posts.json`

### Dashboard
Location:
- `services/dashboard/`

Responsibility:
- load trend snapshots from saved JSON files
- display trends and example posts in the browser

Key files:
- `index.html`
- `script.js`
- `styles.css`

## Stable Interfaces To Preserve
- the normalized post payload emitted by ingestion
- the Kafka topic defined in `services/broker/config.py`
- the trend snapshot JSON structure saved by storage
- the dashboard input file locations used in `services/dashboard/script.js`
- the config values documented in `.env.example`, which mirrors the active Python config modules for reference

## Consistency Notes
- ingestion normalizes posts before publishing them to Kafka
- processing validates and then uses the normalized payload shape when extracting terms
- storage writes snapshots in a stable JSON structure for dashboard consumption
- storage saves snapshots with atomic temp-file replacement before swapping them into place

## Important Repo Note
- The active tracked implementation is centered on `ingestion`, `processing`, `storage`, `broker`, and `dashboard`.
- `.env.example` is a documentation aid for these current settings and is not automatically loaded by the services.
