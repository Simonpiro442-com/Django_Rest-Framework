#!/usr/bin/env python3
"""
Local runner script for the taxonomy and CPT code scraper.
This version doesn't depend on Flask, making it easier to run locally.
"""

import json
import os
from loguru import logger
from scraper import main as run_scraper
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def local_run():
    """Run the scraper locally and print results"""
    try:
        print("=" * 80)
        print("STARTING TAXONOMY AND CPT CODE SCRAPER")
        print("=" * 80)
        print()
        
        # Check for GCS configuration
        gcs_bucket = os.getenv('GCS_BUCKET_NAME')
        if gcs_bucket and gcs_bucket.strip():
            print(f"GCS storage enabled. Files will be uploaded to bucket: {gcs_bucket}")
        else:
            print("GCS storage disabled. Files will be saved locally to the 'output' directory")
        
        print("\nStarting scraper...\n")
        
        # Run the scraper
        results = run_scraper()
        
        print("\n" + "=" * 80)
        print("SCRAPING COMPLETED SUCCESSFULLY")
        print("=" * 80)
        
        # Print results summary
        print(f"\nSummary:")
        print(f"  - CMS CPT/HCPCS codes: {results['cms_codes_count']}")
        print(f"  - NUCC taxonomy codes: {results['nucc_codes_count']}")
        print(f"  - Total codes: {results['total_codes_count']}")
        
        print("\nOutput files:")
        for name, url in results['file_urls'].items():
            print(f"  - {name}: {url}")
            
        print("\nCheck the 'output' directory for the generated files.")
        
        return results
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        logger.error(f"Error running scraper: {str(e)}")
        raise

if __name__ == "__main__":
    local_run() 