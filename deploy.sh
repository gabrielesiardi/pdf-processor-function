#!/bin/bash

# Azure Function Deployment Script
# This script helps deploy the function to Azure

set -e

echo "========================================"
echo "Azure PDF Function - Deployment Script"
echo "========================================"
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "Error: Azure CLI is not installed"
    echo "Install from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in
if ! az account show &> /dev/null; then
    echo "You need to login to Azure..."
    az login
fi

# Get parameters
read -p "Enter Resource Group name: " RESOURCE_GROUP
read -p "Enter Function App name: " FUNCTION_APP_NAME
read -p "Enter Azure Region (e.g., eastus): " LOCATION
read -p "Enter Storage Account name: " STORAGE_ACCOUNT

# Get Mistral credentials
echo ""
echo "Mistral AI Configuration:"
read -p "Enter Mistral API Key: " MISTRAL_API_KEY
read -p "Enter Mistral Base URL: " MISTRAL_BASE_URL

echo ""
echo "Configuration Summary:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Function App: $FUNCTION_APP_NAME"
echo "  Location: $LOCATION"
echo "  Storage: $STORAGE_ACCOUNT"
echo ""
read -p "Proceed with deployment? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled"
    exit 0
fi

# Create resource group if doesn't exist
echo ""
echo "Step 1: Creating resource group..."
az group create --name "$RESOURCE_GROUP" --location "$LOCATION" || true

# Create storage account if doesn't exist
echo ""
echo "Step 2: Creating storage account..."
az storage account create \
  --name "$STORAGE_ACCOUNT" \
  --location "$LOCATION" \
  --resource-group "$RESOURCE_GROUP" \
  --sku Standard_LRS \
  --allow-blob-public-access false || echo "Storage account may already exist"

# Create function app
echo ""
echo "Step 3: Creating Function App..."
az functionapp create \
  --resource-group "$RESOURCE_GROUP" \
  --consumption-plan-location "$LOCATION" \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name "$FUNCTION_APP_NAME" \
  --storage-account "$STORAGE_ACCOUNT" \
  --os-type Linux

# Configure app settings
echo ""
echo "Step 4: Configuring environment variables..."
az functionapp config appsettings set \
  --name "$FUNCTION_APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --settings \
    "MISTRAL_API_KEY=$MISTRAL_API_KEY" \
    "MISTRAL_BASE_URL=$MISTRAL_BASE_URL"

# Deploy function
echo ""
echo "Step 5: Deploying function code..."
func azure functionapp publish "$FUNCTION_APP_NAME" --python

# Get function URL and key
echo ""
echo "Step 6: Retrieving function details..."
FUNCTION_URL=$(az functionapp function show \
  --name "$FUNCTION_APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --function-name ProcessPDF \
  --query invokeUrlTemplate -o tsv)

FUNCTION_KEY=$(az functionapp keys list \
  --name "$FUNCTION_APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query functionKeys.default -o tsv)

echo ""
echo "========================================"
echo "Deployment Complete!"
echo "========================================"
echo ""
echo "Function URL: $FUNCTION_URL"
echo "Function Key: $FUNCTION_KEY"
echo ""
echo "Test your function with:"
echo "curl -X POST '${FUNCTION_URL}?code=${FUNCTION_KEY}' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"pdf_base64\": \"<YOUR_BASE64_PDF>\", \"prompt\": \"Extract data as JSON\"}'"
echo ""
echo "Monitor logs with:"
echo "func azure functionapp logstream $FUNCTION_APP_NAME"
echo ""
