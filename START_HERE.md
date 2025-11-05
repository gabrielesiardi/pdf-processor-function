# 🚀 Deployment Steps - Start Here!

## Prerequisites Check ✓

Before you start, make sure you have:
- [ ] Azure account with active subscription
- [ ] Azure CLI installed (`az --version` to check)
- [ ] Git installed
- [ ] Python 3.11+ installed
- [ ] Azure Functions Core Tools installed (`func --version` to check)

**Install missing tools:**
- Azure CLI: https://docs.microsoft.com/cli/azure/install-azure-cli
- Functions Core Tools: https://docs.microsoft.com/azure/azure-functions/functions-run-local

---

## 🎯 Quick Deploy (5 minutes)

### Step 1: Get Your Credentials

You need:
1. **Mistral API Key** - Get from Azure Portal → Your Mistral AI Resource
2. **Mistral Base URL** - Format: `https://your-resource.services.ai.azure.com`

### Step 2: Choose Your Deployment Method

#### 🟢 Method A: Automated Script (Easiest)

```bash
cd azure-pdf-function
./deploy.sh
```

Follow the prompts. The script will:
- Create all Azure resources
- Configure environment variables
- Deploy the function
- Give you the URL and key

**Done! Skip to Step 3.**

---

#### 🟡 Method B: GitHub Actions (Best for CI/CD)

1. **Push to GitHub:**
   ```bash
   cd azure-pdf-function
   ./push-to-github.sh
   ```

2. **Create Function App in Azure:**
   ```bash
   # Set your variables
   export RG_NAME="my-pdf-function-rg"
   export FUNCTION_NAME="my-pdf-processor"
   export LOCATION="eastus"
   export STORAGE_NAME="mypdfstore$(date +%s)"

   # Login to Azure
   az login

   # Create resource group
   az group create --name $RG_NAME --location $LOCATION

   # Create storage account
   az storage account create \
     --name $STORAGE_NAME \
     --resource-group $RG_NAME \
     --location $LOCATION \
     --sku Standard_LRS

   # Create function app
   az functionapp create \
     --resource-group $RG_NAME \
     --consumption-plan-location $LOCATION \
     --runtime python \
     --runtime-version 3.11 \
     --functions-version 4 \
     --name $FUNCTION_NAME \
     --storage-account $STORAGE_NAME \
     --os-type Linux
   ```

3. **Get Publish Profile:**
   ```bash
   az functionapp deployment list-publishing-profiles \
     --name $FUNCTION_NAME \
     --resource-group $RG_NAME \
     --xml > publish-profile.xml

   # Display the content
   cat publish-profile.xml
   ```

4. **Add to GitHub Secrets:**
   - Go to your GitHub repo
   - Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`
   - Value: Paste the entire XML content
   - Save

5. **Update Workflow:**
   Edit `.github/workflows/deploy.yml`:
   ```yaml
   env:
     AZURE_FUNCTIONAPP_NAME: 'my-pdf-processor'  # Your function name here
   ```

6. **Set Environment Variables in Azure:**
   ```bash
   az functionapp config appsettings set \
     --name $FUNCTION_NAME \
     --resource-group $RG_NAME \
     --settings \
       MISTRAL_API_KEY="your_key_here" \
       MISTRAL_BASE_URL="https://your-resource.services.ai.azure.com"
   ```

7. **Commit and Push:**
   ```bash
   git add .
   git commit -m "Configure deployment"
   git push origin main
   ```

   GitHub Actions will automatically deploy!

---

#### 🟠 Method C: Manual Deploy

```bash
cd azure-pdf-function

# Login to Azure
az login

# Create function app (use commands from Method B above)

# Set environment variables (use command from Method B above)

# Deploy
func azure functionapp publish YOUR_FUNCTION_NAME --python
```

---

### Step 3: Get Your Function URL and Key

```bash
# Get URL
az functionapp function show \
  --name YOUR_FUNCTION_NAME \
  --resource-group YOUR_RESOURCE_GROUP \
  --function-name ProcessPDF \
  --query invokeUrlTemplate -o tsv

# Get Key
az functionapp keys list \
  --name YOUR_FUNCTION_NAME \
  --resource-group YOUR_RESOURCE_GROUP \
  --query functionKeys.default -o tsv
```

Save these! You'll need them to call your function.

---

## 🧪 Testing Your Function

### Test with Sample Request

```bash
# Create a test PDF (base64 encoded)
echo "Sample PDF content" > test.txt
BASE64_PDF=$(base64 -w 0 test.txt)

# Call your function
curl -X POST 'YOUR_FUNCTION_URL?code=YOUR_FUNCTION_KEY' \
  -H 'Content-Type: application/json' \
  -d "{
    \"pdf_base64\": \"$BASE64_PDF\",
    \"prompt\": \"Extract all text and return as JSON\"
  }"
```

### Or use the test script:

```bash
python test_function.py azure \
  "YOUR_FUNCTION_URL" \
  "YOUR_FUNCTION_KEY" \
  your-actual-pdf.pdf \
  "Extract invoice data as JSON"
```

---

## 📊 Monitor Your Function

### View Logs in Real-Time

```bash
func azure functionapp logstream YOUR_FUNCTION_NAME
```

### Or in Azure Portal:
1. Go to Azure Portal
2. Find your Function App
3. Click "Monitor" → "Logs"
4. Select "ProcessPDF" function

---

## 🐛 Troubleshooting

### "401 Unauthorized" from Mistral
- Check `MISTRAL_API_KEY` is set correctly
- Verify the key hasn't expired
- Try regenerating the key in Azure Portal

### "Function not found"
- Wait 1-2 minutes after deployment
- Run: `az functionapp restart --name YOUR_FUNCTION_NAME --resource-group YOUR_RG`

### "OCR failed"
- Check PDF is valid base64
- Ensure PDF isn't corrupted
- Try with a smaller PDF first

### Timeout errors
- Increase timeout in `host.json`:
  ```json
  {
    "functionTimeout": "00:10:00"
  }
  ```
- Redeploy after change

---

## 🎉 Success Checklist

- [ ] Function deployed to Azure
- [ ] Environment variables configured
- [ ] Successfully tested with sample PDF
- [ ] Received structured JSON response
- [ ] Logs visible in Azure Portal

---

## 📝 Next Steps

1. **Integrate into your app:** Use the function URL in your application
2. **Set up monitoring:** Configure Application Insights
3. **Add authentication:** Consider API Management for additional security
4. **Scale if needed:** Monitor usage and upgrade plan if necessary

---

## 💡 Pro Tips

- **Base64 Encoding:** Most languages have built-in base64 encoding:
  - Python: `base64.b64encode(pdf_bytes).decode('utf-8')`
  - JavaScript: `Buffer.from(pdfBytes).toString('base64')`
  - C#: `Convert.ToBase64String(pdfBytes)`

- **Prompt Engineering:** Be specific! Better prompts = better results:
  - ❌ "Extract data"
  - ✅ "Extract vendor name, invoice date, total amount, and line items (with description, quantity, unit price). Return as JSON."

- **Cost Optimization:**
  - Use smaller PDFs when possible
  - Cache results if you process the same PDF multiple times
  - Consider batching requests

---

## 🆘 Need Help?

1. Check the full [README.md](README.md) for detailed docs
2. Review [CHANGES.md](CHANGES.md) to see what changed
3. Look at [QUICKSTART.md](QUICKSTART.md) for quick reference
4. Open an issue on GitHub

---

## 🎊 You're All Set!

Your Azure Function is now ready to process PDFs and extract structured data using Mistral AI!

Test it, integrate it, and start automating your document processing workflows.
