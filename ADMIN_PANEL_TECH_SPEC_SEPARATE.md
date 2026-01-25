# Техническое задание: Admin Panel (React Admin) - Раздельные проекты

**Версия:** 1.0
**Дата:** 2026-01-25
**Тип проекта:** Раздельные репозитории (Backend + Frontend)
**Архитектура:** Вариант 1 - Полностью раздельные проекты

---

## 📋 Содержание

1. [Цель проекта](#цель-проекта)
2. [Текущее состояние](#текущее-состояние)
3. [Целевая архитектура](#целевая-архитектура)
4. [План реализации](#план-реализации)
5. [Технический стек Frontend](#технический-стек-frontend)
6. [Структура проектов](#структура-проектов)
7. [Функциональные требования](#функциональные-требования)
8. [Интеграция Backend-Frontend](#интеграция-backend-frontend)
9. [Развертывание](#развертывание)
10. [CI/CD](#cicd)
11. [План разработки](#план-разработки)

---

## 🎯 Цель проекта

Создать web-интерфейс (Admin Panel) для удаленного управления базой данных NMservices с использованием существующего Admin API как **отдельный независимый проект**.

### Ключевые требования:
- ✅ Использовать существующий Admin API (без изменений в backend)
- ✅ Полная независимость frontend и backend проектов
- ✅ Раздельные репозитории
- ✅ Независимое версионирование
- ✅ Независимый деплой

### Преимущества раздельных проектов:
- 🎯 **Чистое разделение ответственности** - backend и frontend живут отдельно
- 🚀 **Независимый деплой** - можно обновлять frontend без остановки backend
- 👥 **Параллельная разработка** - разные команды/разработчики
- 📦 **Независимое версионирование** - свои релизы и changelog
- 🔧 **Гибкость инфраструктуры** - можно деплоить на разные сервера/CDN
- 🌐 **Frontend можно хостить на Vercel/Netlify** - бесплатный SSL, CDN, автодеплой

---

## 📊 Текущее состояние

### Существующий репозиторий: NMservices (Backend)

```
NMservices/                         # Существующий backend репозиторий
├── .git/
├── src/nms/                        # Backend код
│   ├── api/
│   │   ├── admin/                  # ✅ Admin API уже реализован
│   │   │   ├── users.py
│   │   │   └── orders.py
│   │   ├── users.py
│   │   └── orders.py
│   ├── models/
│   │   └── admin.py                # ✅ Admin модели
│   ├── services/
│   ├── config.py
│   └── main.py
├── tests/
├── scripts/
├── pyproject.toml
├── ADMIN_API.md                    # ✅ Документация API
└── README.md
```

### Что уже реализовано в Backend:
- ✅ Admin API endpoints (REST API)
- ✅ Аутентификация через `X-Admin-Key`
- ✅ CRUD для Users: GET/POST /admin/users, GET/DELETE /admin/users/{id}
- ✅ CRUD для Orders: GET/POST /admin/orders, GET/PATCH/DELETE /admin/orders/{id}
- ✅ Статистика: GET /admin/stats
- ✅ Pydantic модели для всех операций
- ✅ Документация в ADMIN_API.md

### Что НЕ нужно менять в Backend:
- ❌ Структуру репозитория
- ❌ API endpoints
- ❌ Модели данных
- ❌ Код приложения

### Что нужно добавить в Backend (минимально):
- ✅ CORS middleware для разрешения запросов с frontend
- ✅ Настройка allowed origins в .env

---

## 🏗️ Целевая архитектура

### Два независимых репозитория:

#### 1. NMservices (Backend) - Без изменений структуры

```
NMservices/                         # ⬅️ Существующий репозиторий (БЕЗ ИЗМЕНЕНИЙ)
├── .git/
├── src/nms/
│   ├── api/admin/                  # Admin API endpoints
│   ├── models/admin.py
│   ├── main.py                     # ⬅️ Добавим только CORS middleware
│   └── ...
├── tests/
├── scripts/
├── pyproject.toml
├── .env.example                    # ⬅️ Добавим CORS_ORIGINS
├── ADMIN_API.md
└── README.md
```

**URL:** `http://192.168.1.191:8000` или `https://api.nmservices.uz`

---

#### 2. NMservices-Admin (Frontend) - Новый репозиторий

```
NMservices-Admin/                   # ⬅️ НОВЫЙ РЕПОЗИТОРИЙ
├── .git/                           # Отдельный Git
├── src/
│   ├── App.tsx                     # React Admin setup
│   ├── main.tsx                    # Entry point
│   ├── vite-env.d.ts
│   │
│   ├── providers/
│   │   ├── authProvider.ts         # Аутентификация (X-Admin-Key)
│   │   └── dataProvider.ts         # API integration
│   │
│   ├── theme/
│   │   └── theme.ts                # Material-UI theme
│   │
│   ├── layout/
│   │   ├── CustomLayout.tsx        # Custom layout
│   │   └── CustomAppBar.tsx        # App bar с логотипом
│   │
│   ├── dashboard/
│   │   └── Dashboard.tsx           # Главная страница со статистикой
│   │
│   ├── users/                      # User management
│   │   ├── UserList.tsx            # Список пользователей
│   │   ├── UserShow.tsx            # Просмотр пользователя
│   │   ├── UserCreate.tsx          # Создание пользователя
│   │   └── UserEdit.tsx            # Редактирование (если нужно)
│   │
│   ├── orders/                     # Order management
│   │   ├── OrderList.tsx           # Список заказов
│   │   ├── OrderShow.tsx           # Просмотр заказа
│   │   ├── OrderCreate.tsx         # Создание заказа
│   │   └── OrderEdit.tsx           # Редактирование заказа
│   │
│   └── types/
│       ├── user.ts                 # TypeScript типы для User
│       └── order.ts                # TypeScript типы для Order
│
├── public/
│   ├── favicon.ico
│   └── logo.png
│
├── index.html
├── package.json                    # Node.js зависимости
├── package-lock.json
├── tsconfig.json                   # TypeScript config
├── tsconfig.node.json
├── vite.config.ts                  # Vite bundler config
├── .env.example                    # Пример конфигурации
├── .gitignore
├── README.md                       # Frontend документация
├── DEPLOYMENT.md                   # Инструкции по деплою
└── LICENSE
```

**URL:** `http://192.168.1.191:3000` или `https://admin.nmservices.uz`

---

### Взаимодействие проектов:

```
┌─────────────────────────────────────────────────────────────┐
│                        User Browser                          │
│                    http://admin.nmservices.uz                │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ HTTP Requests
                           │ (с заголовком X-Admin-Key)
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              NMservices Backend (FastAPI)                    │
│                 http://api.nmservices.uz                     │
│                                                              │
│  Endpoints:                                                  │
│  • GET  /admin/users                                         │
│  • POST /admin/users                                         │
│  • GET  /admin/orders                                        │
│  • PATCH /admin/orders/{id}                                  │
│  • GET  /admin/stats                                         │
│  • ...                                                       │
│                                                              │
│  CORS: allow_origins=["https://admin.nmservices.uz"]       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │   PostgreSQL    │
                  │   Database      │
                  └─────────────────┘
```

---

## 🔄 План реализации

### Этап 1: Подготовка Backend (30 минут)

**НЕ требуется изменение структуры**, только небольшие дополнения:

#### 1.1 Добавить CORS middleware

**src/nms/main.py:**
```python
from fastapi.middleware.cors import CORSMiddleware

# ... существующий код ...

# Add CORS middleware (ДОБАВИТЬ после создания app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # Из .env
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ... остальной код без изменений ...
```

#### 1.2 Добавить настройки CORS в config

**src/nms/config.py:**
```python
class Settings(BaseSettings):
    # ... существующие настройки ...

    # CORS settings
    cors_origins: list[str] = Field(
        default=["http://localhost:5173"],  # Vite dev server по умолчанию
        alias="CORS_ORIGINS"
    )
```

#### 1.3 Обновить .env.example

**.env.example:**
```bash
# API Security
API_SECRET_KEY=your_secret_key_here
ADMIN_SECRET_KEY=your_admin_secret_key_here

# CORS (comma-separated list)
CORS_ORIGINS=http://localhost:5173,https://admin.nmservices.uz

# ... остальное без изменений ...
```

#### 1.4 Обновить README.md

Добавить ссылку на frontend репозиторий:

```markdown
## Related Projects

- **Admin Panel:** [NMservices-Admin](https://github.com/username/NMservices-Admin) - Web interface for database management
```

**Итого изменений в Backend:**
- ✅ 5-10 строк в main.py (CORS middleware)
- ✅ 5 строк в config.py (настройка cors_origins)
- ✅ 1 строка в .env.example
- ✅ 2 строки в README.md

**Структура репозитория остается БЕЗ ИЗМЕНЕНИЙ!**

---

### Этап 2: Создание Frontend репозитория (1 день)

#### 2.1 Создать новый репозиторий на GitHub/GitLab

```bash
# На вашем компьютере или GitHub
Repository name: NMservices-Admin
Description: Admin Panel for NMservices - React Admin web interface
Visibility: Private (или Public)
```

#### 2.2 Клонировать и инициализировать проект

```bash
# Клонировать пустой репозиторий
git clone https://github.com/username/NMservices-Admin.git
cd NMservices-Admin

# Инициализировать Vite + React + TypeScript
npm create vite@latest . -- --template react-ts

# Установить зависимости
npm install

# Установить React Admin и зависимости
npm install react-admin ra-data-simple-rest
npm install @mui/material @emotion/react @emotion/styled
npm install @mui/icons-material
```

#### 2.3 Создать структуру файлов

```bash
# Создать директории
mkdir -p src/providers
mkdir -p src/users
mkdir -p src/orders
mkdir -p src/dashboard
mkdir -p src/layout
mkdir -p src/theme
mkdir -p src/types
```

---

## 🛠️ Технический стек Frontend

### Core
- **React** 18.2+ - UI библиотека
- **TypeScript** 5.3+ - Типизация
- **Vite** 5.0+ - Сборщик и dev server (быстрее чем Webpack)

### React Admin
- **react-admin** 4.16+ - Admin framework
- **ra-data-simple-rest** 4.16+ - REST data provider

### UI/UX
- **Material-UI (MUI)** 5.15+ - Компоненты
- **@mui/icons-material** - Иконки
- **@emotion/react** + **@emotion/styled** - CSS-in-JS

### HTTP
- **fetch API** (встроенный) - используется react-admin

### Dev Tools
- **ESLint** - Линтинг TypeScript/React
- **Prettier** - Форматирование кода
- **TypeScript** - Проверка типов

---

## 📁 Структура проектов (детально)

### Backend: NMservices (БЕЗ ИЗМЕНЕНИЙ структуры)

```
NMservices/
├── src/nms/
│   ├── api/
│   │   ├── admin/
│   │   │   ├── __init__.py
│   │   │   ├── users.py          # ✅ Готово
│   │   │   └── orders.py         # ✅ Готово
│   │   ├── dependencies.py       # ✅ get_admin_key готово
│   │   ├── users.py
│   │   └── orders.py
│   ├── models/
│   │   ├── admin.py              # ✅ Все модели готовы
│   │   └── ...
│   ├── main.py                   # ⬅️ Добавим CORS (5 строк)
│   └── config.py                 # ⬅️ Добавим cors_origins (5 строк)
└── ...
```

---

### Frontend: NMservices-Admin (НОВЫЙ проект)

#### package.json
```json
{
  "name": "nmservices-admin",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "format": "prettier --write \"src/**/*.{ts,tsx,json,css}\""
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-admin": "^4.16.0",
    "ra-data-simple-rest": "^4.16.0",
    "@mui/material": "^5.15.0",
    "@mui/icons-material": "^5.15.0",
    "@emotion/react": "^11.11.0",
    "@emotion/styled": "^11.11.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@typescript-eslint/eslint-plugin": "^6.14.0",
    "@typescript-eslint/parser": "^6.14.0",
    "@vitejs/plugin-react": "^4.2.1",
    "eslint": "^8.55.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.5",
    "prettier": "^3.1.0",
    "typescript": "^5.2.2",
    "vite": "^5.0.8"
  }
}
```

#### src/App.tsx
```typescript
import { Admin, Resource } from 'react-admin';
import { dataProvider } from './providers/dataProvider';
import { authProvider } from './providers/authProvider';
import { Dashboard } from './dashboard/Dashboard';
import { UserList, UserShow, UserCreate } from './users';
import { OrderList, OrderShow, OrderCreate, OrderEdit } from './orders';
import PeopleIcon from '@mui/icons-material/People';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';

export const App = () => (
  <Admin
    dataProvider={dataProvider}
    authProvider={authProvider}
    dashboard={Dashboard}
    title="NMservices Admin"
  >
    <Resource
      name="admin/users"
      options={{ label: 'Users' }}
      list={UserList}
      show={UserShow}
      create={UserCreate}
      icon={PeopleIcon}
    />
    <Resource
      name="admin/orders"
      options={{ label: 'Orders' }}
      list={OrderList}
      show={OrderShow}
      create={OrderCreate}
      edit={OrderEdit}
      icon={ShoppingCartIcon}
    />
  </Admin>
);
```

#### src/providers/authProvider.ts
```typescript
import { AuthProvider } from 'react-admin';

const ADMIN_KEY_STORAGE = 'nmservices_admin_key';

export const authProvider: AuthProvider = {
  // Вызывается при отправке формы логина
  login: ({ username }: { username: string }) => {
    localStorage.setItem(ADMIN_KEY_STORAGE, username);
    return Promise.resolve();
  },

  // Вызывается при клике на logout
  logout: () => {
    localStorage.removeItem(ADMIN_KEY_STORAGE);
    return Promise.resolve();
  },

  // Вызывается при старте приложения
  checkAuth: () => {
    return localStorage.getItem(ADMIN_KEY_STORAGE)
      ? Promise.resolve()
      : Promise.reject({ message: 'Login required' });
  },

  // Вызывается при HTTP ошибке от сервера
  checkError: (error: any) => {
    const status = error.status;
    if (status === 401 || status === 403) {
      localStorage.removeItem(ADMIN_KEY_STORAGE);
      return Promise.reject({ message: 'Invalid credentials' });
    }
    return Promise.resolve();
  },

  // Опционально: права доступа
  getPermissions: () => Promise.resolve(),

  // Опционально: информация о пользователе
  getIdentity: () =>
    Promise.resolve({
      id: 'admin',
      fullName: 'Administrator',
    }),
};
```

#### src/providers/dataProvider.ts
```typescript
import simpleRestProvider from 'ra-data-simple-rest';
import { fetchUtils, DataProvider } from 'react-admin';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const ADMIN_KEY_STORAGE = 'nmservices_admin_key';

// Custom httpClient для добавления X-Admin-Key header
const httpClient = (url: string, options: fetchUtils.Options = {}) => {
  const adminKey = localStorage.getItem(ADMIN_KEY_STORAGE);

  if (!options.headers) {
    options.headers = new Headers({ Accept: 'application/json' });
  }

  const headers = options.headers as Headers;
  headers.set('X-Admin-Key', adminKey || '');

  return fetchUtils.fetchJson(url, options);
};

const baseDataProvider = simpleRestProvider(API_URL, httpClient);

// Кастомизация для работы с нашим API
export const dataProvider: DataProvider = {
  ...baseDataProvider,

  // Переопределение getList для правильной работы с пагинацией
  getList: (resource, params) => {
    const { page, perPage } = params.pagination;
    const skip = (page - 1) * perPage;
    const limit = perPage;

    const url = `${API_URL}/${resource}?skip=${skip}&limit=${limit}`;

    return httpClient(url).then(({ json }) => {
      // Наш API возвращает { users: [...], total: 10 } или { orders: [...], total: 20 }
      const dataKey = resource.includes('users') ? 'users' : 'orders';

      return {
        data: json[dataKey] || [],
        total: json.total || 0,
      };
    });
  },

  // Переопределение getOne для работы с нашим API
  getOne: (resource, params) => {
    const url = `${API_URL}/${resource}/${params.id}`;
    return httpClient(url).then(({ json }) => ({
      data: json,
    }));
  },

  // update для PATCH вместо PUT
  update: (resource, params) => {
    const url = `${API_URL}/${resource}/${params.id}`;
    return httpClient(url, {
      method: 'PATCH',
      body: JSON.stringify(params.data),
    }).then(({ json }) => ({ data: json }));
  },
};
```

#### .env.example
```bash
# Backend API URL
VITE_API_URL=http://192.168.1.191:8000

# For production
# VITE_API_URL=https://api.nmservices.uz
```

#### vite.config.ts
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true, // Слушать на всех интерфейсах
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
});
```

#### tsconfig.json
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,

    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",

    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

#### src/users/UserList.tsx
```typescript
import { List, Datagrid, TextField, DateField, EmailField } from 'react-admin';

export const UserList = () => (
  <List>
    <Datagrid rowClick="show">
      <TextField source="id" />
      <EmailField source="phone_number" label="Phone" />
      <DateField source="created_at" showTime />
      <DateField source="updated_at" showTime />
    </Datagrid>
  </List>
);
```

#### src/users/UserShow.tsx
```typescript
import {
  Show,
  SimpleShowLayout,
  TextField,
  DateField,
  ReferenceManyField,
  Datagrid,
} from 'react-admin';

export const UserShow = () => (
  <Show>
    <SimpleShowLayout>
      <TextField source="id" />
      <TextField source="phone_number" label="Phone Number" />
      <DateField source="created_at" showTime />
      <DateField source="updated_at" showTime />

      <ReferenceManyField
        label="Orders"
        reference="admin/orders"
        target="user_id"
      >
        <Datagrid>
          <TextField source="id" />
          <TextField source="status" />
          <TextField source="total_amount" />
          <DateField source="created_at" />
        </Datagrid>
      </ReferenceManyField>
    </SimpleShowLayout>
  </Show>
);
```

#### src/users/UserCreate.tsx
```typescript
import { Create, SimpleForm, TextInput, required } from 'react-admin';

const validatePhone = [required(), /* можно добавить regex валидацию */];

export const UserCreate = () => (
  <Create>
    <SimpleForm>
      <TextInput source="phone_number" validate={validatePhone} />
    </SimpleForm>
  </Create>
);
```

#### src/users/index.ts
```typescript
export { UserList } from './UserList';
export { UserShow } from './UserShow';
export { UserCreate } from './UserCreate';
```

#### src/types/user.ts
```typescript
export interface User {
  id: number;
  phone_number: string;
  created_at: string;
  updated_at: string;
}
```

#### src/types/order.ts
```typescript
export interface Order {
  id: number;
  user_id: number;
  status: string;
  total_amount: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}
```

#### README.md (Frontend)
```markdown
# NMservices Admin Panel

React Admin web interface for NMservices database management.

## Quick Start

### Development

```bash
npm install
cp .env.example .env
npm run dev
```

Open http://localhost:5173

### Login

Enter your Admin API key in the login form.

## Build

```bash
npm run build
```

Output: `dist/`

## Related Projects

- **Backend API:** [NMservices](https://github.com/username/NMservices)
```

---

## 🎯 Функциональные требования

### 1. Аутентификация
- [x] Форма входа с полем для Admin Key
- [x] Сохранение ключа в localStorage
- [x] Передача ключа в заголовке `X-Admin-Key`
- [x] Редирект на /login при 401/403
- [x] Кнопка Logout

### 2. Dashboard
- [ ] Карточки статистики (total_users, total_orders, orders_by_status)
- [ ] GET /admin/stats

### 3. User Management
- [ ] UserList - таблица с пагинацией
- [ ] UserShow - детали + список заказов
- [ ] UserCreate - форма создания
- [ ] UserDelete - с подтверждением

### 4. Order Management
- [ ] OrderList - таблица с фильтром по статусу
- [ ] OrderShow - детали заказа с информацией о пользователе
- [ ] OrderCreate - форма создания
- [ ] OrderEdit - форма редактирования (PATCH)
- [ ] OrderDelete - с подтверждением

### 5. UI/UX
- [ ] Material Design
- [ ] Breadcrumbs навигация
- [ ] Notifications (success/error)
- [ ] Loading states
- [ ] Error handling

---

## 🔗 Интеграция Backend-Frontend

### API Endpoints mapping

| Frontend Resource | Backend Endpoint | Method | React Admin Action |
|------------------|------------------|--------|-------------------|
| admin/users | GET /admin/users?skip=0&limit=25 | GET | getList |
| admin/users | POST /admin/users | POST | create |
| admin/users/{id} | GET /admin/users/{id} | GET | getOne |
| admin/users/{id} | DELETE /admin/users/{id} | DELETE | delete |
| admin/orders | GET /admin/orders?skip=0&limit=25 | GET | getList |
| admin/orders | POST /admin/orders | POST | create |
| admin/orders/{id} | GET /admin/orders/{id} | GET | getOne |
| admin/orders/{id} | PATCH /admin/orders/{id} | PATCH | update |
| admin/orders/{id} | DELETE /admin/orders/{id} | DELETE | delete |
| admin/stats | GET /admin/stats | GET | custom call |

### CORS настройка

**Backend (.env):**
```bash
CORS_ORIGINS=http://localhost:5173,https://admin.nmservices.uz
```

**Frontend (.env):**
```bash
VITE_API_URL=http://192.168.1.191:8000
```

---

## 🚀 Развертывание

### Development

**Terminal 1: Backend**
```bash
cd NMservices
poetry run nms
# http://localhost:8000
```

**Terminal 2: Frontend**
```bash
cd NMservices-Admin
npm run dev
# http://localhost:5173
```

---

### Production

#### Вариант A: Традиционный VPS

**Backend на 192.168.1.191:8000:**
```bash
cd NMservices
poetry install
nohup poetry run nms > nms.log 2>&1 &
```

**Frontend на 192.168.1.191:3000:**
```bash
cd NMservices-Admin
npm install
npm run build
npm install -g serve
serve -s dist -p 3000
```

**Nginx:**
```nginx
server {
    listen 80;
    server_name nmservices.uz;

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
    }

    location /admin-api {
        proxy_pass http://localhost:8000/admin;
    }

    # Admin Panel
    location /admin {
        proxy_pass http://localhost:3000;
    }
}
```

#### Вариант B: Frontend на Vercel/Netlify (Рекомендуется) ⭐

**Backend:** VPS (192.168.1.191:8000) или cloud

**Frontend:** Vercel (бесплатно)

**Преимущества:**
- ✅ Бесплатный хостинг frontend
- ✅ Автоматический HTTPS
- ✅ CDN (быстрая загрузка)
- ✅ Автодеплой при push в main

**Настройка Vercel:**
```bash
cd NMservices-Admin
npm install -g vercel
vercel login
vercel

# Environment variables в Vercel dashboard:
# VITE_API_URL=https://api.nmservices.uz
```

**После деплоя:**
- Frontend: `https://nmservices-admin.vercel.app`
- Backend: `https://api.nmservices.uz`

**Обновить CORS в backend .env:**
```bash
CORS_ORIGINS=https://nmservices-admin.vercel.app
```

#### Вариант C: Оба на одном VPS через nginx

```nginx
server {
    listen 80;
    server_name admin.nmservices.uz;

    # Frontend (static files)
    root /var/www/nmservices-admin/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}

server {
    listen 80;
    server_name api.nmservices.uz;

    # Backend API
    location / {
        proxy_pass http://localhost:8000;
    }
}
```

---

## 🔄 CI/CD

### Backend: NMservices

**.github/workflows/deploy-backend.yml:**
```yaml
name: Deploy Backend

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to VPS
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd /home/user/NMservices
            git pull
            poetry install
            sudo systemctl restart nmservices
```

### Frontend: NMservices-Admin

**Вариант A: Auto-deploy через Vercel**
- Просто push в main → автоматический деплой

**Вариант B: GitHub Actions для VPS**

**.github/workflows/deploy-frontend.yml:**
```yaml
name: Deploy Frontend

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install and Build
        run: |
          npm ci
          npm run build

      - name: Deploy to VPS
        uses: appleboy/scp-action@master
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          source: "dist/*"
          target: "/var/www/nmservices-admin/"
```

---

## 📅 План разработки

### Фаза 0: Подготовка Backend (30 минут)
- [x] Добавить CORS middleware в main.py
- [x] Добавить cors_origins в config.py
- [x] Обновить .env.example
- [x] Протестировать API с CORS

### Фаза 1: Инициализация Frontend (1 час)
- [ ] Создать репозиторий NMservices-Admin на GitHub
- [ ] Инициализировать Vite + React + TypeScript
- [ ] Установить react-admin и зависимости
- [ ] Создать базовую структуру директорий

### Фаза 2: Базовая настройка (2 часа)
- [ ] authProvider.ts
- [ ] dataProvider.ts
- [ ] App.tsx с базовой конфигурацией
- [ ] Тестовый запуск и подключение к API
- [ ] Login форма

### Фаза 3: User Management (4 часа)
- [ ] UserList компонент
- [ ] UserShow компонент
- [ ] UserCreate компонент
- [ ] Тестирование CRUD

### Фаза 4: Order Management (4 часа)
- [ ] OrderList с фильтрацией
- [ ] OrderShow компонент
- [ ] OrderCreate компонент
- [ ] OrderEdit компонент (PATCH)
- [ ] Тестирование CRUD

### Фаза 5: Dashboard (2 часа)
- [ ] Dashboard компонент
- [ ] Карточки статистики
- [ ] Интеграция с /admin/stats

### Фаза 6: UI/UX (2 часа)
- [ ] Кастомный theme
- [ ] Layout настройка
- [ ] Error handling
- [ ] Notifications
- [ ] Loading states

### Фаза 7: Деплой (2 часа)
- [ ] Production build
- [ ] Деплой на Vercel или VPS
- [ ] Настройка домена
- [ ] SSL сертификат
- [ ] Финальное тестирование

**Итого: 17.5 часов (~2-3 дня работы)**

---

## ✅ Чеклист готовности

### Backend
- [ ] CORS middleware добавлен
- [ ] cors_origins настроен в config
- [ ] .env.example обновлен
- [ ] Admin API работает
- [ ] Swagger docs обновлены

### Frontend
- [ ] Репозиторий создан
- [ ] Vite + React настроен
- [ ] authProvider реализован
- [ ] dataProvider реализован
- [ ] User CRUD работает
- [ ] Order CRUD работает
- [ ] Dashboard показывает статистику
- [ ] Production build успешен

### Деплой
- [ ] Backend задеплоен
- [ ] Frontend задеплоен
- [ ] CORS правильно настроен
- [ ] SSL настроен (если production)
- [ ] Проверена работа на продакшене

### Документация
- [ ] README.md в frontend
- [ ] DEPLOYMENT.md в frontend
- [ ] Обновлен README.md в backend
- [ ] .env.example в обоих проектах

---

## 📊 Сравнение с монорепо

| Критерий | Раздельные проекты ⭐ | Монорепо |
|----------|---------------------|----------|
| Независимость | ✅ Полная | ⚠️  Частичная |
| Деплой | ✅ Независимый | ⚠️  Связанный |
| Версионирование | ✅ Раздельное | ⚠️  Общее |
| CI/CD | ✅ Раздельные пайплайны | ⚠️  Общий пайплайн |
| Размер репо | ✅ Маленькие | ❌ Большой |
| Структура backend | ✅ Без изменений | ❌ Требует реорганизации |
| Команда | ✅ Разные разработчики | ⚠️  Один репо для всех |
| Hosting | ✅ Можно на Vercel | ⚠️  Нужен VPS |

---

## 🔗 Ссылки

- [React Admin Docs](https://marmelab.com/react-admin/)
- [Vite Docs](https://vitejs.dev/)
- [Material-UI Docs](https://mui.com/)
- [Vercel Deployment](https://vercel.com/docs)
- [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/)

---

## 📝 Финальные заметки

### Преимущества раздельных проектов:

1. **Нулевые изменения в структуре backend** - только 10 строк кода (CORS)
2. **Независимость** - можно разрабатывать и деплоить отдельно
3. **Гибкость хостинга** - frontend на Vercel (бесплатно + CDN + SSL)
4. **Чистота** - каждый проект занимается своим делом
5. **Масштабируемость** - легко добавить еще один frontend (мобильное приложение)

### Недостатки:

1. Два репозитория для управления
2. Нужно синхронизировать изменения API

### Рекомендация:

**Используйте раздельные проекты**, если:
- ✅ Вы работаете один или в маленькой команде
- ✅ Хотите минимум изменений в backend
- ✅ Хотите использовать Vercel/Netlify для frontend
- ✅ Планируете независимые релизы

---

**Статус:** Ready for Implementation
**Автор:** Claude Sonnet 4.5
**Дата:** 2026-01-25
