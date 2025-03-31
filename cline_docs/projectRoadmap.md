## Project Roadmap: Caregiver Resource Web Crawler

### High-Level Goals

*   Develop a dynamic web crawler to extract information about caregiver resources from various websites.
*   Create a comprehensive database of caregiver resources, categorized by type, location, and other relevant criteria.
*   Ensure the crawler is robust, scalable, and can handle different website structures.
*   Implement a scheduled crawling mechanism to keep the resource database up-to-date.
*   Output the extracted data in gzipped pickle format for efficient storage.

### Key Features

*   **Dynamic Crawling:** Ability to crawl various websites with different structures.
*   **Data Extraction:** Extract 17 key data points for each resource (name, type, location, contact info, etc.).
*   **Resource Type Categorization:** Classify resources into predefined categories (Direct Care, Support & Education, Financial & Legal, etc.).
*   **Location Awareness:** Capture location information for each resource.
*   **Contact Information Extraction:** Extract phone numbers, emails, websites, etc.
*   **Scheduled Crawling:** Ability to run the crawler on a schedule (daily, weekly, monthly).
*   **Error Handling & Logging:** Graceful error handling and logging of crawling issues.
*   **Gzipped Pickle Output:** Output data in a compressed pickle format.

### Completion Criteria

*   Crawler successfully extracts data from a defined list of target websites.
*   Extracted data includes all 17 key data points for a significant portion of resources.
*   Resource data is accurately categorized by type and location.
*   Crawler runs without errors and logs relevant information.
*   Gzipped pickle output is generated with all extracted data.
*   Basic documentation is in place.

### Progress Tracker

*   **Phase 1: Planning & Documentation** - [x]
    *   Define project scope and goals - [x]
    *   Plan adaptation of existing codebase - [x]
    *   Create initial documentation files - [x]
*   **Phase 2: Code Modification & Data Model** - [ ]
    *   Adapt data model for caregiver resources - [ ]
    *   Update configuration for target websites - [ ]
    *   Modify LLM strategy for resource extraction - [ ]
    *   Modify data saving to use gzipped pickle - [x]  <!-- Added this task -->
*   **Phase 3: Crawling & Extraction Logic** - [ ]
    *   Implement crawling logic for target websites - [ ]
    *   Refine data extraction and processing - [ ]
    *   Implement error handling and logging - [ ]
*   **Phase 4: Testing & Refinement** - [ ]
    *   Test crawler on target websites - [ ]
    *   Validate extracted data quality - [ ]
    *   Refine crawler performance and accuracy - [ ]
*   **Phase 5: Scheduling & Output** - [ ]
    *   Implement scheduled crawling - [ ]
    *   Configure gzipped pickle output - [x] <!-- Updated this task -->
    *   Finalize documentation - [ ]

### Future Scalability Considerations

*   **Website Expansion:** Design the crawler to be easily adaptable to new websites.
*   **Data Storage:** Consider using a database for larger datasets and more efficient data management in the future.
*   **Scalable Infrastructure:** Explore cloud-based crawling solutions for increased scalability if needed.
*   **API Integration:** Potentially expose extracted data through an API for other applications.

### Completed Tasks
*   **2025-03-29:** Project planning and documentation setup initiated. Initial project roadmap created.
*   **2025-03-31:** Modified data saving mechanism to use gzipped pickle format in the `data/` directory. Updated relevant code (`utils/data_utils.py`, `main.py`) and documentation (`currentTask.md`, `projectRoadmap.md`).
