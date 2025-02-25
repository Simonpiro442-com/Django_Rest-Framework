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
        self.url = "https://taxonomy.nucc.org/"

    def scrape(self) -> List[Dict[str, str]]:
        """Scrape NUCC taxonomy codes."""
        logger.info("Starting NUCC taxonomy code scraping")
        
        response = self._make_request(self.url)
        soup = BeautifulSoup(response.content, 'lxml')
        
        codes = []
        try:
            # Note: This is a placeholder for the actual taxonomy code extraction logic
            # You'll need to adjust these selectors based on the actual page structure
            taxonomy_elements = soup.find_all('div', class_='taxonomy-code')  # Adjust selector
            
            for element in taxonomy_elements:
                codes.append({
                    "source": "nucc",
                    "code": element.find('span', class_='code').get_text(strip=True),  # Adjust selector
                    "description": element.find('span', class_='description').get_text(strip=True),  # Adjust selector
                    "category": element.find('span', class_='category').get_text(strip=True),  # Adjust selector
                    "taxonomy_code": element.find('span', class_='code').get_text(strip=True),
                    "cpt_code": None
                })
        
        except Exception as e:
            logger.error(f"Error parsing NUCC data: {str(e)}")
            raise
        
        logger.info(f"Successfully scraped {len(codes)} NUCC taxonomy codes")
        return codes

class GCSUploader:
    def __init__(self):
        self.bucket_name = os.getenv('GCS_BUCKET_NAME')
        self.client = storage.Client()
        self.bucket = self.client.bucket(self.bucket_name)

    def upload_json(self, data: List[Dict[str, Any]], prefix: str) -> str:
        """Upload JSON data to GCS with timestamp in filename."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{prefix}_{timestamp}.json"
        blob = self.bucket.blob(filename)
        
        try:
            blob.upload_from_string(
                json.dumps(data, indent=2),
                content_type='application/json'
            )
            logger.info(f"Successfully uploaded {filename} to GCS")
            return f"gs://{self.bucket_name}/{filename}"
        except Exception as e:
            logger.error(f"Error uploading to GCS: {str(e)}")
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

    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()
