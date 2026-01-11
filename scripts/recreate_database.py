"""
Скрипт для пересоздания таблиц базы данных через SQLAlchemy.

ВАЖНО: Этот скрипт удалит все данные в таблице users!

Использование:
    python scripts/recreate_database.py
"""

import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text

# Импортируем модели
from nms.config import get_settings
from nms.database import Base
from nms.models.db_models import User  # Импортируем, чтобы модель зарегистрировалась


async def check_current_structure():
    """Проверяет текущую структуру таблицы users."""
    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=True)

    print("=" * 60)
    print("ТЕКУЩАЯ СТРУКТУРА ТАБЛИЦЫ users")
    print("=" * 60)

    async with engine.begin() as conn:
        # Проверяем существование таблицы
        result = await conn.execute(
            text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'users'
                ORDER BY ordinal_position;
            """)
        )
        columns = result.fetchall()

        if not columns:
            print("⚠️  Таблица 'users' не существует!")
            return False

        print("\nТекущие колонки в таблице 'users':")
        for col in columns:
            print(f"  - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")

        return True

    await engine.dispose()


async def recreate_tables():
    """Пересоздает все таблицы."""
    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=True)

    print("\n" + "=" * 60)
    print("ПЕРЕСОЗДАНИЕ ТАБЛИЦ")
    print("=" * 60)

    try:
        # Удаляем все таблицы
        print("\n1. Удаление существующих таблиц...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        print("✅ Таблицы удалены")

        # Создаем таблицы заново
        print("\n2. Создание таблиц из моделей SQLAlchemy...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Таблицы созданы")

        # Проверяем созданную структуру
        print("\n3. Проверка созданной структуры...")
        async with engine.begin() as conn:
            result = await conn.execute(
                text("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                      AND table_name = 'users'
                    ORDER BY ordinal_position;
                """)
            )
            columns = result.fetchall()

            print("\nСтруктура таблицы 'users' после пересоздания:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")

        print("\n✅ База данных успешно пересоздана!")
        return True

    except Exception as e:
        print(f"\n❌ Ошибка при пересоздании таблиц: {e}")
        return False

    finally:
        await engine.dispose()


async def test_insert():
    """Тестирует вставку записи напрямую."""
    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=True)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    print("\n" + "=" * 60)
    print("ТЕСТ ВСТАВКИ ЗАПИСИ")
    print("=" * 60)

    async with async_session_maker() as session:
        try:
            # Создаем тестового пользователя
            test_user = User(phone_number="+998999999999")
            session.add(test_user)
            await session.commit()
            await session.refresh(test_user)

            print(f"\n✅ Тестовый пользователь создан: ID={test_user.id}, phone={test_user.phone_number}")

            # Проверяем, что запись действительно в базе
            result = await session.execute(text("SELECT * FROM users WHERE phone_number = '+998999999999'"))
            row = result.fetchone()

            if row:
                print(f"✅ Запись найдена в базе: {dict(row._mapping)}")
            else:
                print("❌ Запись НЕ найдена в базе после коммита!")

            return True

        except Exception as e:
            print(f"\n❌ Ошибка при тестовой вставке: {e}")
            await session.rollback()
            return False

    await engine.dispose()


async def main():
    """Главная функция."""
    print("🔍 ДИАГНОСТИКА И ПЕРЕСОЗДАНИЕ БАЗЫ ДАННЫХ")
    print("=" * 60)

    # 1. Проверяем текущую структуру
    await check_current_structure()

    # 2. Спрашиваем подтверждение
    print("\n⚠️  ВНИМАНИЕ: Сейчас будут удалены ВСЕ данные в таблице users!")
    response = input("Продолжить? (yes/no): ").lower().strip()

    if response != "yes":
        print("❌ Операция отменена")
        sys.exit(0)

    # 3. Пересоздаем таблицы
    success = await recreate_tables()

    if not success:
        sys.exit(1)

    # 4. Тестируем вставку
    await test_insert()

    print("\n" + "=" * 60)
    print("✅ ВСЁ ГОТОВО!")
    print("=" * 60)
    print("\nТеперь попробуйте снова:")
    print("  curl -X POST http://127.0.0.1:8000/users/register \\")
    print("    -H 'X-API-Key: your_api_key' \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -d '{\"phone_number\": \"+998901234567\"}'")
    print()


if __name__ == "__main__":
    asyncio.run(main())
