# Service Interfaces

This document describes the main component boundaries in the project.

## Design Goal

The system uses open design by keeping service responsibilities separate and by documenting
how components exchange data.

## Components

### Producer

Location:
- `services/producer/src/`

Responsibility:
- connect to Bluesky Jetstream
- extract valid post events
- normalize posts into the shared format
- save normalized posts for downstream processing

Input:
- Bluesky Jetstream event stream

Output:
- normalized post records written to `storage/data/sample_post.json`

Shared contract:
- `common/post_schema.json`

Configurable settings:
- `PROJECT_ROOT`
- `JETSTREAM_URL`
- `SOURCE_NAME`
- `SAVE_SAMPLE_PATH`
- `MAX_SAMPLE_POSTS`
- `RECONNECT_DELAY_SECONDS`

### Trend Service

Location:
- `services/trend_service/src/`

Responsibility:
- load normalized post data
- extract hashtags or keywords
- compute top trends
- expose results through HTTP endpoints

Input:
- normalized posts from `storage/data/sample_post.json`

Output:
- JSON API responses from `/`, `/trends`, and `/live-trends`

Configurable settings:
- `TREND_DATA_PATH`
- `TREND_WINDOW_SIZE`
- `TREND_TOP_K`
- `TREND_SERVICE_HOST`
- `TREND_SERVICE_PORT`
- `TREND_SERVICE_DEBUG`

### Shared Data Contract

Location:
- `common/post_schema.json`
- `common/normalize_shape.json`

Responsibility:
- define the normalized payload shape expected across services

## Current Integration Path

```text
Bluesky Jetstream -> Producer -> sample_post.json -> Trend Service API
```

## Planned Integration Path

```text
Bluesky Jetstream -> Producer -> Kafka -> Trend Service -> API / Dashboard
```

## Stable Interfaces To Preserve

These are the easiest interfaces to keep stable as the project evolves:

- normalized post structure in `common/post_schema.json`
- file location or future message payload shape used between producer and consumers
- trend service HTTP endpoints

As long as those interfaces stay documented and consistent, the internal implementation of each service can change more safely.
