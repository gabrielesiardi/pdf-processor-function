# Azure PDF Processing Function

Streamlined Azure Function that uses Mistral AI to extract and structure data from PDFs.

## What's Changed

### Removed:
- ❌ SharePoint integration (download_pdf_from_sharepoint)
- ❌ Azure Blob Storage dependency
- ❌ Session management
- ❌ File upload/download logic
- ❌ Complex URL parsing

### Simplified:
- ✅ Direct PDF base64 input
- ✅ Custom prompt support
- ✅ Single responsibility per method
- ✅ Better error handling
- ✅ Cleaner response format

## API Usage

**Endpoint:** `POST /api/process-pdf`

**Request Body:**
```json
{
  "pdf_base64": "JVBERi0xLjQKJeLjz9MK...",
  "prompt": "Extract all invoice data including vendor name, date, total amount, and line items. Return as JSON."
}
```

**Success Response:**
```json
{
  "status": "success",
  "data": {
    "vendor_name": "Acme Corp",
    "date": "2025-01-15",
    "total_amount": 1250.00,
    "line_items": [...]
  },
  "metadata": {
    "characters_extracted": 1523,
    "processing_timestamp": "2025-11-05T10:30:00.000000"
  }
}
```

## Deployment Guide

### Prerequisites
1. Azure account with active subscription
2. Azure Functions Core Tools installed
3. Azure CLI installed and logged in
4. Mistral AI resource in Azure

### Option 1: Deploy from Local

```bash
# 1. Navigate to the function directory
cd azure-pdf-function

# 2. Create a Function App in Azure
az functionapp create \
  --resource-group <YOUR_RESOURCE_GROUP> \
  --consumption-plan-location <YOUR_REGION> \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name <YOUR_FUNCTION_APP_NAME> \
  --storage-account <YOUR_STORAGE_ACCOUNT> \
  --os-type Linux

# 3. Configure environment variables
az functionapp config appsettings set \
  --name <YOUR_FUNCTION_APP_NAME> \
  --resource-group <YOUR_RESOURCE_GROUP> \
  --settings \
    MISTRAL_API_KEY="<YOUR_MISTRAL_KEY>" \
    MISTRAL_BASE_URL="<YOUR_MISTRAL_ENDPOINT>"

# 4. Deploy the function
func azure functionapp publish <YOUR_FUNCTION_APP_NAME>
```

### Option 2: Deploy from GitHub

```bash
# 1. Push code to GitHub
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main

# 2. Create Function App (if not exists)
az functionapp create \
  --resource-group <YOUR_RESOURCE_GROUP> \
  --consumption-plan-location <YOUR_REGION> \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name <YOUR_FUNCTION_APP_NAME> \
  --storage-account <YOUR_STORAGE_ACCOUNT> \
  --os-type Linux

# 3. Configure GitHub deployment
az functionapp deployment source config \
  --name <YOUR_FUNCTION_APP_NAME> \
  --resource-group <YOUR_RESOURCE_GROUP> \
  --repo-url <YOUR_GITHUB_REPO_URL> \
  --branch main \
  --manual-integration

# 4. Set environment variables
az functionapp config appsettings set \
  --name <YOUR_FUNCTION_APP_NAME> \
  --resource-group <YOUR_RESOURCE_GROUP> \
  --settings \
    MISTRAL_API_KEY="<YOUR_MISTRAL_KEY>" \
    MISTRAL_BASE_URL="<YOUR_MISTRAL_ENDPOINT>"
```

### Option 3: GitHub Actions (Recommended)

1. **Get Publish Profile:**
```bash
az functionapp deployment list-publishing-profiles \
  --name <YOUR_FUNCTION_APP_NAME> \
  --resource-group <YOUR_RESOURCE_GROUP> \
  --xml
```

2. **Add GitHub Secret:**
   - Go to your GitHub repo → Settings → Secrets → Actions
   - Create new secret: `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`
   - Paste the XML content from step 1

3. **GitHub Actions will automatically deploy on push to main**

## Testing

### Local Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Start function locally
func start

# Test with curl
curl -X POST http://localhost:7071/api/process-pdf \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_base64": "<BASE64_PDF_DATA>",
    "prompt": "Extract invoice data as JSON"
  }'
```

### Testing in Azure
```bash
# Get function URL
FUNCTION_URL=$(az functionapp function show \
  --name <YOUR_FUNCTION_APP_NAME> \
  --resource-group <YOUR_RESOURCE_GROUP> \
  --function-name ProcessPDF \
  --query invokeUrlTemplate -o tsv)

# Get function key
FUNCTION_KEY=$(az functionapp keys list \
  --name <YOUR_FUNCTION_APP_NAME> \
  --resource-group <YOUR_RESOURCE_GROUP> \
  --query functionKeys.default -o tsv)

# Test
curl -X POST "${FUNCTION_URL}?code=${FUNCTION_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_base64": "<BASE64_PDF_DATA>",
    "prompt": "Extract all data as JSON"
  }'
```

## Monitoring

View logs in real-time:
```bash
func azure functionapp logstream <YOUR_FUNCTION_APP_NAME>
```

Or in Azure Portal:
- Navigate to your Function App
- Go to "Monitor" → "Logs"
- Select "ProcessPDF" function

## Configuration

### Environment Variables
- `MISTRAL_API_KEY`: Your Mistral API key
- `MISTRAL_BASE_URL`: Mistral endpoint URL (e.g., `https://your-resource.services.ai.azure.com`)

### Timeout Settings
Current timeout: 5 minutes (configured in `host.json`)

To change:
```json
{
  "functionTimeout": "00:10:00"  // 10 minutes
}
```

## Troubleshooting

### Common Issues

1. **"OCR failed: 401"**
   - Check `MISTRAL_API_KEY` is correctly set
   - Verify key has not expired

2. **"No pages found in OCR response"**
   - PDF might be corrupted
   - PDF might be image-based without text

3. **Timeout errors**
   - Increase `functionTimeout` in host.json
   - Consider chunking large PDFs

4. **"Could not parse JSON from response"**
   - Check your prompt requests JSON output
   - Try adding "Return your response as valid JSON" to prompt

## Performance Tips

1. Keep PDFs under 10MB for best performance
2. Use specific, clear prompts for better extraction
3. Consider caching results for repeated queries
4. Monitor function execution times in Azure Portal

## Cost Optimization

- Use Consumption plan for variable workloads
- Consider Premium plan if you need:
  - VNET integration
  - Longer execution times
  - Always-on instances
