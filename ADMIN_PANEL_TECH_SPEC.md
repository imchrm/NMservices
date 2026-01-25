# Техническое задание: Admin Panel (React Admin)

**Версия:** 1.0
**Дата:** 2026-01-24
**Тип проекта:** Монорепозиторий (Backend + Frontend)
**Архитектура:** Вариант 2 - Монорепо для solo/small team

---

## 📋 Содержание

1. [Цель проекта](#цель-проекта)
2. [Текущее состояние](#текущее-состояние)
3. [Целевая архитектура](#целевая-архитектура)
4. [План миграции](#план-миграции)
5. [Технический стек Frontend](#технический-стек-frontend)
6. [Структура проекта](#структура-проекта)
7. [Функциональные требования](#функциональные-требования)
8. [Нефункциональные требования](#нефункциональные-требования)
9. [План разработки](#план-разработки)
10. [Развертывание](#развертывание)

---

## 🎯 Цель проекта

Создать web-интерфейс (Admin Panel) для удаленного управления базой данных NMservices с использованием существующего Admin API.

### Ключевые требования:
- ✅ Использовать существующий Admin API (уже реализован)
- ✅ Организовать код в монорепозиторий (Backend + Frontend)
- ✅ Минимизировать изменения в текущем backend коде
- ✅ Обеспечить возможность независимой разработки frontend/backend

---

## 📊 Текущее состояние

### Текущая структура репозитория:

```
NMservices/
├── .git/
├── src/nms/                    # Основной код backend
├── tests/                      # Тесты backend
├── scripts/                    # Утилиты и CLI
├── docs/                       # Документация
├── pyproject.toml              # Poetry зависимости
├── .env.example
├── .gitignore
├── README.md
├── DEPLOYMENT.md
├── ADMIN_API.md
└── ...
```

### Что уже реализовано:
- ✅ Admin API endpoints (REST API)
- ✅ Аутентификация через `X-Admin-Key`
- ✅ CRUD для Users и Orders
- ✅ Статистика БД
- ✅ Pydantic модели для всех операций
- ✅ Тестовые скрипты (Python, Bash)

---

## 🏗️ Целевая архитектура

### Новая структура монорепозитория:

```
NMservices/                              # Корень монорепо
│
├── .git/                                # Git (общий для всего)
├── .gitignore                           # Общий gitignore
├── README.md                            # Главный README проекта
│
├── backend/                             # ⬅️ Backend (FastAPI) - перемещен
│   ├── src/nms/                         # Код приложения
│   │   ├── api/
│   │   │   ├── admin/                   # Admin API endpoints
│   │   │   ├── users.py
│   │   │   ├── orders.py
│   │   │   └── dependencies.py
│   │   ├── models/
│   │   ├── services/
│   │   ├── database.py
│   │   ├── config.py
│   │   └── main.py
│   ├── tests/                           # Тесты backend
│   ├── scripts/                         # CLI утилиты
│   ├── docs/                            # Backend документация
│   ├── pyproject.toml                   # Python зависимости
│   ├── pytest.ini
│   ├── .env.example
│   ├── README.md                        # Backend README
│   ├── DEPLOYMENT.md
│   └── ADMIN_API.md
│
├── admin-panel/                         # ⬅️ Frontend (React Admin) - новый
│   ├── src/
│   │   ├── App.tsx                      # Главный компонент
│   │   ├── main.tsx                     # Entry point
│   │   ├── authProvider.ts              # Аутентификация
│   │   ├── dataProvider.ts              # API integration
│   │   ├── theme.ts                     # Material UI theme
│   │   │
│   │   ├── users/                       # User management
│   │   │   ├── UserList.tsx
│   │   │   ├── UserShow.tsx
│   │   │   ├── UserCreate.tsx
│   │   │   └── UserEdit.tsx
│   │   │
│   │   ├── orders/                      # Order management
│   │   │   ├── OrderList.tsx
│   │   │   ├── OrderShow.tsx
│   │   │   ├── OrderCreate.tsx
│   │   │   └── OrderEdit.tsx
│   │   │
│   │   └── dashboard/                   # Dashboard
│   │       └── Dashboard.tsx
│   │
│   ├── public/
│   │   └── favicon.ico
│   ├── index.html
│   ├── package.json                     # Node зависимости
│   ├── tsconfig.json                    # TypeScript config
│   ├── vite.config.ts                   # Vite bundler config
│   ├── .env.example                     # Frontend env vars
│   └── README.md                        # Frontend README
│
├── .vscode/                             # VS Code settings (опционально)
│   └── settings.json
│
└── docs/                                # Общая документация
    ├── ARCHITECTURE.md
    ├── MONOREPO_SETUP.md
    └── ADMIN_PANEL_TECH_SPEC.md         # Этот документ
```

---

## 🔄 План миграции

### Этап 1: Подготовка структуры (без изменения кода)

#### 1.1 Создать новые директории
```bash
mkdir backend
mkdir admin-panel
mkdir docs
```

#### 1.2 Переместить существующий backend код
```bash
# Переместить все файлы backend в новую директорию
git mv src backend/
git mv tests backend/
git mv scripts backend/
git mv pyproject.toml backend/
git mv pytest.ini backend/
git mv .env.example backend/

# Переместить backend документацию
git mv DEPLOYMENT.md backend/
git mv ADMIN_API.md backend/
git mv TESTING.md backend/
git mv CHANGELOG_ADMIN_API.md backend/
```

#### 1.3 Обновить пути в backend конфигурации

**backend/pyproject.toml:**
```toml
# Обновить пути (если нужно)
[tool.poetry]
packages = [{ include = "nms", from = "src" }]

[tool.pylint.main]
init-hook = "import sys; sys.path.append('src')"
```

#### 1.4 Создать корневой README.md
```markdown
# NMservices Monorepo

Backend (FastAPI) + Admin Panel (React Admin)

## Structure
- `/backend` - FastAPI backend with Admin API
- `/admin-panel` - React Admin web interface
- `/docs` - Shared documentation
```

### Этап 2: Создание Frontend структуры

#### 2.1 Инициализировать React Admin проект
```bash
cd admin-panel
npm create vite@latest . -- --template react-ts
npm install react-admin ra-data-simple-rest
npm install @mui/material @emotion/react @emotion/styled
```

#### 2.2 Создать базовую структуру файлов (см. раздел "Структура проекта")

### Этап 3: Интеграция

#### 3.1 Настроить CORS в backend

**backend/src/nms/main.py:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 3.2 Обновить .gitignore

**Корневой .gitignore:**
```
# Backend
backend/.env
backend/__pycache__/
backend/.pytest_cache/
backend/.ruff_cache/

# Frontend
admin-panel/node_modules/
admin-panel/dist/
admin-panel/.env.local
admin-panel/.vite/

# IDE
.vscode/
.idea/
```

### Этап 4: Проверка работоспособности

```bash
# Terminal 1: Backend
cd backend
poetry run nms

# Terminal 2: Frontend
cd admin-panel
npm run dev
```

---

## 🛠️ Технический стек Frontend

### Core
- **React** 18+ - UI библиотека
- **TypeScript** 5+ - Типизация
- **Vite** 5+ - Сборщик и dev server

### React Admin
- **react-admin** 4+ - Admin framework
- **ra-data-simple-rest** - REST data provider

### UI/UX
- **Material-UI (MUI)** 5+ - Компоненты
- **@emotion/react** - CSS-in-JS

### HTTP Client
- **axios** - HTTP запросы (используется react-admin)

### Development
- **ESLint** - Линтинг
- **Prettier** - Форматирование

---

## 📁 Структура проекта

### Frontend файлы (детально)

#### admin-panel/src/App.tsx
```typescript
import { Admin, Resource } from 'react-admin';
import { dataProvider } from './dataProvider';
import { authProvider } from './authProvider';
import { UserList, UserShow, UserCreate, UserEdit } from './users';
import { OrderList, OrderShow, OrderCreate, OrderEdit } from './orders';
import { Dashboard } from './dashboard';

export const App = () => (
  <Admin
    dataProvider={dataProvider}
    authProvider={authProvider}
    dashboard={Dashboard}
  >
    <Resource
      name="users"
      list={UserList}
      show={UserShow}
      create={UserCreate}
      edit={UserEdit}
    />
    <Resource
      name="orders"
      list={OrderList}
      show={OrderShow}
      create={OrderCreate}
      edit={OrderEdit}
    />
  </Admin>
);
```

#### admin-panel/src/authProvider.ts
```typescript
import { AuthProvider } from 'react-admin';

const ADMIN_KEY = localStorage.getItem('adminKey') || '';

export const authProvider: AuthProvider = {
  login: ({ username }) => {
    localStorage.setItem('adminKey', username);
    return Promise.resolve();
  },
  logout: () => {
    localStorage.removeItem('adminKey');
    return Promise.resolve();
  },
  checkAuth: () => {
    return localStorage.getItem('adminKey')
      ? Promise.resolve()
      : Promise.reject();
  },
  checkError: (error) => {
    if (error.status === 401 || error.status === 403) {
      localStorage.removeItem('adminKey');
      return Promise.reject();
    }
    return Promise.resolve();
  },
  getPermissions: () => Promise.resolve(),
};
```

#### admin-panel/src/dataProvider.ts
```typescript
import simpleRestProvider from 'ra-data-simple-rest';
import { fetchUtils } from 'react-admin';

const httpClient = (url: string, options: any = {}) => {
  const adminKey = localStorage.getItem('adminKey');
  if (!options.headers) {
    options.headers = new Headers({ Accept: 'application/json' });
  }
  options.headers.set('X-Admin-Key', adminKey);
  return fetchUtils.fetchJson(url, options);
};

export const dataProvider = simpleRestProvider(
  import.meta.env.VITE_API_URL || 'http://localhost:8000',
  httpClient
);
```

#### admin-panel/.env.example
```bash
VITE_API_URL=http://192.168.1.191:8000
```

#### admin-panel/package.json
```json
{
  "name": "nmservices-admin-panel",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx",
    "format": "prettier --write \"src/**/*.{ts,tsx}\""
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-admin": "^4.16.0",
    "ra-data-simple-rest": "^4.16.0",
    "@mui/material": "^5.15.0",
    "@emotion/react": "^11.11.0",
    "@emotion/styled": "^11.11.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "@vitejs/plugin-react": "^4.2.0",
    "eslint": "^8.56.0",
    "prettier": "^3.1.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0"
  }
}
```

---

## 🎯 Функциональные требования

### 1. Аутентификация
- [ ] Форма входа с полем для Admin Key
- [ ] Сохранение ключа в localStorage
- [ ] Автоматическая передача ключа в заголовке `X-Admin-Key`
- [ ] Редирект на /login при 401/403
- [ ] Кнопка Logout

### 2. Dashboard (главная страница)
- [ ] Карточки с метриками:
  - Всего пользователей
  - Всего заказов
  - Заказы по статусам (pending, completed, etc.)
- [ ] Графики (опционально):
  - Динамика создания заказов по дням
  - Распределение заказов по статусам (pie chart)

### 3. User Management (GET /admin/users)
- [ ] **Список пользователей (UserList)**
  - Таблица с колонками: ID, Phone, Created, Actions
  - Пагинация (10/25/50 на страницу)
  - Поиск по номеру телефона
  - Сортировка по ID, дате создания
  - Кнопки: Show, Edit, Delete

- [ ] **Просмотр пользователя (UserShow)**
  - Информация о пользователе
  - Список заказов пользователя (GET /admin/users/{id}/orders)
  - Кнопка "Создать заказ для этого пользователя"

- [ ] **Создание пользователя (UserCreate)**
  - Форма с полем: Phone Number
  - Валидация формата телефона
  - POST /admin/users

- [ ] **Редактирование пользователя (UserEdit)** (если добавится в API)
  - Форма редактирования телефона

- [ ] **Удаление пользователя**
  - Подтверждение: "Удалить пользователя и все его заказы?"
  - DELETE /admin/users/{id}

### 4. Order Management (GET /admin/orders)
- [ ] **Список заказов (OrderList)**
  - Таблица: ID, User ID, Status, Amount, Created, Actions
  - Пагинация
  - Фильтр по статусу (pending, completed, cancelled)
  - Поиск по User ID
  - Сортировка по дате, сумме
  - Цветовая индикация статусов (pending - yellow, completed - green)

- [ ] **Просмотр заказа (OrderShow)**
  - Детали заказа
  - Информация о пользователе (embedded)
  - История изменений (если добавится)

- [ ] **Создание заказа (OrderCreate)**
  - Форма:
    - User ID (dropdown с автокомплитом)
    - Status (dropdown: pending, completed, cancelled)
    - Total Amount (number)
    - Notes (textarea)
  - POST /admin/orders

- [ ] **Редактирование заказа (OrderEdit)**
  - Форма редактирования статуса, суммы, заметок
  - PATCH /admin/orders/{id}

- [ ] **Удаление заказа**
  - Подтверждение: "Удалить заказ #123?"
  - DELETE /admin/orders/{id}

### 5. Дополнительные функции
- [ ] Уведомления (success, error)
- [ ] Breadcrumbs навигация
- [ ] Кнопка "Обновить" данные
- [ ] Loader при загрузке данных
- [ ] Обработка ошибок API

---

## ⚙️ Нефункциональные требования

### Производительность
- [ ] Загрузка страницы < 2 секунд
- [ ] Отклик на действия < 200ms
- [ ] Lazy loading для больших списков

### UX/UI
- [ ] Адаптивный дизайн (desktop, tablet)
- [ ] Интуитивная навигация
- [ ] Consistent UI (Material Design)
- [ ] Темная/светлая тема (опционально)

### Безопасность
- [ ] Admin Key не хранится в коде
- [ ] Admin Key передается только в заголовках
- [ ] XSS защита (React автоматически)
- [ ] CSRF защита не требуется (API key based)

### Совместимость
- [ ] Chrome 100+
- [ ] Firefox 100+
- [ ] Safari 15+
- [ ] Edge 100+

### Документация
- [ ] README.md для frontend
- [ ] Инструкция по локальной разработке
- [ ] Инструкция по деплою

---

## 📅 План разработки

### Фаза 1: Подготовка (1 день)
- [ ] Реорганизация репозитория в монорепо
- [ ] Перемещение backend в `/backend`
- [ ] Создание структуры `/admin-panel`
- [ ] Проверка работоспособности backend после перемещения
- [ ] Обновление документации

### Фаза 2: Базовая настройка Frontend (1 день)
- [ ] Инициализация Vite + React + TypeScript
- [ ] Установка react-admin и зависимостей
- [ ] Настройка authProvider
- [ ] Настройка dataProvider
- [ ] Настройка CORS в backend
- [ ] Тестовый запуск и подключение к API

### Фаза 3: User Management (2 дня)
- [ ] UserList компонент
- [ ] UserShow компонент
- [ ] UserCreate компонент
- [ ] UserEdit компонент (если нужен)
- [ ] Интеграция с API endpoints
- [ ] Тестирование CRUD операций

### Фаза 4: Order Management (2 дня)
- [ ] OrderList компонент
- [ ] OrderShow компонент
- [ ] OrderCreate компонент
- [ ] OrderEdit компонент
- [ ] Фильтрация и поиск
- [ ] Интеграция с API endpoints

### Фаза 5: Dashboard (1 день)
- [ ] Карточки статистики
- [ ] Интеграция с GET /admin/stats
- [ ] Графики (опционально)

### Фаза 6: UI/UX polish (1 день)
- [ ] Настройка темы Material-UI
- [ ] Уведомления
- [ ] Обработка ошибок
- [ ] Breadcrumbs
- [ ] Responsive design

### Фаза 7: Тестирование и деплой (1 день)
- [ ] Тестирование всех функций
- [ ] Исправление багов
- [ ] Сборка production build
- [ ] Деплой на сервер 192.168.1.191
- [ ] Финальная документация

**Итого: 9 дней разработки**

---

## 🚀 Развертывание

### Development (локально)

#### Terminal 1: Backend
```bash
cd backend
poetry install
poetry run nms
# Запустится на http://localhost:8000
```

#### Terminal 2: Frontend
```bash
cd admin-panel
npm install
npm run dev
# Запустится на http://localhost:5173
```

### Production (сервер 192.168.1.191)

#### Вариант A: Раздельный деплой

**Backend:**
```bash
cd backend
poetry install
nohup poetry run nms > nms.log 2>&1 &
# http://192.168.1.191:8000
```

**Frontend:**
```bash
cd admin-panel
npm install
npm run build
# Раздать через nginx или serve
npm install -g serve
serve -s dist -p 3000
# http://192.168.1.191:3000
```

#### Вариант B: Nginx reverse proxy (рекомендуется)

**Nginx конфиг:**
```nginx
server {
    listen 80;
    server_name 192.168.1.191;

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Admin Panel (статика)
    location /admin {
        alias /path/to/NMservices/admin-panel/dist;
        try_files $uri $uri/ /admin/index.html;
    }

    # Root (API docs)
    location / {
        proxy_pass http://localhost:8000;
    }
}
```

**Доступ:**
- API: http://192.168.1.191/api
- Admin Panel: http://192.168.1.191/admin
- API Docs: http://192.168.1.191/docs

#### Вариант C: FastAPI раздает статику

**backend/src/nms/main.py:**
```python
from fastapi.staticfiles import StaticFiles
import os

# Проверить, существует ли собранный frontend
static_path = os.path.join(os.path.dirname(__file__), '../../admin-panel/dist')
if os.path.exists(static_path):
    app.mount("/admin", StaticFiles(directory=static_path, html=True), name="admin")
```

**Сборка и запуск:**
```bash
# 1. Собрать frontend
cd admin-panel
npm run build

# 2. Запустить backend (он раздаст frontend)
cd ../backend
poetry run nms
```

**Доступ:**
- Admin Panel: http://192.168.1.191:8000/admin
- API: http://192.168.1.191:8000/api
- API Docs: http://192.168.1.191:8000/docs

---

## 📋 Чеклист готовности

### Backend
- [ ] Backend перемещен в `/backend`
- [ ] Все пути обновлены
- [ ] CORS настроен
- [ ] Admin API работает
- [ ] Тесты проходят

### Frontend
- [ ] Структура проекта создана
- [ ] Зависимости установлены
- [ ] authProvider реализован
- [ ] dataProvider реализован
- [ ] Все CRUD операции работают
- [ ] Dashboard показывает статистику
- [ ] UI/UX доработан
- [ ] Production build успешен

### Документация
- [ ] README.md обновлен
- [ ] backend/README.md создан
- [ ] admin-panel/README.md создан
- [ ] MONOREPO_SETUP.md создан
- [ ] Инструкции по деплою обновлены

### Деплой
- [ ] Backend задеплоен
- [ ] Frontend задеплоен
- [ ] Nginx настроен (если используется)
- [ ] Проверена работа на продакшене

---

## 🔗 Ссылки

- [React Admin Documentation](https://marmelab.com/react-admin/)
- [Material-UI Documentation](https://mui.com/)
- [Vite Documentation](https://vitejs.dev/)
- [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/)

---

## 📝 Примечания

1. **Изменения в backend минимальны**: только добавление CORS middleware
2. **Backend API не меняется**: frontend использует существующий Admin API
3. **Независимая разработка**: frontend и backend можно развивать отдельно
4. **Git история сохраняется**: используем `git mv` для перемещения файлов
5. **Обратная совместимость**: можно вернуться к старой структуре, просто переместив файлы обратно

---

**Дата последнего обновления:** 2026-01-24
**Автор:** Claude Sonnet 4.5
**Статус:** Draft / Ready for Implementation
