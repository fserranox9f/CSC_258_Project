# Real Time Social Media Trend Analysis

## A CSC 258 Distributed Systems Project

This project is a real time social media trend detection system. It collects live posts from Bluesky, sends them through Kafka, processes the posts into trend data, stores the results in PostgreSQL, and displays the latest trends on a local dashboard.

| Team Member           | Role                              |
| --------------------- | --------------------------------- |
| **Abdurrehman Aslam** | Code Developer and Paper Reviewer |
| **Abubaker Sayyed**   | Paper Writer and Code Reviewer    |
| **Fidel Serrano**     | Code Developer and Paper Reviewer |
| **Soulius Jones**     | Paper Writer and Code Reviewer    |

## Code Structure

https://github.com/fserranox9f/CSC_258_Project.git

The code is structured into 5 main services used by the system.
The flow of the program is:

```text
Bluesky Jetstream -> ingestion -> broker -> processing -> storage -> dashboard
```

The ingestion service opens a continuous WebSocket connection to Bluesky Jetstream. It receives raw event JSON, normalizes valid posts into a common JSON format, and publishes the normalized posts to Kafka.

The broker service is Apache Kafka. Kafka works as the communication layer between ingestion and processing. This allows ingestion and processing to run separately instead of calling each other directly.

The processing service reads normalized posts from Kafka. It validates posts, extracts trending words, hashtags, and phrases, and creates trend snapshots after a configured number of processed posts.

The storage service is a Flask API. Processing sends trend snapshots and example posts to this API. The storage service is the only service that connects directly to PostgreSQL, which keeps database access separate from the rest of the system.

The database service is PostgreSQL. It stores trend snapshots, trend terms, and example posts.

The dashboard service is a local web dashboard. It fetches the latest trend data from the storage API and displays it to the user.

```text
services
    broker
        config.py
    ingestion
        consumer.py
        config.py
        main.py
        normalize.py
        producer.py
    processing
        consumer.py
        config.py
        main.py
        processor.py
    storage
        api_client.py
        config.py
        database_store.py
        main.py
        sql_lib
            create_tables.sql
            insert_trend_snapshot.sql
            insert_trend_term.sql
            insert_trend_example.sql
            select_latest_trends.sql
            select_latest_examples.sql
    dashboard
        index.html
        styles.css
        script.js
tests
    test_normalize.py
    test_processor.py
    test_trend_store.py
```

## Dependencies and Environment

The project currently uses Python, Docker, Kafka, PostgreSQL, Flask, and JavaScript.

Python dependencies are listed in `requirements.txt`.

Docker Desktop is needed to run the local deployment. Docker Compose starts all services together.

- Operating system: Windows
- Shell: PowerShell
- Python runtime: Python 3.11
- Container runtime: Docker Desktop
- Message broker: Apache Kafka running in Docker
- Database: PostgreSQL running in Docker
- Storage API: Flask API running at `http://localhost:5001`
- Dashboard server: Python local HTTP server at `http://localhost:8000/dashboard/index.html`
- Kafka host port: `localhost:9092`
- PostgreSQL host port: `localhost:5432`

The `.env.variables` file is a reference file for environment variables. The Docker Compose file sets the main local service values directly.

## How to Run

The following commands should be run from the root level of the project.

1. Start the full local deployment.

```powershell
docker compose up
```

Or run the stack in the background:

```powershell
docker compose up -d
```

This starts:

- Kafka broker
- ingestion service
- processing service
- PostgreSQL database
- storage Flask API
- dashboard service

2. Check that containers are running.

```powershell
docker compose ps
```

3. Open the dashboard in a browser.

```text
http://localhost:8000/dashboard/index.html
```

4. Check the storage API directly.

```text
http://localhost:5001/api/latest-trends
http://localhost:5001/api/latest-examples
```

5. Stop the local deployment.

```powershell
docker compose down
```

To also remove the PostgreSQL volume and delete saved database data:

```powershell
docker compose down -v
```

## Other

Validate the Docker Compose file:

```powershell
docker compose config
```

View service logs:

```powershell
docker compose logs -f
```

View logs for a specific service:

```powershell
docker compose logs -f ingestion
docker compose logs -f processing
docker compose logs -f storage
docker compose logs -f db
```

See messages in Kafka:

```powershell
docker exec -it broker /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic BlueSky_socialmedia_posts --from-beginning
```

The current local deployment demonstrates service separation, Kafka-based messaging, PostgreSQL persistence, a storage API boundary, and a dashboard that reads trend data through HTTP.
