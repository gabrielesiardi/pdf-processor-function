# Quick Start Guide

## Overview
This is a streamlined Azure Function that processes PDFs using Mistral AI. Send a PDF (as base64) and a prompt, get structured JSON back.

## Key Improvements from Original Code

✅ **Removed unnecessary dependencies:**
- SharePoint integration
- Blob Storage
- Complex session management

✅ **Simplified input:**
- Direct base64 PDF input (no file upload needed)
- Custom prompt per request

✅ **Cleaner code:**
- Single responsibility methods
- Better error handling
- More maintainable

## Deployment Options

### Option 1: Quick Deploy (Recommended)
```bash
# Run the automated deployment script
./deploy.sh
```

This will:
1. Create all necessary Azure resources
2. Configure environment variables
3. Deploy the function
4. Give you the function URL and key

### Option 2: GitHub Actions Auto-Deploy

1. **Update workflow file:**
   Edit `.github/workflows/deploy.yml` and change:
   ```yaml
   AZURE_FUNCTIONAPP_NAME: 'your-actual-function-app-name'
   ```

2. **Get publish profile:**
   ```bash
   az functionapp deployment list-publishing-profiles \
     --name YOUR_FUNCTION_APP_NAME \
     --resource-group YOUR_RESOURCE_GROUP \
     --xml
   ```

3. **Add to GitHub:**
   - Go to: Repository → Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`
   - Value: Paste the XML from step 2
   - Save

4. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Deploy Azure Function"
   git push origin main
   ```

The function will automatically deploy on every push to main!

### Option 3: Manual Deploy

```bash
# 1. Create Function App
az functionapp create \
  --resource-group YOUR_RG \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name YOUR_FUNCTION_NAME \
  --storage-account YOUR_STORAGE \
  --os-type Linux

# 2. Set environment variables
az functionapp config appsettings set \
  --name YOUR_FUNCTION_NAME \
  --resource-group YOUR_RG \
  --settings \
    MISTRAL_API_KEY="your_key" \
    MISTRAL_BASE_URL="https://your-endpoint.services.ai.azure.com"

# 3. Deploy
func azure functionapp publish YOUR_FUNCTION_NAME
```

## Testing

### Test Locally
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Update local.settings.json with your credentials

# 3. Start function
func start

# 4. Test with provided script
python test_function.py local sample.pdf "Extract invoice data as JSON"
```

### Test in Azure
```bash
python test_function.py azure \
  "https://your-function.azurewebsites.net/api/process-pdf" \
  "YOUR_FUNCTION_KEY" \
  sample.pdf \
  "Extract all data as JSON"
```

## Usage Example

### Request
```bash
curl -X POST 'https://your-function.azurewebsites.net/api/process-pdf?code=YOUR_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "pdf_base64": "JVBERi0xLjQKJe...",
    "prompt": "Extract invoice data including vendor, date, total, and line items. Return as JSON."
  }'
```

### Response
```json
{
  "status": "success",
  "data": {
    "vendor": "Acme Corp",
    "date": "2025-01-15",
    "total": 1250.00,
    "line_items": [
      {"description": "Widget A", "quantity": 10, "price": 50.00},
      {"description": "Widget B", "quantity": 5, "price": 150.00}
    ]
  },
  "metadata": {
    "characters_extracted": 1523,
    "processing_timestamp": "2025-11-05T10:30:00.000000"
  }
}
```

## Next Steps

1. **Deploy to Azure** using one of the methods above
2. **Test the function** with your PDF files
3. **Integrate** into your application workflow
4. **Monitor** via Azure Portal or `func azure functionapp logstream`

## Need Help?

- Check the full README.md for detailed documentation
- Review Azure Function logs in the portal
- Ensure Mistral API credentials are correct
- Verify PDF is properly base64 encoded

## Cost Estimate

- **Azure Function (Consumption):** ~$0.20 per million requests
- **Mistral API:** Pay-per-use (check Azure pricing)
- **Storage:** Minimal (~$0.02/GB per month)

Total: Very low for typical usage patterns.
