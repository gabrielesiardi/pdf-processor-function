# 🚀 How to Push to GitHub

I've prepared everything for you, but I need your GitHub credentials to push. Here's how to complete the push:

## Quick Method (Recommended)

### Step 1: Download the project
The complete project is ready at: `azure-pdf-function/`

### Step 2: Navigate to the project
```bash
cd azure-pdf-function
```

### Step 3: Run the push script
```bash
./PUSH_TO_GITHUB.sh
```

This will:
- Initialize git (if needed)
- Add all files
- Create the commit
- Add your GitHub remote: https://github.com/gabrielesiardi/pdf-processor-function
- Push to GitHub (you'll be prompted for credentials)

---

## Authentication Options

When you run the push script, you'll need to authenticate. Choose one:

### Option A: GitHub CLI (Easiest)
```bash
# Install GitHub CLI
# Mac: brew install gh
# Windows: winget install GitHub.cli
# Linux: See https://cli.github.com/

# Authenticate
gh auth login

# Then run the push script
./PUSH_TO_GITHUB.sh
```

### Option B: Personal Access Token
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name like "Azure Function Deploy"
4. Check the "repo" scope
5. Generate and copy the token
6. When prompted for password, use the token instead

### Option C: SSH Key (If you have one set up)
```bash
# Change the remote to use SSH instead of HTTPS
git remote set-url origin git@github.com:gabrielesiardi/pdf-processor-function.git

# Then push
git push -u origin main
```

---

## Manual Method (If script doesn't work)

```bash
cd azure-pdf-function

# Initialize git
git init
git branch -M main

# Configure your details
git config user.name "Gabriele Siardi"
git config user.email "gabriele.siardi@villafrut.it"

# Add files
git add .

# Commit
git commit -m "Initial commit: Streamlined Azure PDF Processing Function"

# Add remote
git remote add origin https://github.com/gabrielesiardi/pdf-processor-function.git

# Push (you'll be prompted for credentials)
git push -u origin main
```

---

## What Happens Next

Once pushed, you'll see your code at:
**https://github.com/gabrielesiardi/pdf-processor-function**

Then you can:
1. Set up GitHub Actions for auto-deployment (see START_HERE.md)
2. Deploy directly to Azure using `./deploy.sh`
3. Share the repository with your team

---

## Troubleshooting

### "Authentication failed"
- Use a Personal Access Token instead of your password
- Or install and use GitHub CLI: `gh auth login`

### "Repository not found"
- Make sure the repository exists: https://github.com/gabrielesiardi/pdf-processor-function
- Create it on GitHub if needed (you can create an empty repo)

### "Permission denied"
- Check you're logged into the correct GitHub account
- Verify you have write access to the repository

---

## Need Help?

If you run into issues, you can also:
1. Create the repository on GitHub first (empty)
2. Then run `./PUSH_TO_GITHUB.sh`

Or manually upload:
1. Go to https://github.com/gabrielesiardi/pdf-processor-function
2. Click "uploading an existing file"
3. Drag and drop the entire folder

---

**Ready?** Run `./PUSH_TO_GITHUB.sh` and follow the prompts!
