# utils/scraper_utils.py
import json
import os
from typing import List, Set  # Removed Tuple
import asyncio
from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
    LLMExtractionStrategy,
    LLMConfig,
    CrawlResult
)
from crawl4ai.deep_crawling import DeepCrawlStrategy

from typing import Dict, Any  # Added for type hinting

from models.resource import CareResource, CareResources
from utils.data_utils import is_complete_resource, is_duplicate_resource


def get_browser_config() -> BrowserConfig:
    """
    Returns the browser configuration for the crawler.

    Returns:
        BrowserConfig: The configuration settings for the browser.
    """
    # https://docs.crawl4ai.com/core/browser-crawler-config/
    return BrowserConfig(
        browser_type="chromium",  # Type of browser to simulate
        headless=False,  # Whether to run in headless mode (no GUI)
        verbose=True,  # Enable verbose logging
    )

def get_llm_config() -> LLMConfig:
    return LLMConfig(
        provider="groq/deepseek-r1-distill-llama-70b",  # Name of the LLM provider
        api_token=os.getenv("GROQ_API_KEY"),  # API token for authentication
    )

def get_llm_strategy() -> LLMExtractionStrategy:
    """
    Returns the configuration for the language model extraction strategy.

    Returns:
        LLMExtractionStrategy: The settings for how to extract data using LLM.
    """
    # https://docs.crawl4ai.com/api/strategies/#llmextractionstrategy
    return LLMExtractionStrategy(
        llm_config=get_llm_config(),
        schema=CareResources.model_json_schema(),  # JSON schema of the data model
        extraction_type="schema",  # Type of extraction to perform
        instruction=(
            "Extract any dementia caregiving-related resources with fields such as name, resource type, location, "
            "contact info, description, meeting time, age range, target audience, cost, eligibility, language, "
            "accessibility, format (virtual/in-person), and website. If available, include last updated date and source. "
            "If a field is not present, omit it. Summarize long text when necessary."
        ),  # Instructions for the LLM
        input_format="markdown",  # Format of the input content
        verbose=True,  # Enable verbose logging
    )


async def check_no_results(
    crawler: AsyncWebCrawler,
    url: str,
    session_id: str,
) -> bool:
    """
    Checks if the "No Results Found" message is present on the page.

    Args:
        crawler (AsyncWebCrawler): The web crawler instance.
        url (str): The URL to check.
        session_id (str): The session identifier.

    Returns:
        bool: True if "No Results Found" message is found, False otherwise.
    """
    # Fetch the page without any CSS selector or extraction strategy
    # result = await crawler.arun(
    result = await safe_arun(
        crawler=crawler,
        url=url,
        config=CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            session_id=session_id,
        ),
    )

    if result.success:
        if "No Results Found" in result.cleaned_html:
            return True
    else:
        print(
            f"Error fetching page for 'No Results Found' check: {result.error_message}"
        )

    return False

async def safe_arun(crawler: AsyncWebCrawler, url: str, config: CrawlerRunConfig, retries=3) -> CrawlResult:
    for i in range(retries):
        result: CrawlResult = await crawler.arun(url, config=config)
        if result.success:
            return result
        if "Rate limit reached for model `deepseek-r1-distill-llama-70b`" in (result.error_message or "").lower():
            wait = 5 * (i + 1)
            print(f"⚠️ Groq rate limit hit. Retrying in {wait}s...")
            await asyncio.sleep(wait)
        else:
            break
    return result  # Final attempt, might still be failure

async def fetch_and_process_page(
    crawler: AsyncWebCrawler,
    url: str,  # Changed from page_number and base_url
    css_selector: str | None,  # Optional CSS selector. Do NOT use 'body'. Anything under 'body' is fine
    llm_strategy: LLMExtractionStrategy,
    session_id: str,
    required_keys: List[str],
    seen_resource_identifiers: Set[str],  # Renamed from seen_names
) -> CrawlResult:
    """
    Fetches and processes resource data from a single URL.

    Args:
        crawler (AsyncWebCrawler): The web crawler instance.
        url (str): The URL to fetch data from.
        css_selector (str): The CSS selector to target the content.
        llm_strategy (LLMExtractionStrategy): The LLM extraction strategy.
        session_id (str): The session identifier.
        required_keys (List[str]): List of required keys in the resource data.
        seen_resource_identifiers (Set[str]): Set of resource identifiers (e.g., names) already seen.

    Returns:
        CrawlResult: A list of processed resources from the page.
    """
    # Removed pagination logic and check_no_results call
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,  # Do not use cached data
        deep_crawl_strategy=None,
        extraction_strategy=llm_strategy,  # Strategy for data extraction
        only_text=True,  # get text only
        css_selector=css_selector,  # Target specific content on the page
        session_id=session_id,  # Unique session ID for the crawl
        semaphore_count=2,     # Concurrency cap (like dispatcher)
        mean_delay=2.0,        # Delay between requests to same domain
        max_range=3.0          # Adds random jitter between 0–3s
    )
    # Fetch page content with the extraction strategy
    # result = await crawler.arun(
    result = await safe_arun(
        crawler=crawler,
        url=url,  # Use the direct URL
        config=config,
    )

    # result['message']
    if not (result.success and result.extracted_content):
        print(f"Error fetching page {url}: {result.error_message}")  # Use url in log
        return []  # Return empty list on error

    # Parse extracted content
    try:
        extracted_data = json.loads(result.extracted_content)
        # Handle cases where LLM might return a single dict instead of a list
        if isinstance(extracted_data, dict):
            extracted_data = [extracted_data]
        if not isinstance(extracted_data, list):
            print(f"Unexpected data format from LLM for {url}: {type(extracted_data)}")  # Corrected indentation
            return []  # Corrected indentation
    except json.JSONDecodeError:
        print(f"Failed to decode JSON from LLM for {url}: {result.extracted_content}")
        return []

    if not extracted_data:
        print(f"No resources found on page {url}.")  # Use url in log
        return []

    # Debugging: Print extracted data structure
    # print(f"Extracted data type for {url}: {type(extracted_data)}")
    # print(f"Extracted data content for {url}: {extracted_data}")

    # Process resources
    complete_resources = []
    for resource in extracted_data:
        # Debugging: Print each resource to understand its structure
        # print("Processing resource:", resource)  # Commented out for cleaner logs

        # Ignore the 'error' key if it's False
        if resource.get("error") is False:
            resource.pop("error", None)  # Remove the 'error' key if it's False

        # Ensure resource is a dictionary before proceeding
        if not isinstance(resource, dict):
            print(f"Skipping non-dict item in extracted data for {url}: {resource}")
            continue

        # Use .get() for safer access, especially for 'name'
        resource_name = resource.get("name")
        if not resource_name:
            print(f"Skipping resource without a name from {url}: {resource}")
            continue

        # Ignore the 'error' key if it's False
        if resource.get("error") is False:
            resource.pop("error", None)  # Remove the 'error' key if it's False

        if not is_complete_resource(resource, required_keys):
            # print(f"Skipping incomplete resource '{resource_name}' from {url}.")  # Commented out
            continue  # Skip incomplete resources

        # Use a more robust identifier if needed, for now using name
        resource_identifier = resource_name
        if is_duplicate_resource(resource_identifier, seen_resource_identifiers):
            # print(f"Duplicate resource '{resource_identifier}' found. Skipping.")  # Commented out
            continue  # Skip duplicate resources

        # Add resource identifier to the set
        seen_resource_identifiers.add(resource_identifier)
        complete_resources.append(resource)

    if not complete_resources:
        # print(f"No complete and non-duplicate resources found on page {url}.")  # Commented out
        return []

    # print(f"Processed {len(complete_resources)} resources from {url}.")  # Commented out
    return complete_resources  # Return only the list
