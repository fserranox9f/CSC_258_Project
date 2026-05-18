#-----------------------------------------------------
# Shared Docker image for the cloud services.
#
#   -- Open Design --
#   The same image is used by storage, processing, ingestion, and dashboard.
#   Kubernetes decides which service runs by overriding the command.
#
#   -- Consistency --
#   The image installs the same Python dependencies used by Docker Compose.
#-----------------------------------------------------

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# install Python dependencies before copying source so rebuilds are faster
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy only the active services into the deployable image
COPY services ./services

# default command. GKE overrides this per service in k8s/base/app.yaml
CMD ["python", "-m", "services.storage.main"]
