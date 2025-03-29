## Codebase Summary and Planned Modifications

This document provides an overview of the existing codebase for the wedding venue crawler and the planned modifications to adapt it for crawling caregiver resources.

### Existing Codebase Structure

*   **`main.py`**:
    *   **Purpose:** Main entry point of the crawler application. Orchestrates the crawling process, initializes configurations, and saves the extracted data.
    *   **Adaptation:** Will be modified to use the new `Resource` model and configuration parameters for caregiver resource websites. The core crawling logic will be reused.

*   **`config.py`**:
    *   **Purpose:** Contains configuration constants such as `BASE_URL`, `CSS_SELECTOR`, and `REQUIRED_KEYS`.
    *   **Adaptation:** Will be updated with new `BASE_URL` values for caregiver resource websites, appropriate `CSS_SELECTOR` values to target resource listings, and `REQUIRED_KEYS` corresponding to the fields in the `Resource` model.

*   **`models/resource.py`**:
    *   **Purpose:** Defines the `CareResource` data model using Pydantic, specifying the structure of data to be extracted.

*   **`utils/data_utils.py`**:
    *   **Purpose:** Contains utility functions for data processing, such as checking for duplicate venues, verifying complete venue data, and saving venues to a CSV file.
    *   **Adaptation:** Functions will be adapted to work with the new `Resource` model. Specifically, `save_venues_to_csv` will be updated to use the fields defined in the `Resource` model.

*   **`utils/scraper_utils.py`**:
    *   **Purpose:** Contains utility functions related to web scraping, such as configuring the browser, setting up the LLM extraction strategy, and fetching and processing pages.
    *   **Adaptation:** The `get_llm_strategy` function will be significantly modified to:
        *   Update the `schema` to use the new `Resource` model schema.
        *   Update the `instruction` to guide the LLM to extract the 17 specific fields for caregiver resources.
        *   Other functions like `fetch_and_process_page` will be adapted to handle the new data structure and extraction process.

### Planned Modifications Summary

The primary modifications will focus on:

1.  **Data Model:** Replacing the `Venue` model with a more comprehensive `Resource` model in `models/resource.py`.
2.  **Configuration:** Updating `config.py` with website-specific settings for caregiver resources.
3.  **LLM Strategy:**  Refining the LLM extraction strategy in `utils/scraper_utils.py` to accurately extract the required information for caregiver resources.
4.  **Code Adaptation:** Adjusting `main.py` and utility functions in `utils/data_utils.py` and `utils/scraper_utils.py` to work seamlessly with the new data model and configuration.

These modifications will transform the existing wedding venue crawler into a dynamic and effective caregiver resource web crawler.
