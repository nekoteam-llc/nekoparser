import asyncio
import functools
from typing import Optional, TypeVar

from deep_translator import GoogleTranslator
from pydantic import BaseModel, Field

T = TypeVar("T")


class UserFilledData(BaseModel):
    name: str = Field(description="name of the product")
    sku: str = Field(description="SKU (артикул)")
    price: float = Field(description="price")
    measure_unit: str = Field(description="measure unit")
    currency: str = Field(description="currency")
    description: str = Field(description="description")
    properties: str = Field(description="properties")
    main_image: str = Field(description="main image")


class SatuExport(UserFilledData):
    id: int = Field(description="ID of the product on Satu.kz")
    external_id: Optional[str] = Field(description="External ID of the product")
    keywords: Optional[str] = Field(description="Keywords of the product")
    name_multilang: Optional[dict[str, str]] = Field(
        description="Name of the product in multiple languages"
    )
    description_multilang: Optional[dict[str, str]] = Field(
        description="Description of the product in multiple languages"
    )

    async def translate(self, lang: str = "kz") -> None:
        """
        Translate name and description fields to selected language
        """

        translator = GoogleTranslator(source="ru", target=lang)
        self.name_multilang = {
            "ru": self.name,
            lang: await asyncio.get_event_loop().run_in_executor(
                None,
                functools.partial(translator.translate, self.name),
            ),
        }
        self.description_multilang = {
            "ru": self.description,
            lang: await asyncio.get_event_loop().run_in_executor(
                None,
                functools.partial(translator.translate, self.description),
            ),
        }
