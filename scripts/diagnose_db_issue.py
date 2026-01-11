"""
Быстрая диагностика проблемы с сохранением данных в PostgreSQL.

Использование:
    python scripts/diagnose_db_issue.py
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text, select

from nms.config import get_settings
from nms.models.db_models import User


async def diagnose():
    """Диагностирует проблему."""
    settings = get_settings()
    print(f"DATABASE_URL: {settings.database_url}")
    print("=" * 60)

    engine = create_async_engine(settings.database_url, echo=False)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session_maker() as session:
        print("\n1. Проверка структуры таблицы users...")
        print("-" * 60)

        result = await session.execute(
            text("""
                SELECT column_name, data_type, character_maximum_length,
                       is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'users'
                ORDER BY ordinal_position;
            """)
        )

        columns = result.fetchall()
        if not columns:
            print("❌ Таблица 'users' не найдена!")
            print("\nВероятно, таблицы не были созданы через SQLAlchemy.")
            print("Запустите: python scripts/recreate_database.py")
            return

        print("Структура таблицы 'users':")
        for col in columns:
            print(f"  {col[0]:15} {col[1]:20} max_len={col[2]} nullable={col[3]} default={col[4]}")

        print("\n2. Проверка количества записей...")
        print("-" * 60)

        result = await session.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar()
        print(f"Всего записей в таблице: {count}")

        print("\n3. Попытка вставки тестовой записи ЧЕРЕЗ SQLAlchemy ORM...")
        print("-" * 60)

        test_phone = "+998777777777"

        # Удаляем если уже есть
        await session.execute(text(f"DELETE FROM users WHERE phone_number = '{test_phone}'"))
        await session.commit()

        # Вставляем через ORM
        new_user = User(phone_number=test_phone)
        session.add(new_user)
        await session.flush()  # Получаем ID до коммита

        print(f"После flush: new_user.id = {new_user.id}")

        await session.commit()
        print(f"После commit: new_user.id = {new_user.id}")

        # Проверяем через SQL
        result = await session.execute(
            text(f"SELECT * FROM users WHERE phone_number = '{test_phone}'")
        )
        row = result.fetchone()

        if row:
            print(f"✅ Запись НАЙДЕНА в базе через SQL: {dict(row._mapping)}")
        else:
            print(f"❌ Запись НЕ НАЙДЕНА в базе через SQL!")
            print("   Возможные причины:")
            print("   1. Транзакция не коммитится")
            print("   2. Проблема с правами доступа")
            print("   3. Используется другая база данных")

        print("\n4. Попытка вставки НАПРЯМУЮ через SQL...")
        print("-" * 60)

        test_phone2 = "+998888888888"
        await session.execute(
            text(f"DELETE FROM users WHERE phone_number = '{test_phone2}'")
        )
        await session.execute(
            text(f"INSERT INTO users (phone_number, created_at, updated_at) "
                 f"VALUES ('{test_phone2}', NOW(), NOW())")
        )
        await session.commit()

        # Проверяем
        result = await session.execute(
            text(f"SELECT * FROM users WHERE phone_number = '{test_phone2}'")
        )
        row = result.fetchone()

        if row:
            print(f"✅ Запись через SQL НАЙДЕНА: {dict(row._mapping)}")
        else:
            print(f"❌ Запись через SQL НЕ НАЙДЕНА!")

        print("\n5. Все записи в таблице users:")
        print("-" * 60)
        result = await session.execute(text("SELECT * FROM users"))
        rows = result.fetchall()

        if rows:
            for row in rows:
                print(f"  {dict(row._mapping)}")
        else:
            print("  (таблица пуста)")

    await engine.dispose()

    print("\n" + "=" * 60)
    print("ДИАГНОСТИКА ЗАВЕРШЕНА")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(diagnose())
