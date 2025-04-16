from scraper import main as run_scraper
from flask import jsonify
import json
from loguru import logger

def scrape_taxonomies(request):
    """Cloud Function entry point that wraps the scraper main function.
    
    Args:
        request: The request object from Flask
        
    Returns:
        A JSON response indicating success or failure
    """
    try:
        # Configure the logger for cloud environment
        logger.info("Starting taxonomy and CPT code scraping via Cloud Function")
        
        # Execute the scraper
        results = run_scraper()
        
        # Return success response with result details
        return jsonify({
            "status": "success", 
            "message": "Scraping completed successfully",
            "results": results
        })
    except Exception as e:
        logger.error(f"Error in Cloud Function: {str(e)}")
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

def local_run():
    """Function to run the scraper locally and print results"""
    try:
        print("Starting taxonomy and CPT code scraping...")
        results = run_scraper()
        print(f"Scraping completed successfully!")
        print(f"Results: {json.dumps(results, indent=2)}")
        return results
    except Exception as e:
        print(f"Error running scraper: {str(e)}")
        raise

if __name__ == "__main__":
    # This allows the script to be run directly for local testing
    local_run()
