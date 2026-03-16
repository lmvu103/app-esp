---
name: deploying-to-vercel
description: Deploying Streamlit apps to Vercel. Use when configuring Python runtimes, vercel.json, and setting up automatic GitHub deployments.
license: Apache-2.0
---

# Deploying to Vercel

Configuring your Streamlit app for the Vercel platform.

## 1. Configuration (vercel.json)

Create a `vercel.json` file in your root directory. This tells Vercel how to handle the Streamlit server:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "streamlit_app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "(.*)",
      "dest": "streamlit_app.py"
    }
  ]
}
```

## 2. Requirements

Ensure your `requirements.txt` is up to date. Vercel automatically installs these during the build:

```bash
pip freeze > requirements.txt
```

> [!IMPORTANT]
> Ensure `streamlit` is listed in your `requirements.txt`.

## 3. Deployment Flow

1. **GitHub Integration**: Connect your GitHub repository within the Vercel Dashboard.
2. **Environment Variables**: If your app uses secrets (like API keys), add them in **Project Settings > Environment Variables** on Vercel.
3. **Deploy**: Every push to the `main` branch will trigger an automatic deployment.

## Common Issues

- **Port issues**: Vercel handles the networking. Do not specify `--server.port` in any deployment scripts.
- **Heavy dependencies**: Large ML models may exceed Vercel's build limits. For heavy apps, **Streamlit Community Cloud** is often a better alternative.

## References

- [Vercel Python Runtime](https://vercel.com/docs/functions/runtimes/python)
- [Streamlit Deployment Guide](https://docs.streamlit.io/deploy/streamlit-community-cloud)
