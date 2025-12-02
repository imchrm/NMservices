from pydantic import BaseModel

# Модель данных, приходящих от бота при регистрации
class UserRegistrationRequest(BaseModel):
    phone_number: str
    # Можно добавить chat_id или full_name, если нужно

# Модель ответа при регистрации
class RegistrationResponse(BaseModel):
    status: str
    message: str
    user_id: int  # Возвращаем ID созданного пользователя

# Модель данных для создания заказа
class OrderCreateRequest(BaseModel):
    user_id: int
    tariff_code: str  # например "standard_300"

# Модель ответа при создании заказа
class OrderResponse(BaseModel):
    status: str
    order_id: int
    message: str