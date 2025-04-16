<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# Generate a mark down file with the implementation plan described above..

```markdown
# CPT Code Scraper Implementation Plan

## 📋 Overview
Weekly scraper for healthcare services/CPT codes running on GCP Cloud Run with GCS integration.

---

## 🛠️ Core Components

### 1. Python Scraper (`scraper.py`)
```

import json
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from google.cloud import storage

def fetch_cpt_codes():
url = "https://example-cpt-code-source.com"  \# REPLACE WITH ACTUAL SOURCE
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

    services = []
    for row in soup.select("table.cpt-codes tr"):  # ADJUST SELECTOR
        cells = row.find_all("td")
        if len(cells) == 2:
            services.append({
                "service": cells.text.strip(),
                "cpt_code": cells.text.strip()
            })
    return services
    def upload_to_gcs(bucket_name, data):
client = storage.Client()
bucket = client.bucket(bucket_name)
blob = bucket.blob(f"cpt-codes-{datetime.now().isoformat()}.json")
blob.upload_from_string(json.dumps(data))

if __name__ == "__main__":
data = fetch_cpt_codes()
upload_to_gcs(os.environ["GCS_BUCKET"], data)

```

---

### 2. Infrastructure Setup
| Service           | Configuration                                                                 |
|-------------------|-------------------------------------------------------------------------------|
| **GCS Bucket**    | `healthcare-cpt-codes` with IAM permissions for Cloud Run service account      |
| **Cloud Run**     | 1 CPU / 256MB RAM, timeout set to 10 minutes                                   |
| **Cloud Scheduler** | Cron: `0 0 * * 0` (Sundays 00:00 UTC)                                        |

---

## 🐳 Deployment Package
```


# Dockerfile

FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY scraper.py .
CMD ["python", "scraper.py"]

```

**Requirements:**
```

requests==2.31.0
beautifulsoup4==4.12.3
google-cloud-storage==2.14.0

```

---

## 🚀 Deployment Commands
```


# Build and deploy

gcloud builds submit --tag gcr.io/YOUR-PROJECT/cpt-scraper
gcloud run deploy cpt-scraper \
--image gcr.io/YOUR-PROJECT/cpt-scraper \
--set-env-vars GCS_BUCKET=healthcare-cpt-codes \
--service-account=scraper-sa@YOUR-PROJECT.iam.gserviceaccount.com \
--region us-central1 \
--no-allow-unauthenticated

# Schedule job

gcloud scheduler jobs create http cpt-scraper-job \
--schedule "0 0 * * 0" \
--uri="https://cpt-scraper-xxxxxx-uc.a.run.app" \
--oidc-service-account-email=scraper-sa@YOUR-PROJECT.iam.gserviceaccount.com

```

---

## 🔐 Security &amp; Compliance
1. Add service account with **Storage Object Admin** role
2. Enable VPC Service Controls if handling PHI
3. Implement IP rotation using `requests-rotating-proxy`

---

## ✅ Validation Checklist
```

def validate_cpt(code):
return len(code) == 5 and code.isdigit()

# Add to main script:

valid_entries = [s for s in data if validate_cpt(s['cpt_code'])]

```

---

## 💡 Optimization Tips
1. Enable GCS lifecycle rules for auto-archival
2. Use Cloud Run min instances = 0 for cost efficiency
3. Implement request caching with `CacheControl`

---

## 🚨 Error Handling
```


# Add to scraper.py

from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_cpt_codes():
\# existing code

```

**Note:** Install `tenacity` package for retry logic

---

## 📊 Monitoring Setup
1. Create Cloud Monitoring alerts for:
   - Failed Cloud Run executions
   - GCS upload errors
   - HTTP 429/503 responses from target site
2. Enable Cloud Logging with filter:
   `resource.type="cloud_run_revision" severity&gt;=WARNING`

```

Save this as `IMPLEMENTATION.md` and replace ALL CAPS placeholders with your project-specific values. Remember to verify web scraping compliance with the target website's terms of service.

