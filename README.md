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

## Deployment Options

This project now supports two deployment paths:

- Local Docker Compose deployment for running everything on your machine.
- Google Cloud deployment with Cloud Build, Artifact Registry, and Google Kubernetes Engine.

For local Docker, see `How to Run`.

For Google Cloud through the browser UI and Cloud Shell, see `Google Cloud and GKE Deployment`.

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

## Google Cloud and GKE Deployment

The project can also run on Google Kubernetes Engine. The easiest browser-based workflow is to use the Google Cloud Console for setup and Cloud Shell for commands.

### 1. Create Google Cloud resources in the browser

In the Google Cloud Console:

1. Create or select a project.
2. Make sure billing is enabled.
3. Enable these APIs:
   - Kubernetes Engine API
   - Artifact Registry API
   - Cloud Build API

Create the Docker image repository:

1. Open Artifact Registry.
2. Click Repositories.
3. Click Create Repository.
4. Name it `csc258`.
5. Set Format to Docker.
6. Set Location type to Multi-region.
7. Set Location to `us`.
8. Click Create.

Create the GKE cluster:

1. Open Kubernetes Engine.
2. Click Create.
3. Choose Autopilot.
4. Name it `csc258-cluster`.
5. Set Region to `us-central1`.
6. Keep the defaults and click Create.

### 2. Upload or clone the repo in Cloud Shell

Open Cloud Shell from the top-right terminal icon in Google Cloud Console. Put this project in Cloud Shell by cloning your GitHub repo or uploading the project files.

From the project root, set your project:

```bash
gcloud config set project YOUR_PROJECT_ID
```

Edit `k8s/base/kustomization.yaml` and replace `PROJECT_ID` with your real Google Cloud project ID.

Edit `k8s/base/secret.example.yaml` and replace `change-me-before-deploying` with a real database password.

### 3. Build and push the Docker image

```bash
gcloud builds submit --config cloudbuild.yaml
```

This builds the shared Python image and pushes it to Artifact Registry as:

```text
us-docker.pkg.dev/YOUR_PROJECT_ID/csc258/trend-system:latest
```

### 4. Connect Cloud Shell to the GKE cluster

```bash
gcloud container clusters get-credentials csc258-cluster --region us-central1
```

### 5. Deploy the Kubernetes resources

```bash
kubectl apply -k k8s/base
```

Check the pods:

```bash
kubectl get pods -n csc258
```

Check the public service IPs:

```bash
kubectl get services -n csc258
```

Wait until both `storage` and `dashboard` show external IP addresses.

### 6. Point the dashboard at the storage API

After the `storage` service has an external IP, update the dashboard config:

```bash
kubectl create configmap dashboard-config \
  --namespace csc258 \
  --from-literal=config.js='window.DASHBOARD_API_BASE_URL = "http://STORAGE_EXTERNAL_IP:5001";' \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl rollout restart deployment/dashboard -n csc258
```

Replace `STORAGE_EXTERNAL_IP` with the external IP from `kubectl get services -n csc258`.

Open the dashboard:

```text
http://DASHBOARD_EXTERNAL_IP:8000/dashboard/index.html
```

Replace `DASHBOARD_EXTERNAL_IP` with the dashboard service external IP.

Useful GKE commands:

```bash
kubectl logs -n csc258 deployment/ingestion --tail=100
kubectl logs -n csc258 deployment/processing --tail=100
kubectl logs -n csc258 deployment/storage --tail=100
kubectl rollout status -n csc258 deployment/storage
kubectl delete -k k8s/base
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
