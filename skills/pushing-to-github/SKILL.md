---
name: pushing-to-github
description: Pushing Streamlit projects to GitHub. Use when initializing a repository, setting up .gitignore, and managing the commit/push workflow.
license: Apache-2.0
---

# Pushing to GitHub

Guide for managing your Streamlit source code on GitHub.

## 1. Initial setup

If you haven't initialized git in your project directory:

```bash
git init
git branch -M main
```

## 2. Configure .gitignore

Create a `.gitignore` file in your root directory to avoid pushing heavy environment files or secrets:

```text
# Python environment
.venv/
venv/
__pycache__/
*.pyc

# Streamlit secrets
.streamlit/secrets.toml

# OS specific
.DS_Store
Thumbs.db
```

## 3. Connect to GitHub

1. Create a new repository on GitHub.
2. Link your local directory to the remote:

```bash
git remote add origin https://github.com/your-username/your-repo-name.git
```

## 4. Committing and Pushing

Follow this standard flow for updates:

```bash
# Stage changes
git add .

# Commit with a clear message
git commit -m "feat: improve ui design and add icons"

# Push to main branch
git push -u origin main
```

## Tips

- **GitHub Desktop**: If you prefer a GUI, use GitHub Desktop for easier visual branching and staging.
- **Tokens**: If asked for a password during `git push`, use a **Personal Access Token (PAT)** instead of your account password.
