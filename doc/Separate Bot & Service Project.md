### 1\. Стоит ли делать это отдельным проектом?

**Однозначно ДА.**

Вы абсолютно правы, планируя создать отдельный репозиторий `NMservis`. Это классическая клиент-серверная архитектура:

* **Telegram-бот (`@nomus_uz_bot`)** — это **Фронтенд** (клиент). Он отвечает только за отображение кнопок и отправку данных.  
* **NMservis** — это **Бэкенд** (сервер). Он отвечает за логику, хранение данных и интеграции.

**Почему это важно даже для PoC:**

1. **Масштабируемость:** На этапе MVP или позже вы захотите сделать мобильное приложение или сайт. Они будут обращаться к тому же `NMservis`, что и бот.  
2. **Безопасность:** Логика платежей и базы данных должна быть спрятана на сервере, а не в коде бота.  
3. **Независимость:** Вы сможете обновлять логику расчета тарифов на сервере, не перезагружая бота.

### 2\. Как лучше начать проект микросервиса на Python?

Для реализации задач PoC (этап 0\) и последующего перехода в MVP, лучшим выбором будет связка:

* **Язык:** Python 3.11+  
* **Фреймворк:** **FastAPI**.

**Почему FastAPI?**

* Он очень быстрый и современный.  
* Он "из коробки" создает документацию (Swagger UI), что идеально для тестирования заглушек. Вы сможете зайти в браузер и нажимать кнопки "Execute", чтобы проверить, как работает ваш API, даже не запуская бота.  
* Легко писать асинхронный код (как и в боте).

### 3\. План старта и структура `NMservis`

Вот пошаговая инструкция, как организовать этот проект на GitHub.

#### Шаг A: Структура папок

Создайте репозиторий `NMservis` со следующей структурой. Это "чистая архитектура" в миниатюре, готовая к росту.

| `NMservis/ ├── app/ │   ├── __init__.py │   ├── main.py            # Точка входа в приложение │   ├── models.py          # Pydantic модели (структура данных запросов/ответов) │   └── services/          # Бизнес-логика │       ├── __init__.py │       ├── auth.py        # Логика регистрации (заглушка SMS тут) │       └── orders.py      # Логика заказов (заглушка оплаты тут) ├── requirements.txt       # Зависимости ├── .gitignore └── README.md` |
| :---- |

#### Шаг B: Зависимости (`requirements.txt`)

Вам понадобится минимум библиотек для PoC:

fastapi

uvicorn\[standard\]

pydantic

#### Шаг C: Реализация кода (Скелет для PoC)

Вот готовый пример кода, который покрывает требования вашего документа "PoC \- Проверка технической концепции".

**1\. `app/models.py` (Описываем данные, которыми обмениваемся)**

from pydantic import BaseModel

\# Модель данных, приходящих от бота при регистрации

class UserRegistrationRequest(BaseModel):

    phone\_number: str

    \# Можно добавить chat\_id или full\_name, если нужно

\# Модель ответа при регистрации

class RegistrationResponse(BaseModel):

    status: str

    message: str

    user\_id: int  \# Возвращаем ID созданного пользователя

\# Модель данных для создания заказа

class OrderCreateRequest(BaseModel):

    user\_id: int

    tariff\_code: str  \# например "standard\_300"

\# Модель ответа при создании заказа

class OrderResponse(BaseModel):

    status: str

    order\_id: int

    message: str

**2\. `app/main.py` (Сам микросервис с эндпоинтами)**

from fastapi import FastAPI

from app.models import UserRegistrationRequest, RegistrationResponse, OrderCreateRequest, OrderResponse

import random

import time

app \= FastAPI(title="NoMus Backend API (PoC)")

\# \--- MOCKS / STUBS (Заглушки) \---

def mock\_sms\_service(phone: str):

    """Имитация отправки СМС"""

    print(f"\[STUB-SMS\] Sending code to {phone}...")

    return True

def mock\_payment\_service(amount: int):

    """Имитация оплаты"""

    print(f"\[STUB-PAYMENT\] Processing payment of {amount} sum...")

    time.sleep(1) \# Имитация задержки сети

    return True

def mock\_db\_save\_user(phone: str):

    """Имитация сохранения юзера в БД"""

    fake\_id \= random.randint(1000, 9999\)

    print(f"\[STUB-DB\] User {phone} saved with ID {fake\_id}")

    return fake\_id

def mock\_db\_save\_order(user\_id: int, tariff: str):

    """Имитация сохранения заказа"""

    fake\_order\_id \= random.randint(100, 999\)

    print(f"\[STUB-DB\] Order \#{fake\_order\_id} created for User {user\_id} (Tariff: {tariff})")

    print(f"\[STUB-NOTIFY\] Dispatcher notified about Order \#{fake\_order\_id}")

    return fake\_order\_id

\# \--- ENDPOINTS (Точки входа для Бота) \---

@app.get("/")

async def root():

    return {"message": "NoMus API is running"}

@app.post("/register", response\_model=RegistrationResponse)

async def register\_user(request: UserRegistrationRequest):

    \# 1\. Логика заглушки SMS (хоть по сценарию бот сам проверяет код,

    \# но регистрация факта подтвержденного номера происходит здесь)

    mock\_sms\_service(request.phone\_number)

    

    \# 2\. Логика заглушки БД

    user\_id \= mock\_db\_save\_user(request.phone\_number)

    

    return RegistrationResponse(

        status="ok",

        message="User registered successfully",

        user\_id=user\_id

    )

@app.post("/create\_order", response\_model=OrderResponse)

async def create\_order(request: OrderCreateRequest):

    \# 1\. Логика заглушки оплаты

    \# Допустим, тариф 'standard' стоит 300 руб (или сум)

    mock\_payment\_service(300)

    

    \# 2\. Логика заглушки БД и Уведомлений

    order\_id \= mock\_db\_save\_order(request.user\_id, request.tariff\_code)

    

    return OrderResponse(

        status="ok",

        order\_id=order\_id,

        message="Order created and payment processed"

    )

### 4\. Как это связать с Ботом?

Когда вы запустите этот сервис (локально или на сервере), у вас будет адрес, например: `http://localhost:8000`.

В коде **Бота** (в файле `infrastructure` или `services`) вы будете использовать библиотеку `aiohttp` или `requests`, чтобы стучаться сюда:

* Когда юзер ввел верный код \-\> Бот шлет POST запрос на `http://localhost:8000/register`.  
* Когда юзер нажал "Оплатить" \-\> Бот шлет POST запрос на `http://localhost:8000/create_order`.

### Следующие шаги для вас:

1. Создайте репозиторий `NMservis` на GitHub.  
2. Скопируйте структуру и код выше.  
3. Запустите локально командой: `uvicorn app.main:app --reload`.  
4. Откройте в браузере `http://127.0.0.1:8000/docs`. Вы увидите красивую документацию API и сможете "подергать" ручки `/register` и `/create_order`, чтобы убедиться, что они отдают JSON-ответы, как в вашем ТЗ.

Это будет идеальным выполнением "Этапа 0: PoC".  
