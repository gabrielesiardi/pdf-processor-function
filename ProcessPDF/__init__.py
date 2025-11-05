import azure.functions as func
import logging
import json
import os
import base64
import re
from typing import Dict, Any
from datetime import datetime

class MistralPDFProcessor:
    """Streamlined PDF processor using Mistral AI models"""
    
    def __init__(self):
        self.api_key = os.environ['MISTRAL_API_KEY']
        self.base_url = os.environ['MISTRAL_BASE_URL'].rstrip('/')
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

    def extract_text_from_pdf(self, pdf_base64: str) -> str:
        """Extract text from PDF using Mistral Document AI"""
        payload = {
            "model": "mistral-document-ai-2505",
            "document": {
                "type": "document_url",
                "document_url": f"data:application/pdf;base64,{pdf_base64}"
            },
            "include_image_base64": False
        }
        
        ocr_url = f"{self.base_url}/providers/mistral/azure/ocr"
        
        logging.info("Extracting text from PDF...")
        
        import requests
        response = requests.post(ocr_url, headers=self.headers, json=payload, timeout=120)
        
        if response.status_code != 200:
            raise Exception(f"OCR failed: {response.status_code} - {response.text}")
        
        ocr_data = response.json()
        
        if not ocr_data.get('pages'):
            raise Exception("No pages found in OCR response")
        
        # Combine all pages
        markdown_content = "\n\n".join(
            page.get('markdown', '') for page in ocr_data['pages']
        )
        
        logging.info(f"Extracted {len(markdown_content)} characters from {len(ocr_data['pages'])} pages")
        return markdown_content

    def extract_data_with_prompt(self, markdown_content: str, user_prompt: str) -> Dict[str, Any]:
        """Extract structured data using custom prompt"""
        payload = {
            "model": "mistral-small-2503",
            "messages": [
                {
                    "role": "user",
                    "content": f"{user_prompt}\n\nDocument content:\n{markdown_content}"
                }
            ],
            "max_tokens": 4096,
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }
        
        chat_url = f"{self.base_url}/models/chat/completions?api-version=2024-05-01-preview"
        
        logging.info("Extracting structured data...")
        
        import requests
        response = requests.post(chat_url, headers=self.headers, json=payload, timeout=90)
        
        if response.status_code != 200:
            raise Exception(f"Extraction failed: {response.status_code} - {response.text}")
        
        chat_response = response.json()
        content = chat_response['choices'][0]['message']['content']
        
        # Parse JSON response
        try:
            # Try direct JSON parse first
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to extract from markdown code block
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1).strip())
            raise Exception("Could not parse JSON from response")

    def process(self, pdf_base64: str, prompt: str) -> Dict[str, Any]:
        """Main processing pipeline"""
        try:
            # Step 1: Extract text from PDF
            markdown_text = self.extract_text_from_pdf(pdf_base64)
            
            # Step 2: Extract structured data using prompt
            structured_data = self.extract_data_with_prompt(markdown_text, prompt)
            
            return {
                "status": "success",
                "data": structured_data,
                "metadata": {
                    "characters_extracted": len(markdown_text),
                    "processing_timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logging.error(f"Processing failed: {str(e)}")
            raise


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Function entry point"""
    logging.info('PDF processing function triggered')
    
    try:
        # Parse request body
        req_body = req.get_json()
        
        if not req_body:
            return func.HttpResponse(
                json.dumps({"error": "Request body required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Validate required parameters
        pdf_data = req_body.get('pdf_base64')
        prompt = req_body.get('prompt')
        
        if not pdf_data or not prompt:
            return func.HttpResponse(
                json.dumps({
                    "error": "Missing required parameters",
                    "required": ["pdf_base64", "prompt"],
                    "received": list(req_body.keys())
                }),
                status_code=400,
                mimetype="application/json"
            )
        
        # Process PDF
        processor = MistralPDFProcessor()
        result = processor.process(pdf_data, prompt)
        
        return func.HttpResponse(
            json.dumps(result, indent=2, ensure_ascii=False),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Function execution failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }),
            status_code=500,
            mimetype="application/json"
        )
