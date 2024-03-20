
# Mares API

Welcome to the Mares API, a cutting-edge recommendation system designed to provide personalized suggestions to users. This document outlines how to set up and run the API locally, using Docker, and deploy it to Google Cloud Platform (GCP).

## Requirements

Ensure you have the following installed on your system:
- Python 3.10.6 or higher
- pip
- Docker
- gcloud (for GCP deployment)

## Setup Instructions

### 1. Install Dependencies

To install necessary Python packages, run:

```bash
make install
```

This command updates pip and installs dependencies listed in `requirements.txt`.

### 2. Running the API Locally

To start the API server on your local machine, run:

```bash
make run_api
```

This will launch the API at `http://0.0.0.0:8080`. The `--reload` flag enables hot reloading, allowing you to see changes in real-time without restarting the server.

### 3. Docker Setup

#### Building the Docker Image

To build a Docker image for the Mares API, run:

```bash
make docker_build
```

#### Running the Docker Container

After building the image, start the container with:

```bash
make docker_run
```

This command runs the API inside a Docker container, mapping the container's port 8080 to port 8080 on your host.

### 4. Deploying to Google Cloud Platform (GCP)

#### Deploying the Service

To deploy the API to GCP, run:

```bash
make gcp_deploy
```

Ensure you have configured your `gcloud` CLI with appropriate permissions and settings before running this command.

#### Deleting the Service

To remove the deployed service from GCP, run:

```bash
make gcp_delete
```

## Usage

After starting the API, visit `http://localhost:8080/docs` to view the interactive API documentation and test endpoints.

## License

Specify your license here or indicate if the software is open-source.

