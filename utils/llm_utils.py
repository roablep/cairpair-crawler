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
from pydantic import BaseModel, create_model

from config import RESOURCE_TYPE_CATEGORIES
from models.resource import CareResource, CareResources
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
    # return ChatGroq(model='deepseek-r1-distill-llama-70b', temperature=0.1, api_key=os.getenv("GROQ_API_KEY"), rate_limiter=rate_limiter)
    return ChatGoogleGenerativeAI(model='gemini-2.0-flash-lite', temperature=0.1, api_key=os.getenv("GOOGLE_API_KEY"), rate_limiter=rate_limiter)


async def dedupe_and_enrich_resources(
    resources: list[CareResource],
    key: str,
    provider: ResourceProvider,
    llm: BaseChatModel = get_langchain_model()
) -> List[Optional[CareResource]]:
    """
    Use an LLM to deduplicate and enrich a list of CareResource objects, returning a list of merged versions.
    FIXED: Now returns a list of CareResource, not a single one.
    """
    if not resources:
        return None

    if not provider:
        logger.warning(f"provider not provided for {key}, {resources}")

    if any(x is None for x in resources):
        logger.error(f"BUG 1: Null value in {resources}")

    try:
        # Prepare input string
        raw_resources_str = "\n\n".join([
            res.model_dump_json(exclude_unset=True, exclude_none=True) for res in resources
        ])

        system_prompt = (
            "You are a smart data enrichment algorithm. Your task is to deduplicate and enrich multiple potentially overlapping caregiving resource entries. "
            "Your goal is to return a list of cleaned, enriched, distinct CareResource objects. "
            "If multiple entries describe different resources, keep them separate. If entries overlap, merge them intelligently into a single object.\n\n"
            "Guidelines:\n"
            "- Preserve accurate fields like phone, email, descriptions, URLs, tags, and categories.\n"
            "- Prefer more complete or detailed descriptions.\n"
            "- Remove empty or redundant values.\n"
            "- Fill in missing fields using other entries if available.\n"
            "- Return a list of CareResource objects in valid JSON format.\n"
            "- IMPORTANT: Follow the CareResource schema strictly.\n"
            "- If unsure about a field, set it to null or leave it out."
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                (
                    "human",
                    "Here are multiple caregiving resources for {key} from the same provider:\n\n{resources}\n\n"
                    "The provider is: {provider}\n\n"
                    "Please return a list of merged, enriched CareResource JSON objects that takes the best from each."
                )
            ]
        )

        # Note: Output is now a List[CareResource], not single
        chain = prompt | llm.with_structured_output(CareResources)

        prompt_completion = {
            "resources": raw_resources_str,
            "key": key,
        }
        if provider:
            prompt_completion['provider'] = provider.model_dump_json()

        enriched_CareResources: CareResources = await chain.ainvoke(prompt_completion)
        enriched_resources = enriched_CareResources.resources

        if any(x is None for x in enriched_resources):
            logger.error(f"BUG 2: Null value in {enriched_resources}")

        return enriched_resources or []

    except Exception as e:
        logger.error(f"LLM dedupe/enrichment failed: {e}", exc_info=True)
        return None

async def extract_with_llm(
    content: str,
    extraction_template: BaseModel,
    llm: BaseChatModel = get_langchain_model(),
    per_field_mode: bool = False
) -> Optional[BaseModel]:
    """Processes HTML content with LangChain and the LLM."""
    if per_field_mode:
        field_values = {}

        # ✅ Important: Build a *temporary single-field schema* per field
        for field_name, field in type(extraction_template).model_fields.items():
            # Dynamically create a single-field Pydantic model for structured output
            SingleFieldModel = create_model(f"SingleFieldModel_{field_name}", **{field_name: (field.annotation, None)})

            field_prompt_template = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        f"You are an expert data extraction assistant. "
                        f"Your task is to extract **only the field** '{field_name}' from the following content.\nComform to the schema: {field}\nIf the field is not found or is unclear, respond with null."
                    ),
                    ("human", "{text}")
                ]
            )

            chain = field_prompt_template | llm.with_structured_output(SingleFieldModel)

            try:
                output = await chain.ainvoke({"text": content})
                # ✅ output is now a Pydantic model with the field name
                field_values[field_name] = getattr(output, field_name)
            except Exception as e:
                logger.error(f"Error extracting field {field_name}: {e}", exc_info=True)
                field_values[field_name] = None

        # Build and return the model
        try:
            return extraction_template(**field_values)
        except Exception as e:
            logger.error(f"Error building model from field values: {e}", exc_info=True)
            return None

    else:
        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an expert information extraction algorithm.
                    Your task is to extract caregiving resource data from the provided website text, field by field into a provided schema.

                    For each field in the schema:
                    1. Ask yourself: "Is this information explicitly or implicitly present?"
                    2. If yes, extract the value cleanly.
                    3. If no, set the value to null.
                    4. Do not guess if unsure.
                    Only extract relevant information from the text.
                    If you do not know the value of an attribute asked to extract, return null for the attribute's value.
                    Important:
                    - Stay focused.
                    - Be mechanical and disciplined.
                    - Do not invent information.
                    - Follow the schema order.""",
                ),
                ("human", "{text}"),
            ]
        )
        chain = prompt_template | llm.with_structured_output(extraction_template)

        try:
            output = await chain.ainvoke({"text": content})
            return output
        except Exception as e:
            logger.error(f"Langchain processing error: {e}", exc_info=True)
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

async def classify_resource_type_tags(content, llm: BaseChatModel = get_langchain_model()) -> Optional[TagType]:
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

        return output.tag if output else None

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
