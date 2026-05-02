# Producer Service

This service connects to Bluesky Jetstream, filters for post records, normalizes them,
and saves a sample dataset for downstream processing.

## Files

- `src/config.py` - connection settings
- `src/bluesky_consumer.py` - WebSocket listener
- `src/normalizer.py` - maps Bluesky events to internal schema
- `src/sample_write.py` - saves normalized posts
- `src/main.py` - entry point

## Run locally

```bash
python -m pip install -r requirements.txt
python src/main.py
```

## Configurable Settings

The producer supports configuration through environment variables:

- `PROJECT_ROOT`: base project path override
- `JETSTREAM_URL`: source WebSocket URL
- `SOURCE_NAME`: normalized source label written into posts
- `SAVE_SAMPLE_PATH`: output path for normalized posts
- `MAX_SAMPLE_POSTS`: stop condition for captured posts
- `RECONNECT_DELAY_SECONDS`: reconnect delay after connection errors

Example:

```bash
set MAX_SAMPLE_POSTS=500
set RECONNECT_DELAY_SECONDS=3
python src/main.py
```

## Interface Summary

Input:

- Bluesky Jetstream post events

Output:

- normalized post objects written to `storage/data/sample_post.json`

Shared contract:

- `../../common/post_schema.json`
