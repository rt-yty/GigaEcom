from pydantic import BaseModel, Field

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Название категории")
    description: str | None = Field(None, max_length=500, description="Описание категории")


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    is_deleted: bool = Field(default=False, description="Признак мягкого удаления")

    class Config:
        from_attributes = True


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Название продукта")
    description: str | None = Field(None, max_length=500, description="Описание продукта")
    price: float = Field(..., gt=0, description="Цена продукта (должна быть больше 0)")
    category_id: int = Field(..., description="ID категории")


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    price: float | None = Field(None, gt=0)
    category_id: int | None = Field(None)


class ProductResponse(ProductBase):
    id: int
    is_deleted: bool = Field(default=False, description="Признак мягкого удаления")

    class Config:
        from_attributes = True


class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, description="Текст сообщения для агента")
    thread_id: str | None = Field(None, description="ID потока для поддержания контекста беседы")


class ChatResponse(BaseModel):
    response: str = Field(..., description="Ответ агента")
    thread_id: str = Field(..., description="ID потока беседы")
