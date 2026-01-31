"""
Database CLI - консольная утилита для управления БД NMservices.

Позволяет:
- Просматривать пользователей
- Просматривать пользователей с их заказами
- Просматривать все заказы
- Создавать новые заказы
- Обновлять статус заказов
- Удалять заказы

Использование:
    python scripts/db_cli.py
"""

import asyncio
# import os
# import sys
from decimal import Decimal
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

# Добавляем путь к папке src, чтобы Python видел пакет nms
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from nms.config import get_settings
from nms.models.db_models import User, Order


VALID_STATUSES = ["pending", "confirmed", "in_progress", "completed", "cancelled"]

class OrderManager:
    """Менеджер для работы с заказами."""

    def __init__(self):
        settings = get_settings()
        self.engine = create_async_engine(settings.database_url, echo=False)
        self.async_session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def close(self):
        """Закрыть соединение с БД."""
        await self.engine.dispose()

    async def list_users(self):
        """Получить список всех пользователей."""
        async with self.async_session_maker() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
            return users

    async def list_users_with_orders(self):
        """Получить список всех пользователей с их заказами."""
        async with self.async_session_maker() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()

            # Загружаем заказы для каждого пользователя
            users_with_orders = []
            for user in users:
                orders_result = await session.execute(
                    select(Order).where(Order.user_id == user.id).order_by(Order.created_at.desc())
                )
                user_orders = orders_result.scalars().all()
                users_with_orders.append((user, user_orders))

            return users_with_orders

    async def create_user(
        self,
        phone_number: str,
        telegram_id: int | None = None,
        language_code: str | None = None,
    ):
        """Создать нового пользователя."""
        async with self.async_session_maker() as session:
            try:
                # Проверяем, что пользователь не существует по номеру телефона
                result = await session.execute(
                    select(User).where(User.phone_number == phone_number)
                )
                existing_user = result.scalar_one_or_none()

                if existing_user:
                    print(f"❌ Ошибка: Пользователь с номером {phone_number} уже существует (ID: {existing_user.id})!")
                    return None

                # Проверяем, что пользователь не существует по telegram_id
                if telegram_id:
                    result = await session.execute(
                        select(User).where(User.telegram_id == telegram_id)
                    )
                    existing_user = result.scalar_one_or_none()
                    if existing_user:
                        print(f"❌ Ошибка: Пользователь с telegram_id {telegram_id} уже существует (ID: {existing_user.id})!")
                        return None

                # Создаем пользователя
                user = User(phone_number=phone_number, telegram_id=telegram_id, language_code=language_code)
                session.add(user)
                await session.commit()
                await session.refresh(user)

                tg_info = f", Telegram ID={user.telegram_id}" if user.telegram_id else ""
                lang_info = f", Язык={user.language_code}" if user.language_code else ""
                print(f"✅ Пользователь создан: ID={user.id}, Телефон={user.phone_number}{tg_info}{lang_info}")
                return user

            except SQLAlchemyError as e:
                print(f"❌ Ошибка при создании пользователя: {e}")
                await session.rollback()
                return None

    async def get_user_by_id(self, user_id: int):
        """Получить пользователя по ID."""
        async with self.async_session_maker() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()

    async def delete_user(self, user_id: int):
        """Удалить пользователя по ID."""
        async with self.async_session_maker() as session:
            try:
                result = await session.execute(
                    select(User).where(User.id == user_id)
                )
                user = result.scalar_one_or_none()

                if not user:
                    print(f"❌ Ошибка: Пользователь с ID {user_id} не найден!")
                    return False

                # Получаем количество заказов пользователя
                orders_result = await session.execute(
                    select(Order).where(Order.user_id == user_id)
                )
                orders_count = len(orders_result.scalars().all())

                await session.delete(user)
                await session.commit()

                if orders_count > 0:
                    print(f"✅ Пользователь {user_id} удален вместе с {orders_count} заказами")
                else:
                    print(f"✅ Пользователь {user_id} удален")
                return True

            except SQLAlchemyError as e:
                print(f"❌ Ошибка при удалении пользователя: {e}")
                await session.rollback()
                return False

    async def list_orders(self):
        """Получить список всех заказов."""
        async with self.async_session_maker() as session:
            result = await session.execute(
                select(Order).order_by(Order.created_at.desc())
            )
            orders = result.scalars().all()
            return orders

    async def get_order_by_id(self, order_id: int):
        """Получить заказ по ID."""
        async with self.async_session_maker() as session:
            result = await session.execute(
                select(Order).where(Order.id == order_id)
            )
            order = result.scalar_one_or_none()
            return order

    async def create_order(
        self,
        user_id: int,
        status: str = "pending",
        total_amount: float | None = None,
        notes: str | None = None
    ):
        """Создать новый заказ."""
        if status not in VALID_STATUSES:
            print(f"❌ Ошибка: Недопустимый статус '{status}'")
            return None

        async with self.async_session_maker() as session:
            try:
                # Проверяем, что пользователь существует
                result = await session.execute(
                    select(User).where(User.id == user_id)
                )
                user = result.scalar_one_or_none()

                if not user:
                    print(f"❌ Ошибка: Пользователь с ID {user_id} не найден!")
                    return None

                # Создаем заказ
                order = Order(
                    user_id=user_id,
                    status=status,
                    total_amount=Decimal(str(total_amount)) if total_amount else None,
                    notes=notes
                )
                session.add(order)
                await session.commit()
                await session.refresh(order)

                print(f"✅ Заказ создан: ID={order.id}")
                return order

            except SQLAlchemyError as e:
                print(f"❌ Ошибка при создании заказа: {e}")
                await session.rollback()
                return None

    async def update_order_status(self, order_id: int, new_status: str):
        """Обновить статус заказа."""
        if new_status not in VALID_STATUSES:
            print(f"❌ Ошибка: Недопустимый статус '{new_status}'")
            return False

        async with self.async_session_maker() as session:
            try:
                result = await session.execute(
                    select(Order).where(Order.id == order_id)
                )
                order = result.scalar_one_or_none()

                if not order:
                    print(f"❌ Ошибка: Заказ с ID {order_id} не найден!")
                    return False

                old_status = order.status
                order.status = new_status
                await session.commit()

                print(f"✅ Статус заказа {order_id} изменен: {old_status} → {new_status}")
                return True

            except SQLAlchemyError as e:
                print(f"❌ Ошибка при обновлении статуса: {e}")
                await session.rollback()
                return False

    async def delete_order(self, order_id: int):
        """Удалить заказ по ID."""
        async with self.async_session_maker() as session:
            try:
                result = await session.execute(
                    select(Order).where(Order.id == order_id)
                )
                order = result.scalar_one_or_none()

                if not order:
                    print(f"❌ Ошибка: Заказ с ID {order_id} не найден!")
                    return False

                await session.delete(order)
                await session.commit()

                print(f"✅ Заказ {order_id} удален")
                return True

            except SQLAlchemyError as e:
                print(f"❌ Ошибка при удалении заказа: {e}")
                await session.rollback()
                return False


def print_header():
    """Вывести заголовок."""
    print("\n" + "=" * 60)
    print("  DATABASE CLI - УПРАВЛЕНИЕ БД NMSERVICES")
    print("=" * 60)


def print_main_menu():
    """Вывести главное меню."""
    print("\n📋 ГЛАВНОЕ МЕНЮ:")
    print("1. Пользователи")
    print("   a. показать всех")
    print("   b. показать всех с заказами")
    print("   c. создать нового")
    print("   d. удалить по ID")
    print("2. Заказы")
    print("   a. показать все")
    print("   b. создать новый")
    print("   c. обновить")
    print("   d. удалить по ID")
    print("0. Выход")
    print()


def print_users_submenu():
    """Вывести подменю пользователей."""
    print("\n👥 ПОЛЬЗОВАТЕЛИ:")
    print("   a. показать всех")
    print("   b. показать всех с заказами")
    print("   c. создать нового")
    print("   d. удалить по ID")
    print("0. вернуться")
    print()


def print_orders_submenu():
    """Вывести подменю заказов."""
    print("\n📦 ЗАКАЗЫ:")
    print("   a. показать все")
    print("   b. создать новый")
    print("   c. обновить")
    print("   d. удалить по ID")
    print("0. вернуться")
    print()


def print_users(users):
    """Вывести список пользователей."""
    if not users:
        print("\n⚠️  Пользователей не найдено!")
        print("Создайте пользователя через API или скрипт recreate_database.py")
        return

    print("\n" + "-" * 90)
    print("ПОЛЬЗОВАТЕЛИ:")
    print("-" * 90)
    print(f"{'ID':<5} {'Телефон':<20} {'Telegram ID':<15} {'Язык':<6} {'Дата создания':<20}")
    print("-" * 90)
    for user in users:
        created = user.created_at.strftime("%Y-%m-%d %H:%M:%S")
        tg_id = str(user.telegram_id) if user.telegram_id else "—"
        lang = user.language_code if user.language_code else "—"
        print(f"{user.id:<5} {user.phone_number:<20} {tg_id:<15} {lang:<6} {created:<20}")
    print("-" * 90)


def print_users_with_orders(users_with_orders):
    """Вывести список пользователей с их заказами."""
    if not users_with_orders:
        print("\n⚠️  Пользователей не найдено!")
        print("Создайте пользователя через API или скрипт recreate_database.py")
        return

    print("\n" + "-" * 95)
    print("ПОЛЬЗОВАТЕЛИ И ЗАКАЗЫ:")
    print("-" * 95)
    print(f"{'ID':<5} {'Телефон':<20} {'Telegram ID':<15} {'Дата создания':<20}")
    print("-" * 95)

    for user, orders in users_with_orders:
        created = user.created_at.strftime("%Y-%m-%d %H:%M:%S")
        tg_id = str(user.telegram_id) if user.telegram_id else "—"
        print(f"{user.id:<5} {user.phone_number:<20} {tg_id:<15} {created:<20}")

        # Если у пользователя есть заказы, выводим их с отступом
        if orders:
            for order in orders:
                amount = f"{order.total_amount}" if order.total_amount else "—"
                print(f"  └─ ID: {order.id:<5} Статус: {order.status:<12} Сумма: {amount}")
        # Если заказов нет, переходим к следующему пользователю без вывода
    print("-" * 95)


def print_orders(orders):
    """Вывести список заказов."""
    if not orders:
        print("\n⚠️  Заказов не найдено!")
        return

    print("\n" + "-" * 80)
    print("ЗАКАЗЫ:")
    print("-" * 80)
    print(f"{'ID':<5} {'User ID':<8} {'Статус':<12} {'Сумма':<12} {'Примечания':<20}")
    print("-" * 80)
    for order in orders:
        order_id = order.id
        user_id = order.user_id
        status = order.status
        amount = f"{order.total_amount}" if order.total_amount else "—"
        notes = (order.notes[:17] + "...") if order.notes and len(order.notes) > 20 else (order.notes or "—")
        print(f"{order_id:<5} {user_id:<8} {status:<12} {amount:<12} {notes:<20}")
    print("-" * 80)


async def handle_users_menu(manager: OrderManager, subchoice: str = None):
    """Обработать меню пользователей."""
    if subchoice is None:
        print_users_submenu()
        subchoice = input("Выберите действие: ").strip().lower()

    if subchoice == "0":
        return
    elif subchoice == "a":
        users = await manager.list_users()
        print_users(users)
    elif subchoice == "b":
        users_with_orders = await manager.list_users_with_orders()
        print_users_with_orders(users_with_orders)
    elif subchoice == "c":
        print("\n➕ СОЗДАНИЕ НОВОГО ПОЛЬЗОВАТЕЛЯ")
        try:
            phone_number = input("Введите номер телефона (например, +998901234567): ").strip()

            if not phone_number:
                print("❌ Ошибка: Номер телефона не может быть пустым!")
                return

            telegram_id_input = input("Введите Telegram ID (или Enter для пропуска): ").strip()
            telegram_id = int(telegram_id_input) if telegram_id_input else None

            print("Выберите язык:")
            print("  1 или ru - Русский")
            print("  2 или uz - Узбекский")
            print("  3 или en - English")
            print("  0 или Enter - Пропустить")
            lang_choice = input("Ваш выбор [0]: ").strip().lower()

            language_code = None
            if lang_choice in ("1", "ru"):
                language_code = "ru"
            elif lang_choice in ("2", "uz"):
                language_code = "uz"
            elif lang_choice in ("3", "en"):
                language_code = "en"

            await manager.create_user(phone_number, telegram_id, language_code)

        except ValueError:
            print("❌ Ошибка: Telegram ID должен быть числом!")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    elif subchoice == "d":
        print("\n🗑️  УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ")
        users = await manager.list_users()
        print_users(users)

        if not users:
            return

        try:
            user_id = int(input("\nВведите ID пользователя для удаления: ").strip())

            # Получаем пользователя для подтверждения
            user = await manager.get_user_by_id(user_id)

            if not user:
                print(f"❌ Пользователь с ID {user_id} не найден!")
                return

            confirm = input(f"Вы уверены, что хотите удалить пользователя: {user_id} с номером телефона: {user.phone_number}? (yes/no): ").lower().strip()

            if confirm == "yes":
                await manager.delete_user(user_id)
            else:
                print("❌ Удаление отменено")

        except ValueError:
            print("❌ Ошибка: Некорректный ввод!")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    else:
        print("❌ Неверный выбор!")


async def handle_orders_menu(manager: OrderManager, subchoice: str = None):
    """Обработать меню заказов."""
    if subchoice is None:
        print_orders_submenu()
        subchoice = input("Выберите действие: ").strip().lower()

    if subchoice == "0":
        return
    elif subchoice == "a":
        orders = await manager.list_orders()
        print_orders(orders)
    elif subchoice == "b":
        print("\n➕ СОЗДАНИЕ НОВОГО ЗАКАЗА")
        users = await manager.list_users()
        print_users(users)

        if not users:
            return

        try:
            user_id = int(input("\nВведите ID пользователя: ").strip())
            status = input("Введите статус (pending/confirmed/in_progress/completed/cancelled) [pending]: ").strip() or "pending"
            amount_input = input("Введите сумму заказа (или Enter для пропуска): ").strip()
            total_amount = float(amount_input) if amount_input else None
            notes = input("Введите примечания (или Enter для пропуска): ").strip() or None

            await manager.create_order(user_id, status, total_amount, notes)

        except ValueError:
            print("❌ Ошибка: Некорректный ввод!")

    elif subchoice == "c":
        print("\n✏️  ОБНОВЛЕНИЕ СТАТУСА ЗАКАЗА")
        orders = await manager.list_orders()
        print_orders(orders)

        if not orders:
            return

        try:
            order_id = int(input("\nВведите ID заказа: ").strip())
            new_status = input("Введите новый статус (pending/confirmed/in_progress/completed/cancelled): ").strip()

            if new_status not in VALID_STATUSES:
                print("❌ Некорректный статус!")
                return

            await manager.update_order_status(order_id, new_status)

        except ValueError:
            print("❌ Ошибка: Некорректный ввод!")

    elif subchoice == "d":
        print("\n🗑️  УДАЛЕНИЕ ЗАКАЗА")
        orders = await manager.list_orders()
        print_orders(orders)

        if not orders:
            return

        try:
            order_id = int(input("\nВведите ID заказа для удаления: ").strip())
            confirm = input(f"Вы уверены, что хотите удалить заказ {order_id}? (yes/no): ").lower().strip()

            if confirm == "yes":
                await manager.delete_order(order_id)
            else:
                print("❌ Удаление отменено")

        except ValueError:
            print("❌ Ошибка: Некорректный ввод!")
    else:
        print("❌ Неверный выбор!")


async def main():
    """Главная функция."""
    print_header()

    manager = OrderManager()

    try:
        while True:
            print_main_menu()
            choice = input("Выберите действие: ").strip().lower()

            if choice == "0":
                print("\n👋 До свидания!")
                break

            # Обработка комбинированных команд (1a, 2b и т.д.)
            elif len(choice) == 2 and choice[0] in ["1", "2"] and choice[1] in ["a", "b", "c", "d"]:
                if choice[0] == "1":
                    await handle_users_menu(manager, choice[1])
                elif choice[0] == "2":
                    await handle_orders_menu(manager, choice[1])

            # Обработка главного меню
            elif choice == "1":
                await handle_users_menu(manager)

            elif choice == "2":
                await handle_orders_menu(manager)

            else:
                print("❌ Неверный выбор! Попробуйте снова.")

    finally:
        await manager.close()


if __name__ == "__main__":
    asyncio.run(main())
