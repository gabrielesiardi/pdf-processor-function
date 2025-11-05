#!/bin/bash

# GitHub Push Script
# This script helps you push the code to GitHub

set -e

echo "========================================="
echo "Push Azure Function to GitHub"
echo "========================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "Error: Git is not installed"
    exit 1
fi

# Get GitHub repository URL
echo "First, create a new repository on GitHub if you haven't already."
echo "Then come back here."
echo ""
read -p "Enter your GitHub repository URL (e.g., https://github.com/username/repo.git): " REPO_URL

if [ -z "$REPO_URL" ]; then
    echo "Error: Repository URL is required"
    exit 1
fi

# Initialize git if not already
if [ ! -d .git ]; then
    echo ""
    echo "Initializing git repository..."
    git init
    echo "Git repository initialized"
fi

# Add all files
echo ""
echo "Adding files to git..."
git add .

# Create initial commit
echo ""
read -p "Enter commit message (default: 'Initial commit - Streamlined Azure PDF Function'): " COMMIT_MSG
COMMIT_MSG=${COMMIT_MSG:-"Initial commit - Streamlined Azure PDF Function"}

git commit -m "$COMMIT_MSG" || echo "Nothing to commit or already committed"

# Rename branch to main if needed
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo ""
    echo "Renaming branch to 'main'..."
    git branch -M main
fi

# Add remote
echo ""
echo "Adding remote repository..."
git remote remove origin 2>/dev/null || true
git remote add origin "$REPO_URL"

# Push to GitHub
echo ""
echo "Pushing to GitHub..."
git push -u origin main

echo ""
echo "========================================="
echo "Success! Code pushed to GitHub"
echo "========================================="
echo ""
echo "Repository: $REPO_URL"
echo ""
echo "Next steps:"
echo "1. Go to your GitHub repository"
echo "2. Add AZURE_FUNCTIONAPP_PUBLISH_PROFILE secret for auto-deployment"
echo "3. Update .github/workflows/deploy.yml with your function app name"
echo "4. Push changes to trigger automatic deployment"
echo ""
echo "Or deploy manually using: ./deploy.sh"
echo ""
