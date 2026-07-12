# Transaction Fraud Detection

Flask web app for transaction fraud detection.

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

## Render deployment

Use these settings on Render:

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`

The included `render.yaml` uses the same settings.
