from fastapi import APIRouter
from pydantic import BaseModel

from packages.database import Config, TheSession

router = APIRouter(
    prefix="/api/v1/config",
    tags=["config"],
)


class ConfigModel(BaseModel):
    chatgpt_key: str
    model: str
    pages_concurrency: int
    products_concurrency: int
    required: list[str]
    not_reprocess: list[str]
    description_prompt: str
    keywords_prompt: str
    properties_prompt: str


@router.get("/")
async def get_config() -> ConfigModel:
    """
    Get the current configuration.
    """

    with TheSession() as session:
        config = session.query(Config).first()

        if not config:
            config = Config(
                chatgpt_key="",
                model="gpt-3.5-turbo-1106",
                pages_concurrency=5,
                products_concurrency=30,
                required=["name", "description"],
                not_reprocess=["description", "properties", "keywords"],
                properties_prompt='You are a data scientist. You are given the set of data from the website and your goal is to extract the properties of the product from the text. You must respond with a valid JSON object, containing the dictionary of the extracted properties. For example: {"color": "red", "size": "small"}. If no properties can be found, respond with an empty dictionary.',
                description_prompt='You are a data scientist. You are given a product description and your goal is to normalize the text. Remove any shop-specific parts, keep only the relevant information and technical specs of the product to showcase to the customer. Respond with a valid JSON object containing a single field - "text" with the normalized text.',
                keywords_prompt='You are a data scientist. You are given a product description and your goal is to extract the keywords from the text. Respond with a valid JSON object containing a single field - "keywords" with a list of extracted keywords. If no specific keywords can be found, respond with an empty list.',
            )

            session.add(config)
            session.commit()

        return ConfigModel(
            chatgpt_key=config.chatgpt_key,
            model=config.model,
            pages_concurrency=config.pages_concurrency,
            products_concurrency=config.products_concurrency,
            required=config.required,
            not_reprocess=config.not_reprocess,
            description_prompt=config.description_prompt,
            keywords_prompt=config.keywords_prompt,
            properties_prompt=config.properties_prompt,
        )


@router.put("/")
async def update_config(config: ConfigModel) -> ConfigModel:
    """
    Update the configuration.
    """

    with TheSession() as session:
        db_config = session.query(Config).one()

        db_config.chatgpt_key = config.chatgpt_key
        db_config.model = config.model
        db_config.pages_concurrency = config.pages_concurrency
        db_config.products_concurrency = config.products_concurrency
        db_config.required = config.required
        db_config.not_reprocess = config.not_reprocess
        db_config.description_prompt = config.description_prompt
        db_config.keywords_prompt = config.keywords_prompt
        db_config.properties_prompt = config.properties_prompt

        session.commit()

    return config
