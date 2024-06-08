from typing import TypeVar

from pydantic import BaseModel, ValidationInfo, field_validator

T = TypeVar("T")


class SatuExport(BaseModel):
    Код_товара: int
    Название_позиции: str
    Поисковые_запросы: str
    Описание: str
    Тип_товара: str
    Цена: str
    Валюта: str
    Единица_измерения: str
    Минимальный_объем_заказа: str
    Оптовая_цена: str
    Минимальный_заказ_опт: str
    Ссылка_изображения: str
    Наличие: str
    Количество: str
    Номер_группы: int
    Название_группы: str
    Адрес_подраздела: str
    Возможность_поставки: str
    Срок_поставки: str
    Способ_упаковки: str
    Уникальный_идентификатор: int
    Идентификатор_товара: str
    Идентификатор_подраздела: int
    Идентификатор_группы: str
    Производитель: str
    Страна_производитель: str
    Скидка: str
    ID_группы_разновидностей: str
    Личные_заметки: str
    Продукт_на_сайте: str
    Срок_действия_скидки_от: str
    Срок_действия_скидки_до: str
    Цена_от: str
    Ярлык: str
    HTML_заголовок: str
    HTML_описание: str
    Код_маркировки_GTIN: str
    Номер_устройства_MPN: str
    Название_Характеристики: str
    Измерение_Характеристики: str
    Значение_Характеристики: str

    class Config:
        extra = "allow"

    @field_validator("*")
    def validate_fields(cls, value: T, info: ValidationInfo) -> T:
        if info.field_name is None:
            raise ValueError(f"Invalid field name: {info.field_name}")

        if "__" in info.field_name:
            name, num = info.field_name.split("__")
            if not num.isdigit() or name not in {
                "Название_Характеристики",
                "Измерение_Характеристики",
                "Значение_Характеристики",
            }:
                raise ValueError(f"Invalid field name: {info.field_name}")

        return value
