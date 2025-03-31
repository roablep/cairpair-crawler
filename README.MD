## Installation

1. **Create and Activate a Conda Environment**

   ```bash
   conda update conda
   conda create -n deep-seek-crawler python=3.12 -y
   conda activate deep-seek-crawler

   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install Dependencies**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Set Up Your Environment Variables**

   Create a `.env` file in the root directory with content similar to:

   ```env
   GROQ_API_KEY=your_groq_api_key_here
   GOOGLE_API_KEY=your google key
   ```

   *(Note: The `.env` file is in your .gitignore, so it won’t be pushed to version control.)*

## Usage

To start the crawler, run:

```bash
python main.py
```
The script will crawl the specified website, extract data page by page, and save the complete venues to a `csv` file in the project directory. Additionally, usage statistics for the LLM strategy will be displayed after crawling.

## Additional Notes

Possibly use a proxy - https://dataimpulse.com/
https://github.com/scraperai/scraperai

Example services/resources
needymeds.org
wearehfc.org/care-grants/
leezascareconnection.org/home
https://lorenzoshouse.org/
https://www.fns.usda.gov/snap/supplemental-nutrition-assistance-program
