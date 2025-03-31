# utils/llm_utils.py

import os
import logging
from dotenv import load_dotenv
from typing import Optional, List
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.rate_limiters import InMemoryRateLimiter

from models.resource import RankedUrlList

load_dotenv()

rate_limiter = InMemoryRateLimiter(
    requests_per_second=5,  # Limit to 5 requests per second
    check_every_n_seconds=0.1,  # Wake up every 100 ms to check whether allowed to make a request,
    max_bucket_size=10,  # Controls the maximum burst size.
)

def get_langchain_groq() -> BaseChatModel:
    """Returns a LangChain Groq LLM instance."""
    return ChatGroq(model='groq/deepseek-r1-distill-llama-70b', temperature=0.2, api_key=os.getenv("GROQ_API_KEY"), rate_limiter=rate_limiter)


async def extract_with_llm(content: str, extraction_template: BaseModel, llm: BaseChatModel = get_langchain_groq()) -> Optional[BaseModel]:
    """Processes HTML content with LangChain and the LLM."""
    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert extraction algorithm. "
                "Only extract relevant information from the text. "
                "If you do not know the value of an attribute asked to extract, "
                "return null for the attribute's value.",
            ),
            # Please see the how-to about improving performance with
            # reference examples.
            # MessagesPlaceholder('examples'),
            ("human", "{text}"),
        ]
    )
    chain = prompt_template | llm.with_structured_output(extraction_template)

    try:
        output = await chain.ainvoke({"text": content})
        return output
    except Exception as e:
        print(f"Langchain processing error: {e}")
        return None

async def rank_pages_for_secondary_crawl(content: str, llm: BaseChatModel = get_langchain_groq(), max_links_to_rank=20) -> List[str]:
    """
    Analyzes markdown content to find and rank URLs likely containing resource details.

    Args:
        content: The markdown content of the webpage.
        llm: The language model instance to use.
        max_links_to_rank: Maximum number of links to send to LLM for ranking.

    Returns:
        A list of 0 to 5 URLs ranked from most promising to least promising.
    """
    if not content:
        return []

    try:
        # # 1. Extract links (URL and text)
        # extracted_links = extract_links_from_markdown(content)
        # if not extracted_links:
        #     logging.info("No links found in content for secondary crawl ranking.")
        #     return []

        # # Limit the number of links sent to the LLM to avoid overly large prompts
        # links_to_rank = extracted_links[:max_links_to_rank]

        # # Format links for the prompt
        # link_list_string = "\n".join([f"- Text: '{link['text']}', URL: {link['url']}" for link in links_to_rank])

        # 2. Prepare prompt and chain
        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an expert web analyst specializing in finding specific information online. Your task is to analyze a list of links extracted from a webpage's markdown content. The primary goal is to find pages containing detailed information about resources for caregivers, people with dementia, or older adults (e.g., specific program details, support group schedules, financial aid applications, eligibility criteria, direct contact information).\n\n"
                    "Evaluate the provided list of links based on their URL structure and link text. Identify and rank the URLs that are *most likely* to lead directly to this detailed resource information.\n\n"
                    "Prioritize links with text like 'Services', 'Programs', 'Support', 'Resources', 'Grants', 'Apply Here', 'Contact Us', 'Locations', 'Eligibility', 'Schedule', 'Care', 'Assistance'.\n"
                    "De-prioritize or ignore generic links like 'Home', 'About Us' (unless context suggests it lists resources), 'News', 'Blog', 'Privacy Policy', 'Terms of Service', 'Login', 'Donate', main social media profile links, image/document files (.pdf, .jpg).\n\n"
                    "Focus ONLY on the URLs provided in the list below."
                ),
                (
                    "human",
                    "Here is the page:\n{content}\n\n"
                    # "Here is the list of links extracted from the page:\n{link_list_string}\n\n"
                    "Please return a ranked list of the top 2-5 URLs from this list that are most promising for finding detailed caregiver resource information. The list should be ordered from most promising to least promising."
                ),
            ]
        )
        # Ensure the output schema matches the Pydantic model defined above
        chain = prompt_template | llm.with_structured_output(RankedUrlList)

        # 3. Invoke LLM
        output: Optional[RankedUrlList] = await chain.ainvoke({
            # "markdown_content": content, # Avoid sending full markdown if possible
            "content": content
        })

        # 4. Process result
        if output and output.ranked_urls:
            # Ensure we return between 0 and 5 URLs
            ranked_list = output.ranked_urls[:5]
            logging.info(f"LLM recommended secondary crawl URLs: {ranked_list}")
            return ranked_list
        else:
            logging.warning("LLM did not return a ranked list of URLs for secondary crawl.")
            return []

    except Exception as e:
        logging.error(f"Error ranking pages for secondary crawl: {e}", exc_info=True)
        return []