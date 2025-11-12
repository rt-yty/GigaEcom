import json
from langchain_core.tools import StructuredTool

from .llm import llm
from ..db.session import AsyncSessionLocal
from ..crud import (
    create_category,
    create_product,
    get_category_by_name,
    get_category,
    get_product,
    update_category,
    update_product,
    delete_category,
    delete_product,
)
from ..schemas import (
    CategoryCreate,
    ProductCreate,
    CategoryUpdate,
    ProductUpdate,
)


def tool_response(success: bool, *, data: dict | None = None, error: str | None = None) -> str:
    payload: dict[str, object] = {"success": success}
    if data is not None:
        payload["data"] = data
    if error:
        payload["error"] = error
    return json.dumps(payload, ensure_ascii=False)


def serialize_category(category) -> dict:
    return {
        "id": category.id,
        "name": category.name,
        "description": category.description,
        "is_deleted": category.is_deleted,
    }


def serialize_product(product) -> dict:
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "category_id": product.category_id,
        "is_deleted": product.is_deleted,
    }


async def create_category_tool(name: str, description: str | None = None) -> str:
    async with AsyncSessionLocal() as db:
        try:
            category_data = CategoryCreate(name=name, description=description)
            category = await create_category(db, category_data)
            return tool_response(True, data=serialize_category(category))
        except Exception as e:
            return tool_response(False, error=f"Ошибка при создании категории: {str(e)}")


async def create_product_tool(
    name: str,
    price: float,
    category_id: int,
    description: str | None = None
) -> str:
    async with AsyncSessionLocal() as db:
        try:
            product_data = ProductCreate(
                name=name,
                price=price,
                category_id=category_id,
                description=description
            )
            product = await create_product(db, product_data)
            return tool_response(True, data=serialize_product(product))
        except Exception as e:
            return tool_response(False, error=f"Ошибка при создании продукта: {str(e)}")


async def update_category_tool(
    category_id: int,
    name: str | None = None,
    description: str | None = None
) -> str:
    if name is None and description is None:
        return tool_response(False, error="Нужно указать хотя бы одно поле для обновления категории")
    async with AsyncSessionLocal() as db:
        try:
            payload = CategoryUpdate(name=name, description=description)
            category = await update_category(db, category_id, payload)
            return tool_response(True, data=serialize_category(category))
        except ValueError as e:
            return tool_response(False, error=str(e))
        except Exception as e:
            return tool_response(False, error=f"Ошибка при обновлении категории: {str(e)}")


async def delete_category_tool(category_id: int) -> str:
    async with AsyncSessionLocal() as db:
        try:
            category = await delete_category(db, category_id)
            return tool_response(True, data=serialize_category(category))
        except ValueError as e:
            return tool_response(False, error=str(e))
        except Exception as e:
            return tool_response(False, error=f"Ошибка при удалении категории: {str(e)}")


async def get_category_id_by_name_tool(name: str) -> str:
    async with AsyncSessionLocal() as db:
        try:
            category = await get_category_by_name(db, name)
            if category:
                return tool_response(True, data=serialize_category(category))
            return tool_response(False, error=f"Категория '{name}' не найдена")
        except Exception as e:
            return tool_response(False, error=f"Ошибка при поиске категории: {str(e)}")


async def get_category_details_tool(category_id: int) -> str:
    async with AsyncSessionLocal() as db:
        try:
            category = await get_category(db, category_id)
            if not category:
                return tool_response(False, error=f"Категория с ID {category_id} не найдена")
            return tool_response(True, data=serialize_category(category))
        except Exception as e:
            return tool_response(False, error=f"Ошибка при получении категории: {str(e)}")


async def update_product_tool(
    product_id: int,
    name: str | None = None,
    description: str | None = None,
    price: float | None = None,
    category_id: int | None = None
) -> str:
    if all(value is None for value in [name, description, price, category_id]):
        return tool_response(False, error="Нужно указать хотя бы одно поле для обновления продукта")
    async with AsyncSessionLocal() as db:
        try:
            payload = ProductUpdate(
                name=name,
                description=description,
                price=price,
                category_id=category_id
            )
            product = await update_product(db, product_id, payload)
            return tool_response(True, data=serialize_product(product))
        except ValueError as e:
            return tool_response(False, error=str(e))
        except Exception as e:
            return tool_response(False, error=f"Ошибка при обновлении продукта: {str(e)}")


async def delete_product_tool(product_id: int) -> str:
    async with AsyncSessionLocal() as db:
        try:
            product = await delete_product(db, product_id)
            return tool_response(True, data=serialize_product(product))
        except ValueError as e:
            return tool_response(False, error=str(e))
        except Exception as e:
            return tool_response(False, error=f"Ошибка при удалении продукта: {str(e)}")


async def get_product_details_tool(product_id: int) -> str:
    async with AsyncSessionLocal() as db:
        try:
            product = await get_product(db, product_id)
            if not product:
                return tool_response(False, error=f"Продукт с ID {product_id} не найден")
            return tool_response(True, data=serialize_product(product))
        except Exception as e:
            return tool_response(False, error=f"Ошибка при получении продукта: {str(e)}")


create_category_tool_langchain = StructuredTool.from_function(
    name="create_category",
    description=(
        "Создает новую категорию товаров. Используй этот инструмент, "
        "когда пользователь просит создать категорию или добавить категорию."
    ),
    coroutine=create_category_tool,
)

create_product_tool_langchain = StructuredTool.from_function(
    name="create_product",
    description=(
        "Создает новый продукт. Требует category_id - сначала найди категорию "
        "или создай её. Используй этот инструмент, когда пользователь просит "
        "создать продукт, товар или добавить продукт."
    ),
    coroutine=create_product_tool,
)

get_category_id_tool_langchain = StructuredTool.from_function(
    name="get_category_id_by_name",
    description=(
        "Получает ID категории по её названию. Используй перед созданием продукта, "
        "чтобы узнать category_id. Если категории нет, создай её сначала."
    ),
    coroutine=get_category_id_by_name_tool,
)

update_category_tool_langchain = StructuredTool.from_function(
    name="update_category",
    description="Обновляет существующую категорию по ID.",
    coroutine=update_category_tool,
)

delete_category_tool_langchain = StructuredTool.from_function(
    name="delete_category",
    description="Мягко удаляет категорию и связанные продукты.",
    coroutine=delete_category_tool,
)

get_category_details_tool_langchain = StructuredTool.from_function(
    name="get_category",
    description="Возвращает данные категории по ID.",
    coroutine=get_category_details_tool,
)

update_product_tool_langchain = StructuredTool.from_function(
    name="update_product",
    description="Обновляет существующий продукт по ID.",
    coroutine=update_product_tool,
)

delete_product_tool_langchain = StructuredTool.from_function(
    name="delete_product",
    description="Мягко удаляет продукт и скрывает его из каталога.",
    coroutine=delete_product_tool,
)

get_product_details_tool_langchain = StructuredTool.from_function(
    name="get_product",
    description="Возвращает данные продукта по ID.",
    coroutine=get_product_details_tool,
)

tools = [
    create_category_tool_langchain,
    create_product_tool_langchain,
    get_category_id_tool_langchain,
    update_category_tool_langchain,
    delete_category_tool_langchain,
    get_category_details_tool_langchain,
    update_product_tool_langchain,
    delete_product_tool_langchain,
    get_product_details_tool_langchain,
]

llm_with_tools = llm.bind_tools(tools)
