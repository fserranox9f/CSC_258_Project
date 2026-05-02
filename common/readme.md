# Common Data Contract

The `common/` folder defines the shared data format used between project components.

## Purpose

Open design in this project means each service should communicate through a clear,
documented interface instead of hidden internal assumptions.

For Implementation 1, the main shared interface is the normalized social post format.
The producer writes data in this shape, and downstream services such as the trend service
read the same shape.

## Files

- `post_schema.json`: JSON schema for a normalized social post
- `normalize_shape.json`: example normalized post object

## Normalized Post Fields

- `post_id`: unique identifier for the post
- `timestamp`: original creation timestamp when available
- `text`: normalized post text
- `author`: source author identifier when available
- `source`: source platform name such as `bluesky`
- `is_repost`: whether the post is a repost

## Current Producer Contract

The producer service is expected to:

1. ingest Bluesky events
2. normalize each valid post into the shared format
3. append normalized posts to `storage/data/sample_post.json`
4. preserve the shared field names and meanings defined in `post_schema.json`

## Current Trend Service Contract

The trend service is expected to:

1. read normalized posts from `storage/data/sample_post.json`
2. analyze the most recent posts inside the configured window
3. return trend results through `/trends` and `/live-trends`

## Why This Supports Open Design

Because the shared format is documented here:

- services can be changed independently as long as they keep the contract
- Kafka can later replace file-based communication without changing the normalized payload shape
- future components such as a dashboard, database writer, or consumer can reuse the same schema
