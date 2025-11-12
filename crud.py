from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Category, Product
from schemas import CategoryCreate, ProductCreate, CategoryUpdate, ProductUpdate


async def create_category(db: AsyncSession, category: CategoryCreate) -> Category:
    db_category = Category(**category.model_dump())
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category


async def get_category(
    db: AsyncSession,
    category_id: int,
    *,
    include_deleted: bool = False
) -> Category | None:
    stmt = select(Category).filter(Category.id == category_id)
    if not include_deleted:
        stmt = stmt.filter(Category.is_deleted.is_(False))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_category_by_name(
    db: AsyncSession,
    name: str,
    *,
    include_deleted: bool = False
) -> Category | None:
    stmt = select(Category).filter(Category.name == name)
    if not include_deleted:
        stmt = stmt.filter(Category.is_deleted.is_(False))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_category(
    db: AsyncSession,
    category_id: int,
    data: CategoryUpdate
) -> Category:
    category = await get_category(db, category_id)
    if not category:
        raise ValueError(f"Категория с ID {category_id} не найдена")

    updates = data.model_dump(exclude_unset=True)
    if updates:
        for field, value in updates.items():
            setattr(category, field, value)
        await db.commit()
        await db.refresh(category)
    return category


async def delete_category(db: AsyncSession, category_id: int) -> Category:
    category = await get_category(db, category_id)
    if not category:
        raise ValueError(f"Категория с ID {category_id} не найдена")

    category.is_deleted = True
    result = await db.execute(
        select(Product).filter(
            Product.category_id == category_id,
            Product.is_deleted.is_(False)
        )
    )
    for product in result.scalars().all():
        product.is_deleted = True
    await db.commit()
    await db.refresh(category)
    return category


async def create_product(db: AsyncSession, product: ProductCreate) -> Product:
    category = await get_category(db, product.category_id)
    if not category:
        raise ValueError(f"Категория с ID {product.category_id} не найдена")
    
    db_product = Product(**product.model_dump())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


async def get_product(
    db: AsyncSession,
    product_id: int,
    *,
    include_deleted: bool = False
) -> Product | None:
    stmt = select(Product).filter(Product.id == product_id)
    if not include_deleted:
        stmt = stmt.filter(Product.is_deleted.is_(False))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_product(
    db: AsyncSession,
    product_id: int,
    data: ProductUpdate
) -> Product:
    product = await get_product(db, product_id)
    if not product:
        raise ValueError(f"Продукт с ID {product_id} не найден")

    updates = data.model_dump(exclude_unset=True)
    if "category_id" in updates:
        category = await get_category(db, updates["category_id"])
        if not category:
            raise ValueError(f"Категория с ID {updates['category_id']} не найдена")

    if updates:
        for field, value in updates.items():
            setattr(product, field, value)
        await db.commit()
        await db.refresh(product)
    return product


async def delete_product(db: AsyncSession, product_id: int) -> Product:
    product = await get_product(db, product_id)
    if not product:
        raise ValueError(f"Продукт с ID {product_id} не найден")

    product.is_deleted = True
    await db.commit()
    await db.refresh(product)
    return product


async def get_all_categories(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Category]:
    result = await db.execute(
        select(Category)
        .filter(Category.is_deleted.is_(False))
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_all_products(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Product]:
    result = await db.execute(
        select(Product)
        .filter(Product.is_deleted.is_(False))
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())
