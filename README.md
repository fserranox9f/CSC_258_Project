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
- `services/trend_service/src/config.py` for the older standalone trend service path

Reference file:

- `.env.example` mirrors the current config values as a documentation template, but it is not auto-loaded by the running services

## Run Paths In The Current Repo

### Ingestion service
Entry point:

```bash
python services/ingestion/main.py
```

Behavior:
- consumes Bluesky Jetstream events
- normalizes valid posts
- publishes them to Kafka

### Processing service
Entry point:

```bash
python services/processing/main.py
```

Behavior:
- consumes normalized posts from Kafka
- computes top trend terms
- stores trend snapshots and example posts

### Dashboard
Static files:

- `services/dashboard/index.html`
- `services/dashboard/script.js`
- `services/dashboard/styles.css`

The dashboard reads:

- `services/storage/logs/trends.json`
- `services/storage/logs/example_posts.json`

## Consistency
The current codebase improves consistency through:

- a normalized post structure produced before Kafka publishing
- Kafka as the handoff layer between ingestion and processing
- snapshot files written in a consistent JSON structure by storage helpers
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

## Notes
- The root README previously described an older `producer` / `trend_service` prototype flow.
- The active tracked code now centers on `ingestion`, `processing`, `storage`, `broker`, and `dashboard`.
- The `services/trend_service/src/` directory still contains a config file, but the main tracked runtime flow is Kafka-based through `ingestion` and `processing`.
- `.env.example` is included as a reference sheet for current settings, not as the active runtime configuration source.

## Files To Know
- [services/ingestion/main.py](C:/Users/miyan/OneDrive/Miazen_Documents/CSU_California-State/Spring-2026/CSC258/CSC_258_Project/services/ingestion/main.py)
- [services/ingestion/config.py](C:/Users/miyan/OneDrive/Miazen_Documents/CSU_California-State/Spring-2026/CSC258/CSC_258_Project/services/ingestion/config.py)
- [services/processing/main.py](C:/Users/miyan/OneDrive/Miazen_Documents/CSU_California-State/Spring-2026/CSC258/CSC_258_Project/services/processing/main.py)
- [services/processing/processor.py](C:/Users/miyan/OneDrive/Miazen_Documents/CSU_California-State/Spring-2026/CSC258/CSC_258_Project/services/processing/processor.py)
- [services/storage/trend_save.py](C:/Users/miyan/OneDrive/Miazen_Documents/CSU_California-State/Spring-2026/CSC258/CSC_258_Project/services/storage/trend_save.py)
- [services/dashboard/index.html](C:/Users/miyan/OneDrive/Miazen_Documents/CSU_California-State/Spring-2026/CSC258/CSC_258_Project/services/dashboard/index.html)
- [INTERFACES.md](C:/Users/miyan/OneDrive/Miazen_Documents/CSU_California-State/Spring-2026/CSC258/CSC_258_Project/INTERFACES.md)
