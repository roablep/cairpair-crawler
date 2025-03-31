## Current Task: Adapt Web Crawler for Caregiver Resources

### Objectives

*   Adapt the existing web crawler project to extract data for caregiver resources instead of wedding venues.
*   Create a dynamic web crawler that can extract 17 key data points for each resource from various websites.
*   Ensure the crawler is flexible enough to handle different website structures and formats.

### Context

*   We are building a mobile application, CarePair, which is a directory of resources for caregivers of older adults, specifically those caring for individuals with dementia.
*   The goal of the web crawler is to automate the process of collecting resource information, which is currently a manual and inefficient process.
*   We need to extract 17 specific data points for each resource, including name, type, location, contact information, description, and more.
*   We will be using the existing web crawler codebase as a starting point and adapting it to this new use case.
*   This task is part of Phase 2: Code Modification & Data Model in the project roadmap (see `projectRoadmap.md`).

### Next Steps

1.  **Create `techStack.md`:** Document the technology stack for this project, including Python, `crawl4ai`, `pydantic`, etc.
2.  **Create `codebaseSummary.md`:** Provide a summary of the existing codebase structure and planned modifications.
3.  **Modify `models/venue.py` to `models/resource.py`:** Adapt the data model to represent caregiver resources with the required 17 fields.
4.  **Modify `config.py`:** Update configuration variables such as `BASE_URL`, `CSS_SELECTOR`, and `REQUIRED_KEYS` for caregiver resource websites.
5.  **Modify `utils/scraper_utils.py`:** Update the LLM extraction strategy to extract caregiver resource data based on the new `Resource` model.
6.  **Modify `utils/data_utils.py`:** Adapt the data saving function (`save_resources_to_gzipped_pickle`) to save output as a gzipped pickle file in the `data/` directory.
7.  **Modify `main.py`:** Adapt the main crawling logic to call the updated saving function and handle the new output format/location.
8.  **Test the crawler:** Test the adapted crawler on the example URLs provided and refine as needed.

### Reference Documents

*   [projectRoadmap.md](cline_docs/projectRoadmap.md): For high-level project goals and progress.
*   [.clinerules](.clinerules): For project documentation and workflow guidelines.
