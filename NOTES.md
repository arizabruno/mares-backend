
# Mares API

Welcome to the Mares API, a recommendation system designed to provide personalized suggestions to users. This document outlines how to set up and run the API locally, using Docker, and deploy it to AWS.

## Requirements
- Python 3.10.6 or higher
- pip
- Docker
- Terraform
- AWS Account
- AWS CLI

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

### 4. Deploying to AWS

#### 1. Inititalizing Terraform

```bash
make init_cloud_infra
```

#### 2. Upload container to Registry

```bash
make upload_container_to_registry
```

#### 3. Deploying container

```bash
make apply_cloud_infra
```

#### 4. Destroying resources

```bash
make detroy_cloud_infra
```
