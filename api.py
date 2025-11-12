from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)
from crud import (
    create_product,
    get_all_products,
    get_product,
    update_product,
    delete_product,
    create_category,
    get_all_categories,
    get_category,
    update_category,
    delete_category,
)

product_router = APIRouter(prefix="/products", tags=["products"])
category_router = APIRouter(prefix="/categories", tags=["categories"])


@product_router.post("/", response_model=ProductResponse, status_code=201)
async def create_product_endpoint(
    product: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        db_product = await create_product(db, product)
        return ProductResponse.model_validate(db_product)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@product_router.get("/", response_model=list[ProductResponse])
async def list_products(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    products = await get_all_products(db, skip=skip, limit=limit)
    return [ProductResponse.model_validate(prod) for prod in products]


@product_router.get("/{product_id}", response_model=ProductResponse)
async def get_product_endpoint(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    product = await get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Продукт не найден")
    return ProductResponse.model_validate(product)


@product_router.patch("/{product_id}", response_model=ProductResponse)
async def update_product_endpoint(
    product_id: int,
    updates: ProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    if not updates.model_dump(exclude_unset=True):
        raise HTTPException(status_code=400, detail="Не указано ни одно поле для обновления")
    try:
        product = await update_product(db, product_id, updates)
        return ProductResponse.model_validate(product)
    except ValueError as e:
        status = 404 if "не найд" in str(e).lower() else 400
        raise HTTPException(status_code=status, detail=str(e))


@product_router.delete("/{product_id}", response_model=ProductResponse)
async def delete_product_endpoint(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        product = await delete_product(db, product_id)
        return ProductResponse.model_validate(product)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@category_router.post("/", response_model=CategoryResponse, status_code=201)
async def create_category_endpoint(
    category: CategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        db_category = await create_category(db, category)
        return CategoryResponse.model_validate(db_category)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@category_router.get("/", response_model=list[CategoryResponse])
async def list_categories(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    categories = await get_all_categories(db, skip=skip, limit=limit)
    return [CategoryResponse.model_validate(cat) for cat in categories]


@category_router.get("/{category_id}", response_model=CategoryResponse)
async def get_category_endpoint_by_id(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    category = await get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    return CategoryResponse.model_validate(category)


@category_router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category_endpoint(
    category_id: int,
    updates: CategoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    if not updates.model_dump(exclude_unset=True):
        raise HTTPException(status_code=400, detail="Не указано ни одно поле для обновления")
    try:
        category = await update_category(db, category_id, updates)
        return CategoryResponse.model_validate(category)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@category_router.delete("/{category_id}", response_model=CategoryResponse)
async def delete_category_endpoint(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        category = await delete_category(db, category_id)
        return CategoryResponse.model_validate(category)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


routers = (product_router, category_router)
