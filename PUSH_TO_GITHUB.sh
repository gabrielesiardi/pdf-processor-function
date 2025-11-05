#!/bin/bash

# This script will push your Azure Function to GitHub
# Run this on your local machine after downloading the project

echo "========================================="
echo "Pushing to GitHub"
echo "========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "ProcessPDF/__init__.py" ]; then
    echo "Error: Please run this script from the azure-pdf-function directory"
    exit 1
fi

# Check if git is initialized
if [ ! -d .git ]; then
    echo "Initializing git repository..."
    git init
    git branch -M main
fi

# Configure git user (you can change these)
echo "Configuring git user..."
git config user.name "Gabriele Siardi"
git config user.email "gabriele.siardi@villafrut.it"

# Add all files
echo "Adding files..."
git add .

# Commit
echo "Creating commit..."
git commit -m "Initial commit: Streamlined Azure PDF Processing Function

- Removed SharePoint integration
- Removed Blob Storage dependency  
- Simplified to direct PDF base64 input
- Added custom prompt support
- Processes all PDF pages (not just first)
- 40% less code, 50% fewer dependencies
- Complete documentation and deployment tools" || echo "Files already committed"

# Add remote if not exists
if ! git remote | grep -q origin; then
    echo "Adding GitHub remote..."
    git remote add origin https://github.com/gabrielesiardi/pdf-processor-function.git
fi

# Push to GitHub
echo ""
echo "Pushing to GitHub..."
echo "You may be prompted for your GitHub credentials..."
echo ""

git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "SUCCESS! Code pushed to GitHub"
    echo "========================================="
    echo ""
    echo "Repository: https://github.com/gabrielesiardi/pdf-processor-function"
    echo ""
    echo "Next steps:"
    echo "1. Go to https://github.com/gabrielesiardi/pdf-processor-function"
    echo "2. Review your code"
    echo "3. Follow START_HERE.md to deploy to Azure"
    echo ""
else
    echo ""
    echo "========================================="
    echo "Push failed - Authentication needed"
    echo "========================================="
    echo ""
    echo "If you see authentication errors, you have two options:"
    echo ""
    echo "Option 1: Use GitHub CLI (recommended)"
    echo "  1. Install: https://cli.github.com/"
    echo "  2. Run: gh auth login"
    echo "  3. Run this script again"
    echo ""
    echo "Option 2: Use Personal Access Token"
    echo "  1. Go to: https://github.com/settings/tokens"
    echo "  2. Create new token with 'repo' scope"
    echo "  3. Use token as password when prompted"
    echo ""
fi
