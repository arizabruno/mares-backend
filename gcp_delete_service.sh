#!/bin/bash

SERVICE_NAME="api"
REGION="europe-west1"

gcloud run services delete $SERVICE_NAME --region $REGION --quiet
