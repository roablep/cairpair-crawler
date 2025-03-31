# main.py

import asyncio
import argparse
import logging
import os  # Added os import
import re
from urllib.parse import urlparse
from datetime import datetime
from typing import List, Set, Dict, Any  # Added for type hinting

from crawl4ai import AsyncWebCrawler
from dotenv import load_dotenv

from config import CSS_SELECTOR, REQUIRED_KEYS
from utils.data_utils import save_resources_to_csv
from utils.scraper_utils import (
    fetch_and_process_page,
    get_browser_config,
    get_llm_strategy,
)

# Load environment variables
load_dotenv()

STARTING_URLS = [
    "https://wearehfc.org/care-grants/",
    "https://leezascareconnection.org/home",
    "https://lorenzoshouse.org/",
    "https://www.fns.usda.gov/snap/supplemental-nutrition-assistance-program",
    "https://www.needymeds.org"
]

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# --- Helper Function for Sanitizing Filenames ---
def sanitize_filename(url: str) -> str:
    """Creates a safe filename string from a URL."""
    parsed_url = urlparse(url)
    # Use netloc (domain) and path, replacing non-alphanumeric chars
    filename = f"{parsed_url.netloc}{parsed_url.path}"
    filename = re.sub(r'[^\w\-_\.]', '_', filename)  # Keep word chars, hyphen, underscore, dot
    filename = filename.strip('_')  # Remove leading/trailing underscores
    # Truncate if too long (optional)
    max_len = 100
    if len(filename) > max_len:
        filename = filename[:max_len]
    return filename if filename else "default_url"

# --- Core Crawling Function ---
async def crawl_resources(start_urls: list[str], output_filename: str):
    """
    Crawls a list of starting URLs to extract caregiver resources.

    Args:
        start_urls (list[str]): Starting URLs.
        output_filename (str): Output filename (without directory).
    """
    logging.info(f"Initializing crawl for {len(start_urls)} URL(s).")
    browser_config = get_browser_config()
    llm_strategy = get_llm_strategy()
    session_id = f"crawl_session_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    all_resources: List[Dict[str, Any]] = []  # Added type hint
    seen_resource_identifiers: Set[str] = set()  # Renamed and added type hint
    urls_to_crawl = set(start_urls)
    crawled_urls = set()

    async with AsyncWebCrawler(config=browser_config) as crawler:
        while urls_to_crawl:
            url = urls_to_crawl.pop()

            if not url or url in crawled_urls:
                continue

            logging.info(f"🌐 Crawling: {url}")
            crawled_urls.add(url)

            try:
                # Updated function call arguments
                resources = await fetch_and_process_page(
                    crawler=crawler,
                    url=url,
                    css_selector=CSS_SELECTOR,
                    llm_strategy=llm_strategy,
                    session_id=session_id,
                    required_keys=REQUIRED_KEYS,
                    seen_resource_identifiers=seen_resource_identifiers,  # Use renamed variable
                )

                if resources:
                    all_resources.extend(resources)
                    logging.info(f"✅ {len(resources)} resources added from {url} (Total: {len(all_resources)})")
                else:
                    logging.info(f"⚠️ No resources found on {url}")

            except Exception as e:
                logging.error(f"❌ Error processing {url}: {e}", exc_info=True)

            await asyncio.sleep(2)  # Politeness delay

    if all_resources:
        # Ensure the data directory exists
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        full_output_path = os.path.join(data_dir, output_filename)

        save_resources_to_csv(all_resources, full_output_path)
        logging.info(f"📦 All resources saved to {full_output_path} (gzipped pickle)")
    else:
        logging.warning("🚫 No resources extracted.")

    logging.info("📊 LLM Usage:")
    llm_strategy.show_usage()


# --- Main Entry Point ---
async def main():
    parser = argparse.ArgumentParser(
        description="CarePair Resource Crawler – Extracts dementia caregiver resources from web pages."
    )
    parser.add_argument(
        'urls',
        metavar='URL',
        type=str,
        nargs='*',
        help='One or more URLs to crawl.'
    )
    parser.add_argument(
        '-o', '--output',
        default='resources.csv',
        type=str,
        help='Output filename in data/ directory (default: resources.csv)'
    )

    args = parser.parse_args()
    # Check if URLs were provided via CLI argument
    if args.urls:
        logging.info("Using URLs provided via command line.")
        urls = args.urls
    elif STARTING_URLS:
        logging.info("No URLs provided via CLI. Using default STARTING_URLS.")
        urls = STARTING_URLS
    else:
        logging.error("No URLs provided via CLI and STARTING_URLS is empty. Exiting.")
        return  # Exit if no URLs are available

    await crawl_resources(urls, args.output)


if __name__ == "__main__":
    asyncio.run(main())
