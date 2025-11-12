import os
from dotenv import load_dotenv

from langchain_gigachat.chat_models import GigaChat

load_dotenv()

llm = GigaChat(
    credentials=os.getenv("GIGACHAT_TOKEN"),
    scope="GIGACHAT_API_PERS",
    model="GigaChat-2",
    verify_ssl_certs=False,
    temperature=0.1,
)

system_prompt = (
    "Отвечай кратко и по делу, причем только на просьбы сделать что-либо, связанное с товарами и категориями. "
    "Для управления каталогом применяй соответствующие инструменты: "
    "create_category, update_category, delete_category, get_category, get_category_id_by_name, "
    "create_product, update_product, delete_product, get_product. "
    "При создании продукта сначала найди или создай категорию и используй её ID. "
    "Сообщай пользователю результат операции и любые ошибки из инструментов."
)
