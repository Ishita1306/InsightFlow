#!/usr/bin/env bash
# Kosvio Production Deployment Script for Google Cloud Run
# Exit immediately if a command exits with a non-zero status
set -e

# Configuration variables - update these as needed
PROJECT_ID="your-gcp-project-id"
REGION="us-central1"
SERVICE_NAME="kosvio"
CLOUDSQL_INSTANCE="your-gcp-project-id:us-central1:your-mysql-instance-name"

echo "=========================================================="
echo " Starting Kosvio deployment to Google Cloud Run..."
echo "=========================================================="

# 1. Project check
if [[ "$PROJECT_ID" == "your-gcp-project-id" ]]; then
    echo "ERROR: Please edit this script and configure your actual PROJECT_ID, REGION, and CLOUDSQL_INSTANCE variables."
    exit 1
fi

# Ensure user is authenticated and project is set
echo "Configuring gcloud project to: $PROJECT_ID..."
gcloud config set project "$PROJECT_ID"

# 2. Check for encryption key
if [[ -z "$KOSVIO_DECRYPT_KEY" ]]; then
    echo "Enter your KOSVIO_DECRYPT_KEY (encryption key used for .env.enc):"
    read -r -s KOSVIO_DECRYPT_KEY
    if [[ -z "$KOSVIO_DECRYPT_KEY" ]]; then
        echo "ERROR: KOSVIO_DECRYPT_KEY is required to start the application."
        exit 1
    fi
fi

# 3. Submit build to Google Cloud Build
echo "Building container image using Google Cloud Build..."
gcloud builds submit --tag "gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

# 4. Deploy to Google Cloud Run
echo "Deploying to Google Cloud Run (max 1 instance constraint)..."
gcloud run deploy "$SERVICE_NAME" \
  --image "gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest" \
  --platform managed \
  --region "$REGION" \
  --allow-unauthenticated \
  --max-instances 1 \
  --add-cloudsql-instances "$CLOUDSQL_INSTANCE" \
  --set-env-vars "KOSVIO_DECRYPT_KEY=${KOSVIO_DECRYPT_KEY},MYSQL_UNIX_SOCKET=/cloudsql/${CLOUDSQL_INSTANCE}"

echo "=========================================================="
echo " Kosvio has been successfully deployed!"
echo "=========================================================="
