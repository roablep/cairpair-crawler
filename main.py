# main.py

import asyncio
import argparse
import logging
import os
import re
from urllib.parse import urlparse 
from datetime import datetime

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
    filename = re.sub(r'[^\w\-_\.]', '_', filename) # Keep word chars, hyphen, underscore, dot
    filename = filename.strip('_') # Remove leading/trailing underscores
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
        output_filename (str): Output CSV filename.
    """
    logging.info(f"Initializing crawl for {len(start_urls)} URL(s).")
    browser_config = get_browser_config()
    llm_strategy = get_llm_strategy()
    session_id = f"crawl_session_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    all_resources = []
    seen_resource_keys = set()
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
                resources = await fetch_and_process_page(
                    crawler=crawler,
                    url=url,
                    css_selector=CSS_SELECTOR,
                    llm_strategy=llm_strategy,
                    session_id=session_id,
                    required_keys=REQUIRED_KEYS,
                    seen_keys=seen_resource_keys,
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
        save_resources_to_csv(all_resources, output_filename)
        logging.info(f"📦 All resources saved to {output_filename}")
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
        nargs='+',
        help='One or more URLs to crawl.'
    )
    parser.add_argument(
        '-o', '--output',
        default='resources.csv',
        type=str,
        help='Output CSV filename (default: resources.csv)'
    )

    args = parser.parse_args()
    await crawl_resources(args.urls, args.output)


if __name__ == "__main__":
    asyncio.run(main())
