import azure.functions as func
import logging
import json
import os
import requests
import base64
import re
from typing import Dict, Any
from azure.storage.blob import BlobServiceClient
from urllib.parse import unquote
from datetime import datetime

class AzurePDFProcessor:
    def __init__(self):
        self.azure_api_key = os.environ['MISTRAL_API_KEY']
        self.base_url = os.environ['MISTRAL_BASE_URL'].rstrip('/')
        self.storage_connection = os.environ['AZURE_STORAGE_CONNECTION_STRING']
        
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.azure_api_key}'
        })
        
        # Initialize blob client
        self.blob_service = BlobServiceClient.from_connection_string(self.storage_connection)

    def download_pdf_from_sharepoint(self, file_content_url: str, access_token: str) -> bytes:
        """Download PDF from SharePoint using content URL"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/octet-stream'
        }
        
        logging.info(f"Downloading PDF from: {file_content_url}")
        response = requests.get(file_content_url, headers=headers, timeout=60)
        
        if response.status_code != 200:
            raise Exception(f"Failed to download PDF: {response.status_code} - {response.text}")
        
        return response.content

    def extract_text_from_pdf_bytes(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Extract text from PDF using Mistral OCR"""
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        payload = {
            "model": "mistral-document-ai-2505",
            "document": {
                "type": "document_url",
                "document_url": f"data:application/pdf;base64,{pdf_base64}"
            },
            "include_image_base64": False  # Reduce response size
        }
        
        ocr_url = f"{self.base_url}/providers/mistral/azure/ocr"
        
        logging.info("Calling Mistral OCR API...")
        response = self.session.post(ocr_url, json=payload, timeout=120)
        
        if response.status_code != 200:
            raise Exception(f"OCR request failed: {response.status_code} - {response.text}")
        
        return response.json()

    def structure_text_to_json(self, markdown_content: str) -> Dict[str, Any]:
        """Convert markdown to structured JSON"""
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": f"Extract data from this text in a structured json format: {markdown_content}"
                }
            ],
            "max_tokens": 2048,
            "temperature": 0.1,
            "top_p": 0.9,
            "model": "mistral-small-2503"
        }
        
        chat_url = f"{self.base_url}/models/chat/completions?api-version=2024-05-01-preview"
        
        logging.info("Converting to structured JSON...")
        response = self.session.post(chat_url, json=payload, timeout=60)
        
        if response.status_code != 200:
            raise Exception(f"Chat request failed: {response.status_code} - {response.text}")
        
        return response.json()

    def extract_json_from_response(self, chat_response: Dict[str, Any]) -> Dict[str, Any]:
        """Extract clean JSON from chat response"""
        try:
            content = chat_response['choices'][0]['message']['content']
            
            # Look for JSON in markdown code blocks
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1).strip()
            else:
                json_str = content.strip()
            
            return json.loads(json_str)
            
        except (KeyError, json.JSONDecodeError, IndexError) as e:
            raise Exception(f"Failed to extract JSON: {str(e)}")

    def save_to_blob_storage(self, data: Dict[str, Any], filename: str) -> str:
        """Save processed data to blob storage"""
        container_name = "processed-pdfs"
        
        try:
            # Ensure container exists
            try:
                container_client = self.blob_service.get_container_client(container_name)
                container_client.create_container()
                logging.info(f"Created container: {container_name}")
            except Exception:
                pass  # Container likely already exists
            
            # Clean filename for blob name
            clean_filename = filename.replace('.pdf', '').replace(' ', '_')
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            blob_name = f"{clean_filename}_{timestamp}.json"
            
            # Upload data
            json_data = json.dumps(data, indent=2, ensure_ascii=False)
            blob_client = self.blob_service.get_blob_client(container_name, blob_name)
            blob_client.upload_blob(json_data, overwrite=True)
            
            blob_url = f"https://{self.blob_service.account_name}.blob.core.windows.net/{container_name}/{blob_name}"
            logging.info(f"Saved to blob: {blob_url}")
            
            return blob_url
            
        except Exception as e:
            raise Exception(f"Failed to save to blob storage: {str(e)}")

    def process_pdf(self, file_content_url: str, access_token: str, filename: str) -> Dict[str, Any]:
        """Main processing pipeline"""
        try:
            # Download PDF
            logging.info(f"Starting processing for: {filename}")
            pdf_bytes = self.download_pdf_from_sharepoint(file_content_url, access_token)
            logging.info(f"Downloaded PDF: {len(pdf_bytes)} bytes")
            
            # OCR extraction
            ocr_response = self.extract_text_from_pdf_bytes(pdf_bytes)
            
            if not ocr_response.get('pages'):
                raise Exception("No pages found in OCR response")
            
            markdown_content = ocr_response['pages'][0]['markdown']
            logging.info(f"Extracted {len(markdown_content)} characters")
            
            # Structure to JSON
            chat_response = self.structure_text_to_json(markdown_content)
            structured_data = self.extract_json_from_response(chat_response)
            
            # Save results
            blob_url = self.save_to_blob_storage(structured_data, filename)
            
            return {
                "status": "success",
                "filename": filename,
                "blob_url": blob_url,
                "pages_processed": len(ocr_response['pages']),
                "characters_extracted": len(markdown_content),
                "processing_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Processing failed for {filename}: {str(e)}")
            return {
                "status": "error",
                "filename": filename,
                "error": str(e),
                "processing_timestamp": datetime.utcnow().isoformat()
            }


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Function entry point"""
    logging.info('PDF processing function triggered')
    
    try:
        # Get request data
        req_body = req.get_json()
        
        if not req_body:
            return func.HttpResponse(
                json.dumps({"error": "Request body required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Extract Logic App parameters
        file_content_url = req_body.get('fileContentUrl')
        access_token = req_body.get('accessToken')
        filename = req_body.get('filename', 'unknown.pdf')
        
        if not file_content_url or not access_token:
            return func.HttpResponse(
                json.dumps({
                    "error": "Missing required parameters",
                    "required": ["fileContentUrl", "accessToken"]
                }),
                status_code=400,
                mimetype="application/json"
            )
        
        # Process PDF
        processor = AzurePDFProcessor()
        result = processor.process_pdf(file_content_url, access_token, filename)
        
        return func.HttpResponse(
            json.dumps(result, indent=2),
            status_code=200 if result['status'] == 'success' else 500,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Function execution failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "status": "error",
                "error": str(e),
                "processing_timestamp": datetime.utcnow().isoformat()
            }),
            status_code=500,
            mimetype="application/json"
        )
