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


def print_menu():
    """Вывести меню."""
    print("\n📋 МЕНЮ:")
    print("  1 - Показать всех пользователей")
    print("  2 - Показать всех пользователей с их заказами")
    print("  3 - Показать все заказы")
    print("  4 - Создать новый заказ")
    print("  5 - Обновить статус заказа")
    print("  6 - Удалить заказ по ID")
    print("  0 - Выход")
    print()


def print_users(users):
    """Вывести список пользователей."""
    if not users:
        print("\n⚠️  Пользователей не найдено!")
        print("Создайте пользователя через API или скрипт recreate_database.py")
        return

    print("\n" + "-" * 60)
    print("ПОЛЬЗОВАТЕЛИ:")
    print("-" * 60)
    print(f"{'ID':<5} {'Телефон':<20} {'Дата создания':<20}")
    print("-" * 60)
    for user in users:
        created = user.created_at.strftime("%Y-%m-%d %H:%M:%S")
        print(f"{user.id:<5} {user.phone_number:<20} {created:<20}")
    print("-" * 60)


def print_users_with_orders(users_with_orders):
    """Вывести список пользователей с их заказами."""
    if not users_with_orders:
        print("\n⚠️  Пользователей не найдено!")
        print("Создайте пользователя через API или скрипт recreate_database.py")
        return

    print("\n" + "-" * 80)
    print("ПОЛЬЗОВАТЕЛИ И ЗАКАЗЫ:")
    print("-" * 80)
    print(f"{'ID':<5} {'Телефон':<20} {'Дата создания':<20}")
    print("-" * 80)

    for user, orders in users_with_orders:
        created = user.created_at.strftime("%Y-%m-%d %H:%M:%S")
        print(f"{user.id:<5} {user.phone_number:<20} {created:<20}")

        # Если у пользователя есть заказы, выводим их с отступом
        if orders:
            for order in orders:
                amount = f"{order.total_amount}" if order.total_amount else "—"
                print(f"  └─ ID: {order.id:<5} Статус: {order.status:<12} Сумма: {amount}")
        # Если заказов нет, переходим к следующему пользователю без вывода
    print("-" * 80)


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


async def main():
    """Главная функция."""
    print_header()

    manager = OrderManager()

    try:
        while True:
            print_menu()
            choice = input("Выберите действие: ").strip()

            if choice == "0":
                print("\n👋 До свидания!")
                break

            elif choice == "1":
                users = await manager.list_users()
                print_users(users)

            elif choice == "2":
                users_with_orders = await manager.list_users_with_orders()
                print_users_with_orders(users_with_orders)

            elif choice == "3":
                orders = await manager.list_orders()
                print_orders(orders)

            elif choice == "4":
                print("\n➕ СОЗДАНИЕ НОВОГО ЗАКАЗА")
                users = await manager.list_users()
                print_users(users)

                if not users:
                    continue

                try:
                    user_id = int(input("\nВведите ID пользователя: ").strip())
                    status = input("Введите статус (pending/confirmed/in_progress/completed/cancelled) [pending]: ").strip() or "pending"
                    amount_input = input("Введите сумму заказа (или Enter для пропуска): ").strip()
                    total_amount = float(amount_input) if amount_input else None
                    notes = input("Введите примечания (или Enter для пропуска): ").strip() or None

                    await manager.create_order(user_id, status, total_amount, notes)

                except ValueError:
                    print("❌ Ошибка: Некорректный ввод!")

            elif choice == "5":
                print("\n✏️  ОБНОВЛЕНИЕ СТАТУСА ЗАКАЗА")
                orders = await manager.list_orders()
                print_orders(orders)

                if not orders:
                    continue

                try:
                    order_id = int(input("\nВведите ID заказа: ").strip())
                    new_status = input("Введите новый статус (pending/confirmed/in_progress/completed/cancelled): ").strip()

                    if new_status not in VALID_STATUSES:
                        print("❌ Некорректный статус!")
                        continue

                    await manager.update_order_status(order_id, new_status)

                except ValueError:
                    print("❌ Ошибка: Некорректный ввод!")

            elif choice == "6":
                print("\n🗑️  УДАЛЕНИЕ ЗАКАЗА")
                orders = await manager.list_orders()
                print_orders(orders)

                if not orders:
                    continue

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
                print("❌ Неверный выбор! Попробуйте снова.")

    finally:
        await manager.close()


if __name__ == "__main__":
    asyncio.run(main())
