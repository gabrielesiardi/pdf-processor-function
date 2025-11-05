#!/usr/bin/env python3
"""
Test script for the Azure PDF Processing Function
"""

import base64
import json
import requests
import sys
from pathlib import Path

def encode_pdf(pdf_path: str) -> str:
    """Encode PDF file to base64"""
    with open(pdf_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def test_local(pdf_path: str, prompt: str):
    """Test function running locally"""
    url = "http://localhost:7071/api/process-pdf"
    
    pdf_base64 = encode_pdf(pdf_path)
    
    payload = {
        "pdf_base64": pdf_base64,
        "prompt": prompt
    }
    
    print(f"Testing local function at {url}")
    print(f"PDF: {pdf_path}")
    print(f"Prompt: {prompt}")
    print("-" * 60)
    
    response = requests.post(url, json=payload)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))

def test_azure(function_url: str, function_key: str, pdf_path: str, prompt: str):
    """Test function deployed in Azure"""
    url = f"{function_url}?code={function_key}"
    
    pdf_base64 = encode_pdf(pdf_path)
    
    payload = {
        "pdf_base64": pdf_base64,
        "prompt": prompt
    }
    
    print(f"Testing Azure function")
    print(f"PDF: {pdf_path}")
    print(f"Prompt: {prompt}")
    print("-" * 60)
    
    response = requests.post(url, json=payload)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  Local:  python test_function.py local <pdf_path> <prompt>")
        print("  Azure:  python test_function.py azure <function_url> <function_key> <pdf_path> <prompt>")
        sys.exit(1)
    
    mode = sys.argv[1]
    
    if mode == "local":
        if len(sys.argv) < 4:
            print("Error: Missing arguments for local test")
            print("Usage: python test_function.py local <pdf_path> <prompt>")
            sys.exit(1)
        
        pdf_path = sys.argv[2]
        prompt = " ".join(sys.argv[3:])
        test_local(pdf_path, prompt)
        
    elif mode == "azure":
        if len(sys.argv) < 6:
            print("Error: Missing arguments for Azure test")
            print("Usage: python test_function.py azure <function_url> <function_key> <pdf_path> <prompt>")
            sys.exit(1)
        
        function_url = sys.argv[2]
        function_key = sys.argv[3]
        pdf_path = sys.argv[4]
        prompt = " ".join(sys.argv[5:])
        test_azure(function_url, function_key, pdf_path, prompt)
        
    else:
        print(f"Error: Unknown mode '{mode}'")
        print("Use 'local' or 'azure'")
        sys.exit(1)
