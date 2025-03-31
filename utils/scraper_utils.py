# utils/scraper_utils.py
import logging
import os
from datetime import datetime
from typing import List, Set, Optional
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
from urllib.parse import urlparse
from typing import Dict, Any  # Added for type hinting

from utils.llm_utils import extract_with_llm, rank_pages_for_secondary_crawl, classify_resource_type
from models.resource import CareResource, CareResourceforLLM, CareResourcesforLLM, CareResources, ResourceProviderforLLM, ResourceProvider, RankedUrlList
from utils.data_utils import is_complete_resource, is_duplicate_resource, save_resource_to_gzipped_pickle

logger = logging.getLogger(__name__)

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
    llm_strategy: LLMExtractionStrategy | None,
    session_id: str,
    required_keys: List[str],
    seen_resource_identifiers: Set[str],
    global_crawled_urls: Set[str], 
    current_depth: int = 0,
    max_depth: int = 1,
    max_secondary_links: int = 3,
    existing_resources: list[Optional[dict]] = [],
    existing_provider: Optional[ResourceProvider] = None,
) -> tuple[List[Optional[dict[str, Any]]], Optional[ResourceProvider]]:
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
        global_crawled_urls: Set to track URLs already visited in this crawl task.
        current_depth: The current depth of the crawl (0 for initial).
        max_depth: The maximum depth to crawl recursively.
        max_secondary_links: The max number of ranked secondary links to follow.


    Returns:
        CrawlResult: A list of processed resources from the page.
    """
    # --- Base Case Checks ---
    trigger_secondary_crawl = False
    # Check 1: Already crawled globally in this job?
    if url in global_crawled_urls:
        logger.info(f"[Depth {current_depth}] Skipping already crawled URL: {url}")
        return [], None
    # Check 2: Exceeded maximum depth?
    if current_depth > max_depth:
        logger.warning(f"[Depth {current_depth}] Max depth ({max_depth}) reached for URL: {url}. Stopping descent.")
        return [], None

    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,  # Do not use cached data
        deep_crawl_strategy=None,
        extraction_strategy=None,  # llm_strategy,  # Strategy for data extraction
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
    # Mark this URL as crawled for this job run
    global_crawled_urls.add(result.url)

    if not result.success or not result.markdown:
        print(f"Error fetching page {url}: {result.error_message}")  # Use url in log
        return [], None  # Return empty list on error

    ranked_pages = None

    if current_depth == 0:
        # only get on main crawl
        provider: ResourceProvider = await extract_with_llm(content=result.markdown, extraction_template=ResourceProviderforLLM)
    else:
        provider = existing_provider

    care_resources: CareResources = await extract_with_llm(content=result.markdown, extraction_template=CareResourcesforLLM)
    resources = care_resources.resources
    if resources is None or not all(is_complete_resource(r) for r in resources):
        logger.info(f"Generating 2ndary crawl candidates for {result.url}")
        ranked_pages: RankedUrlList = await rank_pages_for_secondary_crawl(content=result.markdown)
        trigger_secondary_crawl = True

    # save result
    save_resource_to_gzipped_pickle(
        resource={'crawl_result': result, 'provider': provider, 'resources': resources, 'ranked_pages': ranked_pages},
        filename=f"result_{url.replace('/', '_')}.pkl.gz",
        data_dir="./data/crawl"
    )

    provider.website = result.url

    if trigger_secondary_crawl:
        if ranked_pages and current_depth < max_depth:
            for i, secondary_url in enumerate(ranked_pages[:max_secondary_links]):
                logger.info(f"[Depth {current_depth}] >>> Trying secondary URL #{i+1}: {secondary_url}")
                secondary_resources, _ = await fetch_and_process_page(
                    crawler=crawler,  # *** Pass the SAME crawler instance ***
                    url=secondary_url,
                    llm_strategy=None,
                    css_selector=None,
                    session_id=session_id,
                    required_keys=required_keys,
                    seen_resource_identifiers=seen_resource_identifiers,  # Share the set for global deduplication
                    global_crawled_urls=global_crawled_urls,      # Share the set to avoid loops/revisits
                    current_depth=current_depth + 1,             # Increment depth
                    max_depth=max_depth,                         # Pass limits down
                    max_secondary_links=max_secondary_links,
                    existing_provider=provider,
                    existing_resources=resources
                )
                if secondary_resources:
                    resources = secondary_resources
                else:
                    print(f"No resources found on subpage {url}.")  # Use url in log
                    return [], None

    # Process resources
    for resource in resources:
        # Use a more robust identifier if needed, for now using name
        resource_identifier = resource.resource_name
        if is_duplicate_resource(resource_identifier, seen_resource_identifiers):
            # print(f"Duplicate resource '{resource_identifier}' found. Skipping.")
            continue  # Skip duplicate resources

        # reclassify the resource
        resource_info = resource.model_dump()
        if resource_info['resource_category']:
            del resource_info['resource_category']

        cat_subscat = await classify_resource_type(resource_info)

        new_resource = CareResource(**resource.model_dump())
        new_resource.resource_category = cat_subscat.category
        new_resource.resource_subcategory = cat_subscat.subcategory
        new_resource.source_url = result.url
        new_resource.date_added_to_db = datetime.now()
        new_resource.date_last_reviewed = datetime.now()
        new_resource.source_url = result.url
        new_resource.source_origin = urlparse(result.url).netloc

        # Add resource identifier to the set
        seen_resource_identifiers.add(resource_identifier)
        existing_resources.append(new_resource.model_dump())

    if not existing_resources:
        # print(f"No complete and non-duplicate resources found on page {url}.")
        return [], provider

    new_provider = ResourceProvider(**provider.model_dump())
    new_provider.resources = existing_resources
    # print(f"Processed {len(complete_resources)} resources from {url}.")
    return existing_resources, new_provider  # Return only the list
