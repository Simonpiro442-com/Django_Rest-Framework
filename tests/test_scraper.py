import pytest
from scraper import BaseScraper, CMSScraper, NUCCScraper

def test_base_scraper_initialization():
    scraper = BaseScraper()
    assert scraper.session is not None
    assert 'User-Agent' in scraper.headers

def test_cms_scraper_initialization():
    scraper = CMSScraper()
    assert scraper.url == "https://www.cms.gov/medicare/regulations-guidance/physician-self-referral/list-cpt-hcpcs-codes"

def test_nucc_scraper_initialization():
    scraper = NUCCScraper()
    assert scraper.url == "https://taxonomy.nucc.org/"
