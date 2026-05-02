# Real Time Social Media Trend Analysis

## A CSC 258 Distributed Systems Project

This project is a real time social media trend detection system. It collects live posts from the website Bluesky and detects trending topics/words.

| Team Member           | Role                                        |
| --------------------- | ------------------------------------------- |
| **Abdurrehman Aslam** | Code Developer and Survey Paper Reviewer    |
| **Abubaker Sayyed**   | Contributed to Survey Paper and Code Review |
| **Fidel Serrano**     | Code Developer and Survey Paper Reviewer    |
| **Soulius Jones**     | Survey Paper Writer and Code Reviewer       |

## Code Structure

https://github.com/fserranox9f/CSC_258_Project.git

The code is structured into five main components where each component has its own subdirectory.
The flow of the program is

ingestion -> broker -> processing -> storage -> dashboard

The ingestion service opens and keeps a continous websocket connectioon to BlueSky servers. It pushes the post read from Bluesky to Kafka Servers. The messages are normalized into a JOSN type.

The broker service (Kafka) works as a communication layer between the ingestion and processing service. Kafka is in a Docker container and the compose file in the root directory builds an image so services can connect to it locally at port 9092.

The processing service reads post from the Kafka server and tries to detect/count the most commonly found words in a post. It saves the results to the storage service.

The storage service holds the data produced by the processing service and then is read from the dashboard service. Currently, the data is being saved locally.

The dashboard service displays the resulting trends of most popular words in a local webpage.

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
        writer.py
        logs
            post_dump.json
    processing
        consumer.py
        config.py
        main.py
        processor.py
    storage
        config.py
        trend_save.py
        logs
            trends.json
            example_posts.json
    dashboard
        index.html
        styles.css
        script.js
```

## Dependencies and Environment

The project currently uses Python, Docker, Kafka, and Javascript.

Python dependencies are listed in `requirements.txt`

Docker is also needed to run the Kafka broker image.

- Operating system: Windows
- Shell: PowerShell
- Python runtime: Python 3.11
- Container runtime: Docker Desktop
- Message broker: Apache Kafka running in Docker
- Kafka port: localhost:9092
- Dashboard server: Python local HTTP server http://localhost:8000/services/dashboard/index.html

## How to Run

The following steps and commands were executed at the root level of the project. Since all services executed here run constiounusly, each command is ran in different terminal windows.

1. Build and run Docker container for Kafka broker

```powershell
    docker compose up -d broker
```

2. Run the ingestion service.

```powershell
    python -m services.ingestion.main
```

3. Run the processing service.

```powershell
    python -m services.processing.main
```

4. Run the local http server

```powershell
    python -m http.server 8000
```

5. See the local dashboard in a web browser
   http://localhost:8000/services/dashboard/index.html

Other

See messages in Kafka

```powershell
    docker exec -it broker /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic BlueSky_socialmedia_posts --from-beginning
```

Install Python dependencies

```powershell
    pip install -r requirements.txt
```
