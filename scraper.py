#!/usr/bin/env python3
"""
Taxonomy and CPT Code Scraper
This script scrapes CMS CPT/HCPCS codes and NUCC taxonomy codes,
consolidates them into JSON format, and uploads to Google Cloud Storage.
"""

import os
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from loguru import logger
from google.cloud import storage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger.add("scraper.log", rotation="500 MB")

class BaseScraper:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def _make_request(self, url: str) -> requests.Response:
        """Make HTTP request with error handling and retries."""
        try:
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            raise

class CMSScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.url = "https://www.cms.gov/medicare/regulations-guidance/physician-self-referral/list-cpt-hcpcs-codes"

    def scrape(self) -> List[Dict[str, str]]:
        """Scrape CMS CPT/HCPCS codes."""
        logger.info("Starting CMS CPT/HCPCS code scraping")
        
        response = self._make_request(self.url)
        soup = BeautifulSoup(response.content, 'lxml')
        
        codes = []
        try:
            # Note: This is a placeholder for the actual table selection logic
            # You'll need to adjust these selectors based on the actual page structure
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header row
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        codes.append({
                            "source": "cms",
                            "code": cols[0].get_text(strip=True),
                            "description": cols[1].get_text(strip=True),
                            "category": "CPT/HCPCS",
                            "taxonomy_code": None,
                            "cpt_code": cols[0].get_text(strip=True)
                        })
        
        except Exception as e:
            logger.error(f"Error parsing CMS data: {str(e)}")
            raise
        
        logger.info(f"Successfully scraped {len(codes)} CMS codes")
        return codes

class NUCCScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://taxonomy.nucc.org/"
        self.csv_url = "https://taxonomy.nucc.org/cs/groups/public/documents/datalist/nucc_taxonomy_234.csv"
        # Check if the CSV URL is updated periodically, you might need to scrape the main page to find the current link

    def scrape(self) -> List[Dict[str, str]]:
        """Scrape NUCC taxonomy codes."""
        logger.info("Starting NUCC taxonomy code scraping")
        
        try:
            # First try direct CSV download (more reliable)
            response = self._make_request(self.csv_url)
            
            # Process the CSV data
            import csv
            from io import StringIO
            
            csv_data = StringIO(response.text)
            reader = csv.DictReader(csv_data)
            
            codes = []
            for row in reader:
                # Adjust these field names based on actual CSV headers
                codes.append({
                    "source": "nucc",
                    "code": row.get("Code"),
                    "description": row.get("Classification"),
                    "category": row.get("Specialization"),
                    "taxonomy_code": row.get("Code"),
                    "speciality": row.get("Definition"),
                    "cpt_code": None
                })
                
            logger.info(f"Successfully scraped {len(codes)} NUCC taxonomy codes from CSV")
            return codes
            
        except Exception as e:
            logger.warning(f"CSV download failed, attempting HTML scraping: {str(e)}")
            
            # Fallback to HTML scraping
            response = self._make_request(self.base_url)
            soup = BeautifulSoup(response.content, 'lxml')
            
            codes = []
            # Look for download links or tables
            download_link = soup.find('a', href=lambda href: href and '.csv' in href)
            
            if download_link:
                # If we found a CSV link, use that instead
                csv_url = download_link.get('href')
                if not csv_url.startswith('http'):
                    csv_url = self.base_url + csv_url
                
                logger.info(f"Found CSV download link: {csv_url}")
                return self.scrape_from_csv(csv_url)
            
            # If no CSV, look for tables
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        codes.append({
                            "source": "nucc",
                            "code": cols[0].get_text(strip=True),
                            "description": cols[1].get_text(strip=True),
                            "category": cols[2].get_text(strip=True) if len(cols) > 2 else "General",
                            "taxonomy_code": cols[0].get_text(strip=True),
                            "cpt_code": None
                        })
            
            logger.info(f"Successfully scraped {len(codes)} NUCC taxonomy codes from HTML")
            return codes
            
    def scrape_from_csv(self, csv_url: str) -> List[Dict[str, str]]:
        """Helper method to scrape from CSV URL."""
        response = self._make_request(csv_url)
        import csv
        from io import StringIO
        
        csv_data = StringIO(response.text)
        reader = csv.DictReader(csv_data)
        
        codes = []
        for row in reader:
            # Adjust field names based on actual CSV structure
            codes.append({
                "source": "nucc",
                "code": row.get("Code"),
                "description": row.get("Classification"),
                "category": row.get("Specialization"),
                "taxonomy_code": row.get("Code"),
                "cpt_code": None
            })
        
        return codes

class GCSUploader:
    def __init__(self):
        # Comment out GCS functionality and force local storage for testing
        # self.bucket_name = os.getenv('GCS_BUCKET_NAME')
        # self.use_gcs = self.bucket_name is not None and self.bucket_name.strip() != ""
        
        # Force local storage for testing
        self.use_gcs = False
        self.bucket_name = None
        
        # if self.use_gcs:
        #     self.client = storage.Client()
        #     self.bucket = self.client.bucket(self.bucket_name)
        #     logger.info(f"GCS storage enabled. Will upload to bucket: {self.bucket_name}")
        # else:
        # Ensure local output directory exists
        self.output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"GCS storage disabled. Will save files locally to: {self.output_dir}")

    def upload_json(self, data: List[Dict[str, Any]], prefix: str) -> str:
        """Upload JSON data to GCS or save locally with timestamp in filename."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{prefix}_{timestamp}.json"
        
        try:
            # Comment out GCS upload code for testing
            # if self.use_gcs:
            #     # Upload to Google Cloud Storage
            #     blob = self.bucket.blob(filename)
            #     blob.upload_from_string(
            #         json.dumps(data, indent=2),
            #         content_type='application/json'
            #     )
            #     file_path = f"gs://{self.bucket_name}/{filename}"
            #     logger.info(f"Successfully uploaded {filename} to GCS")
            # else:
            # Save locally
            local_path = os.path.join(self.output_dir, filename)
            with open(local_path, 'w') as f:
                json.dump(data, f, indent=2)
            file_path = f"file://{local_path}"
            logger.info(f"Successfully saved {filename} locally")
                
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving/uploading data: {str(e)}")
            raise

def main():
    """Main execution function."""
    try:
        # Scrape CMS codes
        cms_scraper = CMSScraper()
        cms_codes = cms_scraper.scrape()

        # Scrape NUCC taxonomy codes
        nucc_scraper = NUCCScraper()
        nucc_codes = nucc_scraper.scrape()

        # Combine all codes
        all_codes = cms_codes + nucc_codes

        # Upload to GCS
        uploader = GCSUploader()
        
        # Upload combined dataset
        combined_url = uploader.upload_json(all_codes, "all_codes")
        logger.info(f"Combined dataset uploaded to: {combined_url}")
        
        # Upload separate datasets
        cms_url = uploader.upload_json(cms_codes, "cms_codes")
        nucc_url = uploader.upload_json(nucc_codes, "nucc_codes")
        
        logger.info(f"CMS codes uploaded to: {cms_url}")
        logger.info(f"NUCC codes uploaded to: {nucc_url}")

        # Return results for API response
        return {
            "cms_codes_count": len(cms_codes),
            "nucc_codes_count": len(nucc_codes),
            "total_codes_count": len(all_codes),
            "file_urls": {
                "combined": combined_url,
                "cms": cms_url,
                "nucc": nucc_url
            }
        }

    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()
