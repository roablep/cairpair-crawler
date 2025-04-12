# utils/llm_utils.py

import logging
import os
from typing import Dict, List, Optional

from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from pydantic import BaseModel

from config import RESOURCE_TYPE_CATEGORIES
from models.resource import CareResource
from models.resource_provider import ResourceProvider, ResourceProviderforLLM
from models.other_models import RankedUrlList, TagType, TagOutput

load_dotenv()

logger = logging.getLogger(__name__)

class category(BaseModel):
    category: str
    subcategory: str

rate_limiter = InMemoryRateLimiter(
    requests_per_second=5,  # Limit to 5 requests per second
    check_every_n_seconds=0.1,  # Wake up every 100 ms to check whether allowed to make a request,
    max_bucket_size=10,  # Controls the maximum burst size.
)

def get_langchain_model() -> BaseChatModel:
    """Returns a LangChain Groq LLM instance."""
    # return ChatGroq(model='deepseek-r1-distill-llama-70b', temperature=0.2, api_key=os.getenv("GROQ_API_KEY"), rate_limiter=rate_limiter)
    return ChatGoogleGenerativeAI(model='gemini-2.0-flash-lite', temperature=0.2, api_key=os.getenv("GOOGLE_API_KEY"), rate_limiter=rate_limiter)

async def dedupe_and_enrich_resource(
    resources: list[dict],
    key: str,
    provider: ResourceProvider,
    llm: BaseChatModel = get_langchain_model()
) -> Optional[dict]:
    """
    Use an LLM to deduplicate and enrich a list of CareResource objects, returning a single merged version.
    """
    if not resources:
        return None

    try:
        # Prepare input string
        raw_resources_str = "\n\n".join([str(res) for res in resources])

        system_prompt = (
            "You are a smart data enrichment algorithm. Your task is to deduplicate and enrich overlapping resource entries. "
            "Each resource describes the same or related service but may contain missing or conflicting details. "
            "Your job is to intelligently combine the entries into a single, comprehensive version that retains the most accurate, complete, and specific information.\n\n"
            "Preserve accurate fields like phone, email, descriptions, URLs, tags, and categories. Prefer more complete or detailed descriptions. "
            "Remove empty or redundant values. Fill in missing fields using other entries if available.\n\n"
            "You must return a single JSON object that matches the CareResource schema. If unsure about a field, use `null` or leave it out."
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                (
                    "human",
                    "Here are multiple possibly overlapping resources for {key} from the same provider:\n\n{resources}\n\n"
                    "The provider is: {provider}\n\n"
                    "Please return ONE merged, enriched CareResource JSON object that takes the best from each."
                )
            ]
        )

        chain = prompt | llm.with_structured_output(CareResource)

        enriched: CareResource = await chain.ainvoke({
            "resources": raw_resources_str,
            "key": key,
            "provider": provider.model_dump_json()
        })

        return enriched.model_dump()

    except Exception as e:
        logger.error(f"LLM dedupe/enrichment failed: {e}", exc_info=True)
        return None

async def extract_with_llm(content: str, extraction_template: BaseModel, llm: BaseChatModel = get_langchain_model()) -> Optional[BaseModel]:
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

async def rank_pages_for_secondary_crawl(content: str, llm: BaseChatModel = get_langchain_model(), max_links_to_rank=5) -> List[str]:
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
            "content": content
        })

        # 4. Process result
        if output and output.ranked_urls:
            # Ensure we return between 0 and 5 URLs
            ranked_list = output.ranked_urls[:5]
            logger.info(f"LLM recommended secondary crawl URLs: {ranked_list}")
            return ranked_list
        else:
            logger.warning("LLM did not return a ranked list of URLs for secondary crawl.")
            return []

    except Exception as e:
        logger.error(f"Error ranking pages for secondary crawl: {e}", exc_info=True)
        return []

async def classify_resource_type_tags(content, llm: BaseChatModel = get_langchain_model()) -> Optional[TagOutput]:
    """
    Classifies the resource tag based on the provided content.

    Args:
        content: The content to classify.
        llm: The language model instance to use.

    Returns:
        The classified resource tag, or None if classification fails.
    """
    try:
        # Prepare the list of tags to show in the system prompt
        formatted_tags = "\n".join(f"- {tag}" for tag in TagType.__args__)

        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"You are an expert in classifying resources for caregivers, people with dementia, or older adults. "
                    f"Given the provided content, determine the most appropriate tag from the following list:\n\n{formatted_tags}\n\n"
                    "Return ONLY ONE tag from the list. If none fit, return None."
                ),
                (
                    "human",
                    "Here is the content to classify:\n{content}"
                ),
            ]
        )

        chain = prompt_template | llm.with_structured_output(TagOutput)

        output: Optional[TagOutput] = await chain.ainvoke({"content": content})

        return output

    except Exception as e:
        logger.error(f"Error classifying resource tag: {e}", exc_info=True)
        return None

async def classify_resource_type_detail(content, llm: BaseChatModel = get_langchain_model()) -> category:
    """
    Classifies the resource type based on the provided content.

    Args:
        content: The content to classify.
        llm: The language model instance to use.

    Returns:
        The classified resource type, or None if classification fails.
    """
    try:
        formatted_categories = "\n".join(
            [
                f"{category}:\n" + "\n".join([f"- {sub}" for sub in subcategories])
                for category, subcategories in RESOURCE_TYPE_CATEGORIES.items()
            ]
        )
        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"You are an expert in classifying resources for caregivers, people with dementia, or older adults. Given the provided content, determine the most appropriate resource category and subcategory from the following list:\n\n{formatted_categories}\n\n"
                    "Return ONLY ONE category name and ONE subcategory. If none of the categories fit, return None."
                ),
                (
                    "human",
                    "Here is the content to classify:\n{content}"
                ),
            ]
        )

        chain = prompt_template | llm.with_structured_output(category)

        output: Optional[Dict[str, str]] = await chain.ainvoke({
            "content": content
        })

        return output

    except Exception as e:
        logger.error(f"Error classifying resource type: {e}", exc_info=True)
        return None
