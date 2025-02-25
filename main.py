from scraper import main
from flask import jsonify

def scrape_taxonomies(request):
    """Cloud Function entry point that wraps the scraper main function."""
    try:
        main()
        return jsonify({"status": "success", "message": "Scraping completed successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
