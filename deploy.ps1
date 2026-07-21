# Kosvio Production Deployment Script for Google Cloud Run (PowerShell)
$ErrorActionPreference = "Stop"

# Configuration variables - update these as needed
$PROJECT_ID = "your-gcp-project-id"
$REGION = "us-central1"
$SERVICE_NAME = "kosvio"
$CLOUDSQL_INSTANCE = "your-gcp-project-id:us-central1:your-mysql-instance-name"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Starting Kosvio deployment to Google Cloud Run..." -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Project check
if ($PROJECT_ID -eq "your-gcp-project-id") {
    Write-Error "Please edit this script and configure your actual PROJECT_ID, REGION, and CLOUDSQL_INSTANCE variables."
    exit 1
}

# Ensure user is authenticated and project is set
Write-Host "Configuring gcloud project to: $PROJECT_ID..." -ForegroundColor Green
gcloud config set project $PROJECT_ID

# 2. Check for encryption key
$decryptKey = $env:KOSVIO_DECRYPT_KEY
if ([string]::IsNullOrEmpty($decryptKey)) {
    $decryptKey = Read-Host -Prompt "Enter your KOSVIO_DECRYPT_KEY (encryption key used for .env.enc) (Input is hidden)" -AsSecureString
    $bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($decryptKey)
    $decryptKey = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
}

if ([string]::IsNullOrEmpty($decryptKey)) {
    Write-Error "KOSVIO_DECRYPT_KEY is required to start the application."
    exit 1
}

# 3. Submit build to Google Cloud Build
Write-Host "Building container image using Google Cloud Build..." -ForegroundColor Green
gcloud builds submit --tag "gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

# 4. Deploy to Google Cloud Run
Write-Host "Deploying to Google Cloud Run (max 1 instance constraint)..." -ForegroundColor Green
gcloud run deploy $SERVICE_NAME `
  --image "gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest" `
  --platform managed `
  --region $REGION `
  --allow-unauthenticated `
  --max-instances 1 `
  --add-cloudsql-instances $CLOUDSQL_INSTANCE `
  --set-env-vars "KOSVIO_DECRYPT_KEY=${decryptKey},MYSQL_UNIX_SOCKET=/cloudsql/${CLOUDSQL_INSTANCE}"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Kosvio has been successfully deployed!" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
